#!/usr/bin/env python3
"""Generate Milestone 04 evidence from exact machine captures and reviews."""

from __future__ import annotations

import argparse
import ast
import csv
import io
import ipaddress
import json
from pathlib import Path
import re
import shlex
import tokenize
from typing import Any

from generate_milestone_00_receipt import (
    COMMIT,
    DIGEST,
    ROOT,
    EvidenceError,
    checked_references,
    output_file,
    read_json_object,
    repository_file,
    unique,
    utc_timestamp,
)


GATE_IDS = (
    "01-compose-config",
    "02-build-api",
    "03-image-digest",
    "04-start-stack",
    "05-stack-state",
    "06-migrate-up",
    "07-pgvector-revision",
    "08-migrate-down",
    "09-migrate-reup",
    "10-migration-head",
    "11-http-ready",
    "12-stop-redis",
    "13-http-redis-down",
    "14-restore-redis",
    "15-stop-db",
    "16-http-db-down",
    "17-restore-stack",
    "18-integration-pytest",
    "19-worker-ping",
    "20-restart-stack",
    "21-restart-health",
    "22-validate-docs",
    "23-validate-milestone",
    "24-validate-codex-controls",
    "25-ruff",
    "26-mypy",
    "27-pytest",
    "28-pre-commit",
    "29-teardown",
)
PYTEST_GATES = {"18-integration-pytest", "27-pytest"}
ACCEPTANCE_IDS = tuple(f"M04-AC{number:02d}" for number in range(1, 11))
PLACEHOLDER_SCOPE = (
    ".dockerignore",
    ".env.example",
    ".gitignore",
    "Dockerfile",
    "Makefile",
    "alembic.ini",
    "alembic/env.py",
    "alembic/versions/0001_initial.py",
    "compose.yaml",
    "docs/OPERATIONS.md",
    "docs/milestones/04-local-environment-and-repository-bootstrap.md",
    "pyproject.toml",
    "scripts/bootstrap.sh",
    "scripts/check.sh",
    "scripts/check_runtime_http.py",
    "scripts/check_worker_ping.py",
    "scripts/dev.sh",
    "scripts/generate_milestone_04_receipt.py",
    "scripts/run_milestone_04_gates.sh",
    "src/job_agent/config/settings.py",
    "src/job_agent/db/__init__.py",
    "src/job_agent/db/base.py",
    "src/job_agent/db/session.py",
    "src/job_agent/web/app.py",
    "src/job_agent/web/health.py",
    "src/job_agent/web/healthcheck.py",
    "src/job_agent/workers/app.py",
    "tests/test_milestone_04_evidence.py",
    "tests/test_runtime_foundation.py",
    "tests/test_runtime_integration.py",
)


def expected_command(gate: str, tested_commit: str) -> list[str]:
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
        "06-migrate-up": [*compose, "run", "--rm", "api", "alembic", "upgrade", "head"],
        "07-pgvector-revision": [
            *compose,
            "exec",
            "-T",
            "db",
            "psql",
            "--username",
            "job_agent",
            "--dbname",
            "job_agent",
            "--tuples-only",
            "--no-align",
            "--set",
            "ON_ERROR_STOP=1",
            "--command",
            "SELECT extname || ':' || (SELECT version_num FROM alembic_version) "
            "FROM pg_extension WHERE extname = 'vector';",
        ],
        "08-migrate-down": [
            *compose,
            "run",
            "--rm",
            "api",
            "alembic",
            "downgrade",
            "base",
        ],
        "09-migrate-reup": [
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
        "11-http-ready": [
            *compose,
            "exec",
            "-T",
            "api",
            "python",
            "scripts/check_runtime_http.py",
            "--expected-commit",
            tested_commit,
            "--expected-readiness",
            "ready",
        ],
        "12-stop-redis": [*compose, "stop", "redis"],
        "13-http-redis-down": [
            *compose,
            "exec",
            "-T",
            "api",
            "python",
            "scripts/check_runtime_http.py",
            "--expected-commit",
            tested_commit,
            "--expected-readiness",
            "redis-down",
        ],
        "14-restore-redis": [*compose, "up", "-d", "--wait", "redis"],
        "15-stop-db": [*compose, "stop", "db"],
        "16-http-db-down": [
            *compose,
            "exec",
            "-T",
            "api",
            "python",
            "scripts/check_runtime_http.py",
            "--expected-commit",
            tested_commit,
            "--expected-readiness",
            "database-down",
        ],
        "17-restore-stack": [*compose, "up", "-d", "--wait"],
        "18-integration-pytest": [
            *compose,
            "run",
            "--rm",
            "-e",
            "JOB_AGENT_RUN_INTEGRATION=true",
            "api",
            "pytest",
            "-q",
            "-m",
            "integration",
        ],
        "19-worker-ping": [
            *compose,
            "exec",
            "-T",
            "api",
            "python",
            "scripts/check_worker_ping.py",
        ],
        "20-restart-stack": [*compose, "restart"],
        "21-restart-health": [*compose, "up", "-d", "--wait"],
        "22-validate-docs": [
            *compose,
            "run",
            "--rm",
            "--no-deps",
            "api",
            "python",
            "scripts/validate_docs.py",
        ],
        "23-validate-milestone": [
            *compose,
            "run",
            "--rm",
            "--no-deps",
            "api",
            "python",
            "scripts/validate_milestone.py",
            "--all",
        ],
        "24-validate-codex-controls": [
            *compose,
            "run",
            "--rm",
            "--no-deps",
            "api",
            "python",
            "scripts/validate_codex_controls.py",
        ],
        "25-ruff": [*compose, "run", "--rm", "--no-deps", "api", "ruff", "check", "."],
        "26-mypy": [*compose, "run", "--rm", "--no-deps", "api", "mypy", "src"],
        "27-pytest": [*compose, "run", "--rm", "--no-deps", "api", "pytest", "-q"],
        "28-pre-commit": [
            *compose,
            "run",
            "--rm",
            "--no-deps",
            "api",
            "pre-commit",
            "run",
            "--all-files",
        ],
        "29-teardown": [*compose, "down", "--volumes", "--remove-orphans"],
    }
    return commands[gate]


def read_metadata(
    root: Path, manifest: Path, expected_label: str
) -> tuple[dict[str, str], str]:
    metadata_path = manifest.with_name("metadata.tsv")
    metadata_path, metadata_ref = repository_file(
        root, metadata_path, f"{expected_label} metadata"
    )
    with metadata_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if not rows or any(set(row) != {"key", "value"} for row in rows):
        raise EvidenceError(f"{expected_label} metadata has an invalid TSV schema")
    metadata: dict[str, str] = {}
    for row in rows:
        if row["key"] in metadata:
            raise EvidenceError(f"{expected_label} metadata repeats key {row['key']}")
        metadata[row["key"]] = row["value"]
    required = {
        "schema_version",
        "run_label",
        "tested_commit",
        "timestamp_utc",
        "compose_project_name",
        "network_subnet",
        "image_digest",
        "result",
    }
    if set(metadata) != required:
        raise EvidenceError(f"{expected_label} metadata keys do not match the M04 schema")
    if metadata["schema_version"] != "1" or metadata["run_label"] != expected_label:
        raise EvidenceError(f"{expected_label} metadata has the wrong schema or label")
    if metadata["result"] != "PASS":
        raise EvidenceError(f"{expected_label} run did not PASS")
    if not COMMIT.fullmatch(metadata["tested_commit"]):
        raise EvidenceError(f"{expected_label} tested commit is invalid")
    if not DIGEST.fullmatch(metadata["image_digest"]):
        raise EvidenceError(f"{expected_label} image digest is invalid")
    utc_timestamp(metadata["timestamp_utc"], f"{expected_label} timestamp")
    try:
        network = ipaddress.ip_network(metadata["network_subnet"], strict=True)
    except ValueError as exc:
        raise EvidenceError(f"{expected_label} network subnet is invalid") from exc
    if network.version != 4 or not network.is_private:
        raise EvidenceError(f"{expected_label} network subnet is not private IPv4")
    project = metadata["compose_project_name"]
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", project):
        raise EvidenceError(f"{expected_label} Compose project name is invalid")
    return metadata, metadata_ref


def _last_json_object(log_text: str, label: str) -> dict[str, Any]:
    lines = [line for line in log_text.splitlines() if line.strip()]
    if not lines:
        raise EvidenceError(f"{label} log is empty")
    try:
        value = json.loads(lines[-1])
    except json.JSONDecodeError as exc:
        raise EvidenceError(f"{label} log lacks final JSON") from exc
    if not isinstance(value, dict):
        raise EvidenceError(f"{label} final JSON is not an object")
    return value


def validate_runtime_log(
    gate: str,
    log_text: str,
    *,
    tested_commit: str,
    project_name: str,
) -> None:
    if gate == "05-stack-state":
        for service in ("api", "worker", "scheduler", "db", "redis"):
            if f"{project_name}-{service}-1" not in log_text:
                raise EvidenceError(f"stack-state log lacks {service}")
        if log_text.count("(healthy)") < 5:
            raise EvidenceError("stack-state log does not show five healthy services")
        if "127.0.0.1:8000->8000/tcp" not in log_text:
            raise EvidenceError("stack-state log lacks the loopback-only API publish")
        if "0.0.0.0:8000->8000/tcp" in log_text:
            raise EvidenceError("stack-state log exposes the API on all interfaces")
        if "5432->5432" in log_text or "6379->6379" in log_text:
            raise EvidenceError("stack-state log exposes PostgreSQL or Redis")
    elif gate == "07-pgvector-revision":
        if "vector:0001_initial" not in log_text.split():
            raise EvidenceError("pgvector/revision gate lacks the expected marker")
    elif gate == "10-migration-head":
        if "0001_initial (head)" not in log_text:
            raise EvidenceError("migration-head gate lacks the expected revision")
    elif gate in {"11-http-ready", "13-http-redis-down", "16-http-db-down"}:
        payload = _last_json_object(log_text, gate)
        expected_readiness = {
            "11-http-ready": {
                "components": {"database": "up", "redis": "up"},
                "status": "ready",
            },
            "13-http-redis-down": {
                "components": {"database": "up", "redis": "down"},
                "status": "not_ready",
            },
            "16-http-db-down": {
                "components": {"database": "down", "redis": "up"},
                "status": "not_ready",
            },
        }[gate]
        if payload.get("commit") != tested_commit:
            raise EvidenceError(f"{gate} did not report the tested commit")
        if payload.get("liveness") != "live":
            raise EvidenceError(f"{gate} did not preserve liveness")
        if payload.get("readiness") != expected_readiness:
            raise EvidenceError(f"{gate} did not report the expected dependency state")
    elif gate == "19-worker-ping":
        payload = _last_json_object(log_text, gate)
        if payload.get("result") != "pong" or payload.get("nodes") != ["worker@worker"]:
            raise EvidenceError("worker-ping gate lacks the required broker reply")


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
        raise EvidenceError(f"{expected_label} manifest lacks the exact M04 gate order")

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
        if captured_command != expected_command(gate, metadata["tested_commit"]):
            raise EvidenceError(f"{expected_label} gate {gate} is not the required M04 command")
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
            lines = [line for line in log_text.splitlines() if line.strip()]
            if not lines or lines[-1] != metadata["image_digest"]:
                raise EvidenceError(f"{expected_label} image digest log does not match metadata")
        validate_runtime_log(
            gate,
            log_text,
            tested_commit=metadata["tested_commit"],
            project_name=metadata["compose_project_name"],
        )
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
                raise EvidenceError(f"{expected_label} gate {gate} test count is invalid") from exc
            if test_count <= 0:
                raise EvidenceError(f"{expected_label} gate {gate} test count is not positive")
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
    if policy.get("verdict") != "GO" or policy.get("unresolved_high_critical") != []:
        raise EvidenceError("policy/release review is not an unqualified GO")
    if policy.get("tested_commit") != tested_commit:
        raise EvidenceError("policy/release review tested a different commit")
    reviewer = policy.get("reviewer")
    if reviewer != "policy-release-reviewer":
        raise EvidenceError("policy/release review has the wrong reviewer")
    policy_refs = checked_references(root, policy.get("references"), "policy/release review")

    evidence, evidence_ref = read_json_object(root, evidence_value, "evidence analyst review")
    if evidence.get("result") != "PASS":
        raise EvidenceError("evidence analyst review did not PASS")
    if evidence.get("tested_commit") != tested_commit:
        raise EvidenceError("evidence analyst review tested a different commit")
    if evidence.get("reviewer") != "test-evidence-analyst":
        raise EvidenceError("evidence analyst review has the wrong reviewer")
    acceptance = evidence.get("acceptance")
    if not isinstance(acceptance, dict) or set(acceptance) != set(ACCEPTANCE_IDS):
        raise EvidenceError("evidence analyst review lacks the exact M04 acceptance set")
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
    parser.add_argument("--output", default="artifacts/verification/milestone-04.json")
    parser.add_argument(
        "--placeholder-log",
        default="artifacts/verification/milestone-04-placeholder-scan.log",
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
            "scope=M04 Docker/runtime foundation, tests, and evidence tooling\n"
            + ("result=PASS\n" if not findings else "result=FAIL\n")
            + "\n".join(findings)
            + ("\n" if findings else ""),
            encoding="utf-8",
        )
        if findings:
            raise EvidenceError("M04 placeholder scan failed: " + ", ".join(findings))

        main_logs = {item["gate_id"]: item["log_refs"][0] for item in main_commands}
        required = {
            "dockerfile": "Dockerfile",
            "compose": "compose.yaml",
            "project": "pyproject.toml",
            "lock": "uv.lock",
            "env": ".env.example",
            "dockerignore": ".dockerignore",
            "gitignore": ".gitignore",
            "makefile": "Makefile",
            "bootstrap": "scripts/bootstrap.sh",
            "check": "scripts/check.sh",
            "dev": "scripts/dev.sh",
            "http_check": "scripts/check_runtime_http.py",
            "worker_check": "scripts/check_worker_ping.py",
            "runner": "scripts/run_milestone_04_gates.sh",
            "generator": "scripts/generate_milestone_04_receipt.py",
            "settings": "src/job_agent/config/settings.py",
            "db_base": "src/job_agent/db/base.py",
            "db_session": "src/job_agent/db/session.py",
            "web": "src/job_agent/web/app.py",
            "health": "src/job_agent/web/health.py",
            "healthcheck": "src/job_agent/web/healthcheck.py",
            "worker": "src/job_agent/workers/app.py",
            "alembic": "alembic/env.py",
            "migration": "alembic/versions/0001_initial.py",
            "foundation_tests": "tests/test_runtime_foundation.py",
            "integration_tests": "tests/test_runtime_integration.py",
            "evidence_tests": "tests/test_milestone_04_evidence.py",
            "milestone": "docs/milestones/04-local-environment-and-repository-bootstrap.md",
        }
        for label, reference in required.items():
            repository_file(ROOT, reference, f"M04 {label}")

        mapping = {
            "M04-AC01": [
                required["dockerfile"],
                required["project"],
                required["lock"],
                main_logs["01-compose-config"],
                main_logs["02-build-api"],
                main_logs["03-image-digest"],
                main_logs["27-pytest"],
            ],
            "M04-AC02": [
                required["compose"],
                required["dockerfile"],
                required["foundation_tests"],
                main_logs["01-compose-config"],
                main_logs["04-start-stack"],
                main_logs["05-stack-state"],
            ],
            "M04-AC03": [
                required["compose"],
                main_logs["04-start-stack"],
                main_logs["05-stack-state"],
                main_logs["20-restart-stack"],
                main_logs["21-restart-health"],
                main_logs["29-teardown"],
            ],
            "M04-AC04": [
                required["web"],
                required["health"],
                required["http_check"],
                required["integration_tests"],
                main_logs["11-http-ready"],
                main_logs["13-http-redis-down"],
                main_logs["16-http-db-down"],
                main_logs["18-integration-pytest"],
            ],
            "M04-AC05": [
                required["db_base"],
                required["db_session"],
                required["alembic"],
                required["migration"],
                required["integration_tests"],
                main_logs["06-migrate-up"],
                main_logs["07-pgvector-revision"],
                main_logs["08-migrate-down"],
                main_logs["09-migrate-reup"],
                main_logs["10-migration-head"],
                main_logs["18-integration-pytest"],
            ],
            "M04-AC06": [
                required["worker"],
                required["worker_check"],
                required["healthcheck"],
                main_logs["04-start-stack"],
                main_logs["19-worker-ping"],
                main_logs["20-restart-stack"],
                main_logs["21-restart-health"],
            ],
            "M04-AC07": [
                required["settings"],
                required["env"],
                required["dockerignore"],
                required["gitignore"],
                required["foundation_tests"],
                main_logs["27-pytest"],
            ],
            "M04-AC08": [
                required["makefile"],
                required["bootstrap"],
                required["check"],
                required["dev"],
                required["foundation_tests"],
                main_logs["24-validate-codex-controls"],
                main_logs["27-pytest"],
            ],
            "M04-AC09": [
                main_logs["06-migrate-up"],
                main_logs["18-integration-pytest"],
                main_logs["22-validate-docs"],
                main_logs["23-validate-milestone"],
                main_logs["24-validate-codex-controls"],
                main_logs["25-ruff"],
                main_logs["26-mypy"],
                main_logs["27-pytest"],
                main_logs["28-pre-commit"],
            ],
            "M04-AC10": [
                required["runner"],
                required["generator"],
                required["evidence_tests"],
                *clean_refs,
                *evidence_review_refs,
                *review["references"],
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
            "milestone": "04",
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
                "Milestone 04 provides only SQLAlchemy/Alembic infrastructure and pgvector "
                "enablement; persistent domain tables and repositories remain Milestone 06.",
                "The Celery application, worker control path, and beat process are operational, "
                "but task routing, schedules, idempotency, and recovery remain Milestone 16.",
                "The deterministic test suite emits one upstream Starlette/httpx TestClient "
                "deprecation warning; the running Uvicorn HTTP gates are unaffected.",
                "The Compose subnet is configurable because host VPN and existing Docker "
                "network allocations vary; operators must choose a non-overlapping private CIDR.",
                "Evaluation and release-check behavior remain later-milestone scaffold and did "
                "not provide Milestone 04 acceptance evidence.",
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
