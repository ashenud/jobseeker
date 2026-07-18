#!/usr/bin/env python3
"""Generate Milestone 00 evidence from machine captures and independent reviews."""

from __future__ import annotations

import argparse
import ast
import csv
from datetime import UTC, datetime
import io
import json
from pathlib import Path
import re
import shlex
import tokenize
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GATE_IDS = (
    "01-compose-config",
    "02-build-api",
    "03-image-digest",
    "04-validate-docs",
    "05-validate-milestone",
    "06-validate-codex-controls",
    "07-ruff",
    "08-mypy",
    "09-pytest",
    "10-pre-commit",
)
ACCEPTANCE_IDS = tuple(f"M00-AC{number:02d}" for number in range(1, 11))
COMMIT = re.compile(r"[0-9a-f]{40}")
DIGEST = re.compile(r"sha256:[0-9a-f]{64}")
M00_PLACEHOLDER_SCOPE = (
    "Dockerfile",
    "compose.yaml",
    "pyproject.toml",
    ".pre-commit-config.yaml",
    "Makefile",
    "scripts/bootstrap.sh",
    "scripts/check.sh",
    "scripts/dev.sh",
    "scripts/run_milestone_00_gates.sh",
    "scripts/generate_milestone_00_receipt.py",
    "scripts/validate_docs.py",
    "scripts/validate_milestone.py",
    "scripts/validate_codex_controls.py",
    ".codex/hooks/enforce_docker_boundary.py",
    ".codex/hooks/validate_completion.py",
)
LIMITATION = (
    "Application behavior owned by Milestones 01-22 remains an unverified legacy scaffold and "
    "is explicitly outside the Milestone 00 harness acceptance scope."
)


class EvidenceError(ValueError):
    """Raised when captured evidence cannot support a PASS receipt."""


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
        "04-validate-docs": [
            *compose,
            "run",
            "--rm",
            "--no-deps",
            "api",
            "python",
            "scripts/validate_docs.py",
        ],
        "05-validate-milestone": [
            *compose,
            "run",
            "--rm",
            "--no-deps",
            "api",
            "python",
            "scripts/validate_milestone.py",
            "--all",
        ],
        "06-validate-codex-controls": [
            *compose,
            "run",
            "--rm",
            "--no-deps",
            "api",
            "python",
            "scripts/validate_codex_controls.py",
        ],
        "07-ruff": [*compose, "run", "--rm", "--no-deps", "api", "ruff", "check", "."],
        "08-mypy": [*compose, "run", "--rm", "--no-deps", "api", "mypy", "src"],
        "09-pytest": [*compose, "run", "--rm", "--no-deps", "api", "pytest", "-q"],
        "10-pre-commit": [
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


def repository_file(root: Path, value: str | Path, label: str) -> tuple[Path, str]:
    raw = Path(value)
    if not raw.is_absolute() and ".." in raw.parts:
        raise EvidenceError(f"{label} contains traversal: {value}")
    candidate = raw.resolve() if raw.is_absolute() else (root / raw).resolve()
    try:
        relative = candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise EvidenceError(f"{label} escapes repository: {value}") from exc
    if not candidate.is_file():
        raise EvidenceError(f"{label} is not a regular file: {value}")
    return candidate, relative.as_posix()


def output_file(root: Path, value: str | Path, label: str) -> tuple[Path, str]:
    raw = Path(value)
    if not raw.is_absolute() and ".." in raw.parts:
        raise EvidenceError(f"{label} contains traversal: {value}")
    candidate = raw.resolve() if raw.is_absolute() else (root / raw).resolve()
    try:
        relative = candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise EvidenceError(f"{label} escapes repository: {value}") from exc
    candidate.parent.mkdir(parents=True, exist_ok=True)
    return candidate, relative.as_posix()


def utc_timestamp(value: str, label: str) -> str:
    if not value.endswith("Z"):
        raise EvidenceError(f"{label} is not a Z-suffixed UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    except ValueError as exc:
        raise EvidenceError(f"{label} is not an ISO timestamp") from exc
    if parsed.utcoffset() != UTC.utcoffset(parsed):
        raise EvidenceError(f"{label} is not UTC")
    return value


def read_metadata(root: Path, manifest: Path, expected_label: str) -> tuple[dict[str, str], str]:
    metadata_path = manifest.with_name("metadata.tsv")
    metadata_path, metadata_ref = repository_file(root, metadata_path, f"{expected_label} metadata")
    with metadata_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if not rows or any(set(row) != {"key", "value"} for row in rows):
        raise EvidenceError(f"{expected_label} metadata has an invalid TSV schema")
    metadata: dict[str, str] = {}
    for row in rows:
        key = row["key"]
        if key in metadata:
            raise EvidenceError(f"{expected_label} metadata repeats key {key}")
        metadata[key] = row["value"]
    required = {
        "schema_version",
        "run_label",
        "tested_commit",
        "timestamp_utc",
        "compose_project_name",
        "image_digest",
        "result",
    }
    if set(metadata) != required:
        raise EvidenceError(f"{expected_label} metadata keys do not match the required schema")
    if metadata["schema_version"] != "1" or metadata["run_label"] != expected_label:
        raise EvidenceError(f"{expected_label} metadata has the wrong schema or run label")
    if metadata["result"] != "PASS":
        raise EvidenceError(f"{expected_label} run did not PASS")
    if not COMMIT.fullmatch(metadata["tested_commit"]):
        raise EvidenceError(f"{expected_label} tested commit is invalid")
    if not DIGEST.fullmatch(metadata["image_digest"]):
        raise EvidenceError(f"{expected_label} image digest is invalid")
    utc_timestamp(metadata["timestamp_utc"], f"{expected_label} timestamp")
    return metadata, metadata_ref


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
        raise EvidenceError(f"{expected_label} manifest does not contain the exact M00 gate order")
    commands: list[dict[str, Any]] = []
    references = [manifest_ref, metadata_ref]
    for row in rows:
        gate = row["gate_id"]
        if not row["command"].strip() or row["exit_code"] != "0" or row["result"] != "PASS":
            raise EvidenceError(f"{expected_label} gate {gate} did not record a real PASS")
        try:
            captured_command = shlex.split(row["command"])
        except ValueError as exc:
            raise EvidenceError(f"{expected_label} gate {gate} command is not valid shell text") from exc
        if captured_command != expected_command(gate, metadata["compose_project_name"]):
            raise EvidenceError(f"{expected_label} gate {gate} command is not the required command")
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
                    f"{expected_label} image digest metadata does not match its captured log"
                )
        command: dict[str, Any] = {
            "run": expected_label,
            "gate_id": gate,
            "command": row["command"],
            "exit_code": 0,
            "duration_seconds": duration,
            "log_refs": [log_ref],
        }
        if gate == "09-pytest":
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


def read_json_object(root: Path, value: str | Path, label: str) -> tuple[dict[str, Any], str]:
    path, reference = repository_file(root, value, label)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise EvidenceError(f"{label} is not valid JSON") from exc
    if not isinstance(data, dict):
        raise EvidenceError(f"{label} root is not an object")
    return data, reference


def checked_references(root: Path, value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise EvidenceError(f"{label} has no references")
    references: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise EvidenceError(f"{label} has an invalid reference")
        _, reference = repository_file(root, item, label)
        references.append(reference)
    return references


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
        raise EvidenceError("evidence analyst review lacks the exact M00 acceptance set")
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
    for relative in M00_PLACEHOLDER_SCOPE:
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
                    if isinstance(node.exc.func, ast.Name) and node.exc.func.id == "NotImplementedError":
                        findings.append(f"not-implemented:{relative}:{node.lineno}")
            for token in tokenize.generate_tokens(io.StringIO(text).readline):
                if token.type == tokenize.COMMENT and re.search(r"\b(?:TODO|FIXME)\b", token.string):
                    findings.append(f"unfinished-comment:{relative}:{token.start[0]}")
        else:
            for line_number, line in enumerate(text.splitlines(), start=1):
                if line.lstrip().startswith("#") and re.search(r"\b(?:TODO|FIXME)\b", line):
                    findings.append(f"unfinished-comment:{relative}:{line_number}")
    return findings


def unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--main-manifest", required=True)
    parser.add_argument("--clean-manifest", required=True)
    parser.add_argument("--policy-review", required=True)
    parser.add_argument("--evidence-review", required=True)
    parser.add_argument(
        "--output", default="artifacts/verification/milestone-00.json"
    )
    parser.add_argument(
        "--placeholder-log",
        default="artifacts/verification/milestone-00-placeholder-scan.log",
    )
    args = parser.parse_args()

    try:
        main_metadata, main_commands, main_refs = read_manifest(
            ROOT, args.main_manifest, "main"
        )
        clean_metadata, clean_commands, clean_refs = read_manifest(
            ROOT, args.clean_manifest, "clean"
        )
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
            "scope=M00 harness only; src/job_agent and later-milestone application paths excluded\n"
            + ("result=PASS\n" if not findings else "result=FAIL\n")
            + "\n".join(findings)
            + ("\n" if findings else ""),
            encoding="utf-8",
        )
        if findings:
            raise EvidenceError("M00 harness placeholder scan failed: " + ", ".join(findings))

        main_logs = {item["gate_id"]: item["log_refs"][0] for item in main_commands}
        clean_logs = {item["gate_id"]: item["log_refs"][0] for item in clean_commands}
        mapping = {
            "M00-AC01": [main_logs["04-validate-docs"]],
            "M00-AC02": [main_logs["06-validate-codex-controls"]],
            "M00-AC03": [
                main_logs["01-compose-config"],
                main_logs["02-build-api"],
                clean_logs["01-compose-config"],
                clean_logs["02-build-api"],
            ],
            "M00-AC04": [
                main_logs["02-build-api"],
                main_logs["07-ruff"],
                main_logs["08-mypy"],
                main_logs["09-pytest"],
                main_logs["10-pre-commit"],
            ],
            "M00-AC05": [main_logs["06-validate-codex-controls"]],
            "M00-AC06": [
                main_logs["06-validate-codex-controls"],
                main_logs["09-pytest"],
            ],
            "M00-AC07": [
                main_logs["05-validate-milestone"],
                main_logs["09-pytest"],
            ],
            "M00-AC08": [main_logs["09-pytest"]],
            "M00-AC09": main_refs,
            "M00-AC10": [*clean_refs, *evidence_review_refs, *review["references"]],
        }
        acceptance = {
            acceptance_id: {
                "result": "PASS",
                "references": unique([*mapping[acceptance_id], *evidence_refs[acceptance_id]]),
            }
            for acceptance_id in ACCEPTANCE_IDS
        }
        receipt = {
            "milestone": "00",
            "tested_commit": main_metadata["tested_commit"],
            "timestamp_utc": main_metadata["timestamp_utc"],
            "image_digest": main_metadata["image_digest"],
            "result": "PASS",
            "commands": [*main_commands, *clean_commands],
            "acceptance": acceptance,
            "review": review,
            "clean_checkout": {
                "result": "PASS",
                "references": unique(clean_refs),
            },
            "placeholders": {
                "result": "PASS",
                "matches": [],
                "references": [placeholder_ref],
                "scope": list(M00_PLACEHOLDER_SCOPE),
            },
            "known_limitations": [LIMITATION],
        }
        output, _ = output_file(ROOT, args.output, "receipt output")
        temporary = output.with_suffix(output.suffix + ".tmp")
        temporary.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        temporary.replace(output)
    except (EvidenceError, OSError, tokenize.TokenError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"generated {args.output} from validated machine evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
