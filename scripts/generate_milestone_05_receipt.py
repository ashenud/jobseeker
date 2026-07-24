#!/usr/bin/env python3
"""Generate Milestone 05 evidence from exact machine captures and reviews."""

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
    "04-start-stack",
    "05-stack-state",
    "06-http-contracts",
    "07-focused-pytest",
    "08-policy-pytest",
    "09-migrate-up",
    "10-migration-head",
    "11-validate-docs",
    "12-validate-milestone",
    "13-validate-codex-controls",
    "14-ruff",
    "15-mypy",
    "16-pytest",
    "17-pre-commit",
    "18-teardown",
)
PYTEST_GATES = {"07-focused-pytest", "08-policy-pytest", "16-pytest"}
ACCEPTANCE_IDS = tuple(f"M05-AC{number:02d}" for number in range(1, 11))
PLACEHOLDER_SCOPE = (
    "docs/ARCHITECTURE.md",
    "docs/STATE_MACHINES.md",
    "docs/adr/0003-modular-monolith.md",
    "docs/adr/0004-server-rendered-dashboard.md",
    "docs/milestones/05-architecture-boundaries-and-state-machines.md",
    "src/job_agent/core/architecture.py",
    "src/job_agent/core/audit.py",
    "src/job_agent/core/commands.py",
    "src/job_agent/core/contracts.py",
    "src/job_agent/core/errors.py",
    "src/job_agent/core/states.py",
    "src/job_agent/core/transitions.py",
    "src/job_agent/providers/contracts.py",
    "src/job_agent/web/app.py",
    "src/job_agent/web/architecture_routes.py",
    "src/job_agent/web/schemas.py",
    "src/job_agent/workers/transitions.py",
    "scripts/check_architecture_http.py",
    "scripts/run_milestone_05_gates.sh",
    "scripts/generate_milestone_05_receipt.py",
    "tests/test_milestone_05_contracts.py",
    "tests/test_milestone_05_evidence.py",
    "tests/test_milestone_05_http.py",
    "tests/test_milestone_05_providers.py",
    "tests/test_milestone_05_states.py",
)


def expected_command(gate: str) -> list[str]:
    compose = ["docker", "compose", "--profile", "dev"]
    commands = {
        "01-compose-config": [*compose, "config", "--quiet"],
        "02-build-api": [*compose, "build", "api"],
        "03-image-digest": [
            "docker",
            "image",
            "inspect",
            "jobseeker-app:local",
            "--format",
            "{{.Id}}",
        ],
        "04-start-stack": [*compose, "up", "-d", "--wait"],
        "05-stack-state": [*compose, "ps"],
        "06-http-contracts": [
            *compose,
            "exec",
            "-T",
            "api",
            "python",
            "scripts/check_architecture_http.py",
            "--base-url",
            "http://127.0.0.1:8000",
        ],
        "07-focused-pytest": [
            *compose,
            "run",
            "--rm",
            "--no-deps",
            "api",
            "pytest",
            "-q",
            "tests/test_milestone_05_states.py",
            "tests/test_milestone_05_contracts.py",
            "tests/test_milestone_05_providers.py",
            "tests/test_milestone_05_http.py",
        ],
        "08-policy-pytest": [
            *compose,
            "run",
            "--rm",
            "--no-deps",
            "api",
            "pytest",
            "-q",
            "tests/test_policy.py",
            "tests/test_milestone_05_providers.py",
        ],
        "09-migrate-up": [
            *compose,
            "run",
            "--rm",
            "api",
            "alembic",
            "upgrade",
            "head",
        ],
        "10-migration-head": [
            *compose,
            "run",
            "--rm",
            "api",
            "alembic",
            "current",
            "--check-heads",
        ],
        "11-validate-docs": [
            *compose,
            "run",
            "--rm",
            "--no-deps",
            "api",
            "python",
            "scripts/validate_docs.py",
        ],
        "12-validate-milestone": [
            *compose,
            "run",
            "--rm",
            "--no-deps",
            "api",
            "python",
            "scripts/validate_milestone.py",
            "--all",
        ],
        "13-validate-codex-controls": [
            *compose,
            "run",
            "--rm",
            "--no-deps",
            "api",
            "python",
            "scripts/validate_codex_controls.py",
        ],
        "14-ruff": [*compose, "run", "--rm", "--no-deps", "api", "ruff", "check", "."],
        "15-mypy": [*compose, "run", "--rm", "--no-deps", "api", "mypy", "src"],
        "16-pytest": [*compose, "run", "--rm", "--no-deps", "api", "pytest", "-q"],
        "17-pre-commit": [
            *compose,
            "run",
            "--rm",
            "--no-deps",
            "api",
            "pre-commit",
            "run",
            "--all-files",
        ],
        "18-teardown": [*compose, "down", "--volumes", "--remove-orphans"],
    }
    return commands[gate]


def validate_runtime_log(gate: str, text: str, project_name: str) -> None:
    if gate == "05-stack-state":
        for service in ("api", "worker", "scheduler", "db", "redis"):
            name = f"{project_name}-{service}-1"
            matching = [line for line in text.splitlines() if name in line]
            if len(matching) != 1 or "(healthy)" not in matching[0]:
                raise EvidenceError(f"stack-state lacks one healthy {service} service")
        if "0.0.0.0:" in text or ":::8000" in text:
            raise EvidenceError("API is not restricted to the loopback bind")
    elif gate == "06-http-contracts":
        if text.strip() != "architecture HTTP/OpenAPI check passed":
            raise EvidenceError("HTTP contract check lacks its exact success result")
    elif gate == "10-migration-head":
        if "0001_initial (head)" not in text:
            raise EvidenceError("migration check did not report the accepted head")
    elif gate == "11-validate-docs" and "documentation validation passed" not in text:
        raise EvidenceError("documentation validator did not report PASS")
    elif gate == "12-validate-milestone" and "milestone validation passed" not in text:
        raise EvidenceError("milestone validator did not report PASS")
    elif gate == "13-validate-codex-controls" and "Codex control validation passed" not in text:
        raise EvidenceError("Codex validator did not report PASS")
    elif gate == "14-ruff" and "All checks passed!" not in text:
        raise EvidenceError("Ruff did not report PASS")
    elif gate == "15-mypy" and "Success: no issues found" not in text:
        raise EvidenceError("mypy did not report PASS")
    elif gate == "17-pre-commit":
        if "Failed" in text or "Passed" not in text:
            raise EvidenceError("pre-commit did not report all hooks passing")


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
        raise EvidenceError(f"{expected_label} manifest lacks the exact M05 gate order")

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
        if captured_command != expected_command(gate):
            raise EvidenceError(f"{expected_label} gate {gate} is not the required command")
        try:
            duration = float(row["duration_seconds"])
        except ValueError as exc:
            raise EvidenceError(f"{expected_label} gate {gate} duration is invalid") from exc
        if duration < 0:
            raise EvidenceError(f"{expected_label} gate {gate} duration is negative")

        log_path, log_ref = repository_file(
            root, row["log_ref"], f"{expected_label} gate {gate} log"
        )
        log_text = log_path.read_text(encoding="utf-8")
        if gate == "03-image-digest":
            lines = log_text.strip().splitlines()
            if not lines or lines[-1] != metadata["image_digest"]:
                raise EvidenceError("image digest metadata does not match its log")
        validate_runtime_log(gate, log_text, metadata["compose_project_name"])

        command: dict[str, Any] = {
            "run": expected_label,
            "gate_id": gate,
            "command": row["command"],
            "exit_code": 0,
            "duration_seconds": duration,
            "log_refs": [log_ref],
        }
        if gate in PYTEST_GATES:
            try:
                test_count = int(row["test_count"])
            except ValueError as exc:
                raise EvidenceError(f"{expected_label} {gate} test count is invalid") from exc
            if test_count <= 0 or f"{test_count} passed" not in log_text:
                raise EvidenceError(f"{expected_label} {gate} lacks a real positive test count")
            command["test_count"] = test_count
        elif row["test_count"]:
            raise EvidenceError(f"{expected_label} non-pytest gate {gate} has a test count")
        commands.append(command)
        references.append(log_ref)
    return metadata, commands, references


def read_reviews(
    root: Path,
    policy_value: str | Path,
    evidence_value: str | Path,
    *,
    tested_commit: str,
) -> tuple[dict[str, Any], dict[str, list[str]], list[str]]:
    policy, policy_ref = read_json_object(root, policy_value, "policy/release review")
    if (
        policy.get("verdict") != "GO"
        or policy.get("reviewer") != "policy-release-reviewer"
        or policy.get("unresolved_high_critical") != []
        or policy.get("tested_commit") != tested_commit
    ):
        raise EvidenceError("policy/release review is not an exact, current, unqualified GO")
    policy_refs = checked_references(root, policy.get("references"), "policy/release review")

    evidence, evidence_ref = read_json_object(root, evidence_value, "evidence analyst review")
    if (
        evidence.get("result") != "PASS"
        or evidence.get("reviewer") != "test-evidence-analyst"
        or evidence.get("tested_commit") != tested_commit
    ):
        raise EvidenceError("evidence analyst review is not an exact current PASS")
    acceptance = evidence.get("acceptance")
    if not isinstance(acceptance, dict) or set(acceptance) != set(ACCEPTANCE_IDS):
        raise EvidenceError("evidence analyst review lacks the exact M05 acceptance set")
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
        "reviewer": "policy-release-reviewer",
        "tested_commit": tested_commit,
        "references": unique([policy_ref, *policy_refs]),
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
                if isinstance(node, ast.Pass):
                    findings.append(f"pass-statement:{relative}:{node.lineno}")
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
    parser.add_argument("--output", default="artifacts/verification/milestone-05.json")
    parser.add_argument(
        "--placeholder-log",
        default="artifacts/verification/milestone-05-placeholder-scan.log",
    )
    args = parser.parse_args()

    try:
        main_metadata, main_commands, _main_refs = read_manifest(
            ROOT, args.main_manifest, "main"
        )
        clean_metadata, clean_commands, clean_refs = read_manifest(
            ROOT, args.clean_manifest, "clean"
        )
        clean_status_ref = read_clean_checkout(ROOT, args.clean_manifest)
        clean_refs = [*clean_refs, clean_status_ref]
        if main_metadata["tested_commit"] != clean_metadata["tested_commit"]:
            raise EvidenceError("main and clean runs tested different commits")
        if main_metadata["image_digest"] != clean_metadata["image_digest"]:
            raise EvidenceError("main and clean builds produced different image digests")
        review, evidence_refs, _evidence_review_refs = read_reviews(
            ROOT,
            args.policy_review,
            args.evidence_review,
            tested_commit=main_metadata["tested_commit"],
        )

        findings = placeholder_findings(ROOT)
        placeholder_path, placeholder_ref = output_file(
            ROOT, args.placeholder_log, "placeholder log"
        )
        placeholder_path.write_text(
            "scope=M05 architecture, contracts, state machines, HTTP, safety, and evidence\n"
            + ("result=PASS\n" if not findings else "result=FAIL\n")
            + "\n".join(findings)
            + ("\n" if findings else ""),
            encoding="utf-8",
        )
        if findings:
            raise EvidenceError("M05 placeholder scan failed: " + ", ".join(findings))

        main_logs = {item["gate_id"]: item["log_refs"][0] for item in main_commands}
        required = {
            "architecture": "docs/ARCHITECTURE.md",
            "states_doc": "docs/STATE_MACHINES.md",
            "adr_modular": "docs/adr/0003-modular-monolith.md",
            "adr_dashboard": "docs/adr/0004-server-rendered-dashboard.md",
            "milestone": "docs/milestones/05-architecture-boundaries-and-state-machines.md",
            "architecture_code": "src/job_agent/core/architecture.py",
            "audit": "src/job_agent/core/audit.py",
            "commands": "src/job_agent/core/commands.py",
            "contracts": "src/job_agent/core/contracts.py",
            "errors": "src/job_agent/core/errors.py",
            "states": "src/job_agent/core/states.py",
            "transitions": "src/job_agent/core/transitions.py",
            "providers": "src/job_agent/providers/contracts.py",
            "web_routes": "src/job_agent/web/architecture_routes.py",
            "web_schemas": "src/job_agent/web/schemas.py",
            "worker": "src/job_agent/workers/transitions.py",
            "http_check": "scripts/check_architecture_http.py",
            "state_tests": "tests/test_milestone_05_states.py",
            "contract_tests": "tests/test_milestone_05_contracts.py",
            "provider_tests": "tests/test_milestone_05_providers.py",
            "http_tests": "tests/test_milestone_05_http.py",
            "evidence_tests": "tests/test_milestone_05_evidence.py",
        }
        for label, reference in required.items():
            repository_file(ROOT, reference, f"M05 {label}")

        focused = main_logs["07-focused-pytest"]
        policy = main_logs["08-policy-pytest"]
        http = main_logs["06-http-contracts"]
        full = main_logs["16-pytest"]
        mapping = {
            "M05-AC01": [
                required["architecture"],
                required["architecture_code"],
                required["http_tests"],
                http,
                focused,
            ],
            "M05-AC02": [
                required["architecture"],
                required["contracts"],
                required["transitions"],
                required["contract_tests"],
                focused,
            ],
            "M05-AC03": [
                required["providers"],
                required["provider_tests"],
                focused,
            ],
            "M05-AC04": [
                required["states_doc"],
                required["states"],
                required["state_tests"],
                focused,
            ],
            "M05-AC05": [
                required["states_doc"],
                required["states"],
                required["state_tests"],
                focused,
            ],
            "M05-AC06": [
                required["states_doc"],
                required["states"],
                required["state_tests"],
                focused,
            ],
            "M05-AC07": [
                required["commands"],
                required["audit"],
                required["errors"],
                required["contracts"],
                required["transitions"],
                required["contract_tests"],
                focused,
            ],
            "M05-AC08": [
                required["architecture"],
                required["providers"],
                required["provider_tests"],
                policy,
            ],
            "M05-AC09": [
                required["transitions"],
                required["worker"],
                required["contract_tests"],
                focused,
            ],
            "M05-AC10": [
                required["adr_modular"],
                required["adr_dashboard"],
                required["milestone"],
                required["web_routes"],
                required["web_schemas"],
                required["http_check"],
                required["http_tests"],
                required["evidence_tests"],
                http,
                main_logs["09-migrate-up"],
                main_logs["10-migration-head"],
                main_logs["11-validate-docs"],
                main_logs["12-validate-milestone"],
                main_logs["13-validate-codex-controls"],
                main_logs["14-ruff"],
                main_logs["15-mypy"],
                full,
                main_logs["17-pre-commit"],
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
            "milestone": "05",
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
                "Milestone 05 defines repository and unit-of-work protocols only; "
                "concrete PostgreSQL persistence remains Milestone 06.",
                "No marketplace submission connector is implemented or authorized; "
                "the MVP remains manual-only and external writes fail closed.",
                "The full deterministic suite excludes two explicitly opt-in "
                "PostgreSQL/Redis integration tests; the running five-service stack, "
                "migration head, and HTTP contracts are verified separately.",
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
