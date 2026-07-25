from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
import shlex
import sys
from types import ModuleType

import pytest


ROOT = Path(__file__).resolve().parents[1]
TESTED_COMMIT = "a" * 40
IMAGE_DIGEST = "sha256:" + "b" * 64
PROJECT = "jobseeker_m05_test"


def load_generator() -> ModuleType:
    scripts = str(ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    path = ROOT / "scripts" / "generate_milestone_05_receipt.py"
    spec = importlib.util.spec_from_file_location("generate_milestone_05_receipt", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GENERATOR = load_generator()


def write_reference(root: Path, relative: str, text: str = "evidence\n") -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def valid_reviews(root: Path) -> tuple[Path, Path]:
    references = ["artifacts/reviews/source.log"]
    write_reference(root, references[0])
    policy = {
        "verdict": "GO",
        "reviewer": "policy-release-reviewer",
        "tested_commit": TESTED_COMMIT,
        "references": references,
        "unresolved_high_critical": [],
    }
    evidence = {
        "result": "PASS",
        "reviewer": "test-evidence-analyst",
        "tested_commit": TESTED_COMMIT,
        "acceptance": {
            acceptance_id: {"result": "PASS", "references": references}
            for acceptance_id in GENERATOR.ACCEPTANCE_IDS
        },
    }
    policy_path = root / "artifacts/reviews/policy.json"
    evidence_path = root / "artifacts/reviews/evidence.json"
    policy_path.parent.mkdir(parents=True, exist_ok=True)
    policy_path.write_text(json.dumps(policy), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
    return policy_path, evidence_path


def gate_log(gate: str) -> str:
    if gate == "03-image-digest":
        return IMAGE_DIGEST + "\n"
    if gate == "05-stack-state":
        return "\n".join(
            f"{PROJECT}-{service}-1 image command {service} Up (healthy)"
            for service in ("api", "worker", "scheduler", "db", "redis")
        )
    if gate == "06-http-contracts":
        return "architecture HTTP/OpenAPI check passed\n"
    if gate in GENERATOR.PYTEST_GATES:
        return "7 passed in 0.10s\n"
    if gate == "10-migration-head":
        return "0001_initial (head)\n"
    if gate == "11-validate-docs":
        return "documentation validation passed\n"
    if gate == "12-validate-milestone":
        return "milestone validation passed\n"
    if gate == "13-validate-codex-controls":
        return "Codex control validation passed\n"
    if gate == "14-ruff":
        return "All checks passed!\n"
    if gate == "15-mypy":
        return "Success: no issues found in 57 source files\n"
    if gate == "17-pre-commit":
        return "pytest........................................Passed\n"
    return "command completed\n"


def valid_manifest(root: Path, *, label: str = "main") -> Path:
    output = root / f"artifacts/verification/{label}"
    logs = output / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    metadata = {
        "schema_version": "1",
        "run_label": label,
        "tested_commit": TESTED_COMMIT,
        "timestamp_utc": "2026-07-25T12:00:00Z",
        "compose_project_name": PROJECT,
        "image_digest": IMAGE_DIGEST,
        "result": "PASS",
    }
    with (output / "metadata.tsv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=("key", "value"), delimiter="\t")
        writer.writeheader()
        writer.writerows({"key": key, "value": value} for key, value in metadata.items())
    fields = (
        "gate_id",
        "command",
        "exit_code",
        "duration_seconds",
        "log_ref",
        "test_count",
        "result",
    )
    manifest = output / "manifest.tsv"
    with manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        for gate in GENERATOR.GATE_IDS:
            log_ref = f"artifacts/verification/{label}/logs/{gate}.log"
            write_reference(root, log_ref, gate_log(gate))
            writer.writerow(
                {
                    "gate_id": gate,
                    "command": shlex.join(GENERATOR.expected_command(gate)),
                    "exit_code": "0",
                    "duration_seconds": "1",
                    "log_ref": log_ref,
                    "test_count": "7" if gate in GENERATOR.PYTEST_GATES else "",
                    "result": "PASS",
                }
            )
    return manifest


def test_m05_acceptance_and_gate_sets_are_stable() -> None:
    assert GENERATOR.ACCEPTANCE_IDS == tuple(
        f"M05-AC{number:02d}" for number in range(1, 11)
    )
    assert GENERATOR.GATE_IDS[:6] == (
        "01-compose-config",
        "02-build-api",
        "03-image-digest",
        "04-start-stack",
        "05-stack-state",
        "06-http-contracts",
    )
    assert GENERATOR.GATE_IDS[-3:] == (
        "16-pytest",
        "17-pre-commit",
        "18-teardown",
    )


def test_m05_expected_commands_bind_public_http_policy_and_full_suite() -> None:
    assert GENERATOR.expected_command("06-http-contracts")[-2:] == [
        "--base-url",
        "http://127.0.0.1:8000",
    ]
    assert GENERATOR.expected_command("08-policy-pytest")[-2:] == [
        "tests/test_policy.py",
        "tests/test_milestone_05_providers.py",
    ]
    assert GENERATOR.expected_command("16-pytest")[-2:] == ["pytest", "-q"]


def test_m05_manifest_requires_exact_commands_runtime_logs_and_test_counts(
    tmp_path: Path,
) -> None:
    manifest = valid_manifest(tmp_path)
    metadata, commands, references = GENERATOR.read_manifest(
        tmp_path, manifest, "main"
    )
    assert metadata["tested_commit"] == TESTED_COMMIT
    assert len(commands) == len(GENERATOR.GATE_IDS)
    assert {item["gate_id"] for item in commands if "test_count" in item} == set(
        GENERATOR.PYTEST_GATES
    )
    assert references


def test_m05_manifest_rejects_zero_test_count(tmp_path: Path) -> None:
    manifest = valid_manifest(tmp_path)
    rows = list(
        csv.DictReader(
            manifest.read_text(encoding="utf-8").splitlines(),
            delimiter="\t",
        )
    )
    rows[6]["test_count"] = "0"
    with manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys(), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(GENERATOR.EvidenceError, match="positive test count"):
        GENERATOR.read_manifest(tmp_path, manifest, "main")


def test_m05_reviews_require_exact_roles_commit_and_acceptance(tmp_path: Path) -> None:
    policy, evidence = valid_reviews(tmp_path)
    review, acceptance, references = GENERATOR.read_reviews(
        tmp_path,
        policy,
        evidence,
        tested_commit=TESTED_COMMIT,
    )
    assert review["verdict"] == "GO"
    assert review["reviewer"] == "policy-release-reviewer"
    assert set(acceptance) == set(GENERATOR.ACCEPTANCE_IDS)
    assert references == ["artifacts/reviews/evidence.json"]


def test_m05_capture_pair_requires_same_commit_not_same_attestation_digest() -> None:
    main = {"tested_commit": TESTED_COMMIT, "image_digest": IMAGE_DIGEST}
    clean = {
        "tested_commit": TESTED_COMMIT,
        "image_digest": "sha256:" + "c" * 64,
    }
    GENERATOR.validate_capture_pair(main, clean)
    clean["tested_commit"] = "d" * 40
    with pytest.raises(GENERATOR.EvidenceError, match="different commits"):
        GENERATOR.validate_capture_pair(main, clean)


@pytest.mark.parametrize(
    "mutation",
    ("no_go", "unresolved", "wrong_policy_role", "wrong_evidence_role", "stale"),
)
def test_m05_reviews_fail_closed(tmp_path: Path, mutation: str) -> None:
    policy_path, evidence_path = valid_reviews(tmp_path)
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if mutation == "no_go":
        policy["verdict"] = "NO-GO"
    elif mutation == "unresolved":
        policy["unresolved_high_critical"] = ["blocker"]
    elif mutation == "wrong_policy_role":
        policy["reviewer"] = "implementation-worker"
    elif mutation == "wrong_evidence_role":
        evidence["reviewer"] = "implementation-worker"
    else:
        evidence["tested_commit"] = "c" * 40
    policy_path.write_text(json.dumps(policy), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
    with pytest.raises(GENERATOR.EvidenceError):
        GENERATOR.read_reviews(
            tmp_path,
            policy_path,
            evidence_path,
            tested_commit=TESTED_COMMIT,
        )


def test_m05_placeholder_scope_is_complete_and_current() -> None:
    assert GENERATOR.placeholder_findings(ROOT) == []
