#!/usr/bin/env python3
"""Generate Milestone 03 evidence from machine captures and independent reviews."""

from __future__ import annotations

import argparse
import ast
import csv
import io
import json
from pathlib import Path
import re
import shlex
import tokenize
from typing import Any

from generate_milestone_00_receipt import (
    ROOT,
    EvidenceError,
    checked_references,
    output_file,
    read_json_object,
    read_metadata,
    repository_file,
    unique,
)


GATE_IDS = (
    "01-compose-config",
    "02-build-api",
    "03-image-digest",
    "04-profile-validate",
    "05-validate-docs",
    "06-validate-milestone",
    "07-validate-codex-controls",
    "08-ruff",
    "09-mypy",
    "10-pytest",
    "11-pre-commit",
)
ACCEPTANCE_IDS = tuple(f"M03-AC{number:02d}" for number in range(1, 7))
PLACEHOLDER_SCOPE = (
    ".gitignore",
    "config/profile.yaml",
    "config/profile.example.yaml",
    "config/scoring.yaml",
    "config/scoring.example.yaml",
    "data/private/portfolio_manifest.yaml",
    "data/private/proposal_style_anchors/README.md",
    "docs/SUCCESS_METRICS.md",
    "docs/milestones/03-positioning-profile-and-success-metrics.md",
    "src/job_agent/profile/__init__.py",
    "src/job_agent/profile/exceptions.py",
    "src/job_agent/profile/models.py",
    "src/job_agent/profile/service.py",
    "src/job_agent/cli.py",
    "tests/test_profile.py",
    "tests/test_cli.py",
    "scripts/run_milestone_03_gates.sh",
    "scripts/generate_milestone_03_receipt.py",
    "tests/test_milestone_03_evidence.py",
)


def expected_command(gate: str, project_name: str) -> list[str]:
    compose = ["docker", "compose", "--profile", "dev"]
    commands = {
        "01-compose-config": [*compose, "config", "--quiet"],
        "02-build-api": [*compose, "build", "api"],
        "03-image-digest": [
            "docker",
            "image",
            "inspect",
            f"{project_name}-api",
            "--format",
            "{{.Id}}",
        ],
        "04-profile-validate": [
            *compose,
            "run",
            "--rm",
            "--no-deps",
            "api",
            "job-agent",
            "profile-validate",
        ],
        "05-validate-docs": [
            *compose,
            "run",
            "--rm",
            "--no-deps",
            "api",
            "python",
            "scripts/validate_docs.py",
        ],
        "06-validate-milestone": [
            *compose,
            "run",
            "--rm",
            "--no-deps",
            "api",
            "python",
            "scripts/validate_milestone.py",
            "--all",
        ],
        "07-validate-codex-controls": [
            *compose,
            "run",
            "--rm",
            "--no-deps",
            "api",
            "python",
            "scripts/validate_codex_controls.py",
        ],
        "08-ruff": [*compose, "run", "--rm", "--no-deps", "api", "ruff", "check", "."],
        "09-mypy": [*compose, "run", "--rm", "--no-deps", "api", "mypy", "src"],
        "10-pytest": [*compose, "run", "--rm", "--no-deps", "api", "pytest", "-q"],
        "11-pre-commit": [
            *compose,
            "run",
            "--rm",
            "--no-deps",
            "api",
            "sh",
            "-c",
            "git config --global --add safe.directory /app && pre-commit run --all-files",
        ],
    }
    return commands[gate]


def read_manifest(
    root: Path, value: str | Path, expected_label: str
) -> tuple[dict[str, str], list[dict[str, Any]], list[str]]:
    manifest, manifest_ref = repository_file(root, value, f"{expected_label} manifest")
    metadata, metadata_ref = read_metadata(root, manifest, expected_label)
    with manifest.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    required_columns = {
        "gate_id",
        "command",
        "exit_code",
        "duration_seconds",
        "log_ref",
        "test_count",
        "result",
    }
    if not rows or any(set(row) != required_columns for row in rows):
        raise EvidenceError(f"{expected_label} manifest has an invalid TSV schema")
    if tuple(row["gate_id"] for row in rows) != GATE_IDS:
        raise EvidenceError(f"{expected_label} manifest does not contain the exact M03 gate order")

    commands: list[dict[str, Any]] = []
    references = [manifest_ref, metadata_ref]
    for row in rows:
        gate = row["gate_id"]
        if not row["command"].strip() or row["exit_code"] != "0" or row["result"] != "PASS":
            raise EvidenceError(f"{expected_label} gate {gate} did not record a real PASS")
        try:
            captured_command = shlex.split(row["command"])
        except ValueError as exc:
            raise EvidenceError(f"{expected_label} gate {gate} command is invalid") from exc
        if captured_command != expected_command(gate, metadata["compose_project_name"]):
            raise EvidenceError(f"{expected_label} gate {gate} command is not required M03 command")
        try:
            duration = float(row["duration_seconds"])
        except ValueError as exc:
            raise EvidenceError(f"{expected_label} gate {gate} duration is invalid") from exc
        if duration < 0:
            raise EvidenceError(f"{expected_label} gate {gate} duration is negative")
        log_path, log_ref = repository_file(
            root, row["log_ref"], f"{expected_label} gate {gate} log"
        )
        if gate == "03-image-digest":
            captured_digest = log_path.read_text(encoding="utf-8").strip().splitlines()
            if not captured_digest or captured_digest[-1] != metadata["image_digest"]:
                raise EvidenceError(
                    f"{expected_label} image digest metadata does not match its log"
                )
        command: dict[str, Any] = {
            "run": expected_label,
            "gate_id": gate,
            "command": row["command"],
            "exit_code": 0,
            "duration_seconds": duration,
            "log_refs": [log_ref],
        }
        if gate == "10-pytest":
            try:
                test_count = int(row["test_count"])
            except ValueError as exc:
                raise EvidenceError(f"{expected_label} pytest count is invalid") from exc
            if test_count <= 0:
                raise EvidenceError(f"{expected_label} pytest count is not positive")
            command["test_count"] = test_count
        elif row["test_count"]:
            raise EvidenceError(f"{expected_label} non-pytest gate {gate} has a test count")
        commands.append(command)
        references.append(log_ref)
    return metadata, commands, references


def read_reviews(
    root: Path, policy_value: str | Path, evidence_value: str | Path
) -> tuple[dict[str, Any], dict[str, list[str]], list[str]]:
    policy, policy_ref = read_json_object(root, policy_value, "policy/release review")
    if policy.get("verdict") != "GO" or policy.get("unresolved_high_critical") != []:
        raise EvidenceError("policy/release review is not an unqualified GO")
    reviewer = policy.get("reviewer")
    if not isinstance(reviewer, str) or not reviewer.strip():
        raise EvidenceError("policy/release review has no reviewer")
    policy_refs = checked_references(root, policy.get("references"), "policy/release review")

    evidence, evidence_ref = read_json_object(root, evidence_value, "evidence analyst review")
    if evidence.get("result") != "PASS":
        raise EvidenceError("evidence analyst review did not PASS")
    acceptance = evidence.get("acceptance")
    if not isinstance(acceptance, dict) or set(acceptance) != set(ACCEPTANCE_IDS):
        raise EvidenceError("evidence analyst review lacks the exact M03 acceptance set")
    evidence_refs: dict[str, list[str]] = {}
    for acceptance_id in ACCEPTANCE_IDS:
        item = acceptance[acceptance_id]
        if not isinstance(item, dict) or item.get("result") != "PASS":
            raise EvidenceError(f"evidence analyst did not PASS {acceptance_id}")
        evidence_refs[acceptance_id] = checked_references(
            root, item.get("references"), f"evidence analyst {acceptance_id}"
        )
    review = {
        "verdict": "GO",
        "reviewer": reviewer,
        "references": sorted(set([policy_ref, *policy_refs])),
        "unresolved_high_critical": [],
    }
    return review, evidence_refs, [evidence_ref]


def placeholder_findings(root: Path) -> list[str]:
    findings: list[str] = []
    marker = re.compile(r"\b(?:TODO|FIXME|TBD)\b", re.IGNORECASE)
    for relative in PLACEHOLDER_SCOPE:
        path = root / relative
        if not path.is_file():
            findings.append(f"missing:{relative}")
            continue
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".py":
            try:
                tree = ast.parse(text, filename=relative)
            except SyntaxError as exc:
                findings.append(f"syntax:{relative}:{exc.lineno}")
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call):
                    function = node.exc.func
                    if isinstance(function, ast.Name) and function.id == "NotImplementedError":
                        findings.append(f"not-implemented:{relative}:{node.lineno}")
            for token in tokenize.generate_tokens(io.StringIO(text).readline):
                if token.type == tokenize.COMMENT and marker.search(token.string):
                    findings.append(f"unfinished-comment:{relative}:{token.start[0]}")
        else:
            for line_number, line in enumerate(text.splitlines(), start=1):
                if marker.search(line):
                    findings.append(f"unfinished-marker:{relative}:{line_number}")
    return findings


def read_clean_checkout(root: Path, manifest_value: str | Path) -> str:
    manifest, _ = repository_file(root, manifest_value, "clean manifest")
    status_path = manifest.with_name("checkout-status.log")
    status_path, status_ref = repository_file(root, status_path, "clean checkout status")
    if status_path.read_text(encoding="utf-8") != "":
        raise EvidenceError("clean checkout status is not empty")
    return status_ref


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--main-manifest", required=True)
    parser.add_argument("--clean-manifest", required=True)
    parser.add_argument("--policy-review", required=True)
    parser.add_argument("--evidence-review", required=True)
    parser.add_argument("--output", default="artifacts/verification/milestone-03.json")
    parser.add_argument(
        "--placeholder-log",
        default="artifacts/verification/milestone-03-placeholder-scan.log",
    )
    args = parser.parse_args()

    try:
        main_metadata, main_commands, main_refs = read_manifest(
            ROOT, args.main_manifest, "main"
        )
        clean_metadata, clean_commands, clean_refs = read_manifest(
            ROOT, args.clean_manifest, "clean"
        )
        clean_status_ref = read_clean_checkout(ROOT, args.clean_manifest)
        clean_refs = [*clean_refs, clean_status_ref]
        if main_metadata["tested_commit"] != clean_metadata["tested_commit"]:
            raise EvidenceError("main and clean runs tested different commits")
        review, evidence_refs, evidence_review_refs = read_reviews(
            ROOT, args.policy_review, args.evidence_review
        )

        findings = placeholder_findings(ROOT)
        placeholder_path, placeholder_ref = output_file(
            ROOT, args.placeholder_log, "placeholder log"
        )
        placeholder_path.write_text(
            "scope=M03 profile, scoring, portfolio metadata, KPIs, CLI, tests, and evidence tooling\n"
            + ("result=PASS\n" if not findings else "result=FAIL\n")
            + "\n".join(findings)
            + ("\n" if findings else ""),
            encoding="utf-8",
        )
        if findings:
            raise EvidenceError("M03 placeholder scan failed: " + ", ".join(findings))

        main_logs = {item["gate_id"]: item["log_refs"][0] for item in main_commands}
        required = {
            "profile": "config/profile.yaml",
            "profile_example": "config/profile.example.yaml",
            "scoring": "config/scoring.yaml",
            "scoring_example": "config/scoring.example.yaml",
            "manifest": "data/private/portfolio_manifest.yaml",
            "anchors": "data/private/proposal_style_anchors/README.md",
            "metrics": "docs/SUCCESS_METRICS.md",
            "milestone": "docs/milestones/03-positioning-profile-and-success-metrics.md",
            "models": "src/job_agent/profile/models.py",
            "service": "src/job_agent/profile/service.py",
            "cli": "src/job_agent/cli.py",
            "tests": "tests/test_profile.py",
            "cli_tests": "tests/test_cli.py",
            "gitignore": ".gitignore",
        }
        for label, reference in required.items():
            repository_file(ROOT, reference, f"M03 {label}")

        mapping = {
            "M03-AC01": [
                required["profile"],
                required["scoring"],
                required["manifest"],
                required["models"],
                required["service"],
                required["cli"],
                main_logs["04-profile-validate"],
                main_logs["10-pytest"],
            ],
            "M03-AC02": [
                required["profile"],
                required["manifest"],
                required["models"],
                required["tests"],
                main_logs["10-pytest"],
            ],
            "M03-AC03": [
                required["manifest"],
                required["models"],
                required["tests"],
                main_logs["10-pytest"],
            ],
            "M03-AC04": [
                required["profile"],
                required["scoring"],
                required["profile_example"],
                required["scoring_example"],
                required["tests"],
                main_logs["10-pytest"],
            ],
            "M03-AC05": [
                required["metrics"],
                required["models"],
                required["tests"],
                main_logs["10-pytest"],
            ],
            "M03-AC06": [
                required["gitignore"],
                required["manifest"],
                required["anchors"],
                required["tests"],
                main_logs["10-pytest"],
                *clean_refs,
            ],
        }
        acceptance = {
            acceptance_id: {
                "result": "PASS",
                "references": unique(
                    [*mapping[acceptance_id], *evidence_refs[acceptance_id]]
                ),
            }
            for acceptance_id in ACCEPTANCE_IDS
        }
        receipt = {
            "milestone": "03",
            "tested_commit": main_metadata["tested_commit"],
            "timestamp_utc": main_metadata["timestamp_utc"],
            "image_digest": main_metadata["image_digest"],
            "result": "PASS",
            "commands": [*main_commands, *clean_commands],
            "acceptance": acceptance,
            "review": review,
            "clean_checkout": {"result": "PASS", "references": unique(clean_refs)},
            "placeholders": {
                "result": "PASS",
                "matches": [],
                "references": [placeholder_ref],
                "scope": list(PLACEHOLDER_SCOPE),
            },
            "known_limitations": [
                "Only HERBACORIUM is currently verified for completed-client-work "
                "proposal claims; other service claims require owner-approved evidence.",
                "PDF and bounded public-link content ingestion are deferred to Milestone 11; "
                "M03 stores scrubbed provenance metadata only.",
            ],
        }
        output, _ = output_file(ROOT, args.output, "receipt output")
        temporary = output.with_suffix(output.suffix + ".tmp")
        temporary.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        temporary.replace(output)
    except (EvidenceError, KeyError, OSError, tokenize.TokenError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"generated {args.output} from validated machine evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
