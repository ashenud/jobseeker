from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType

import pytest


ROOT = Path(__file__).resolve().parents[1]
GATE_WRAPPER = ROOT / "scripts" / "run_milestone_04_gates.sh"
TESTED_COMMIT = "a" * 40
PROJECT = "jobseeker_m04_test"


def load_generator() -> ModuleType:
    scripts = str(ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    path = ROOT / "scripts" / "generate_milestone_04_receipt.py"
    spec = importlib.util.spec_from_file_location("generate_milestone_04_receipt", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GENERATOR = load_generator()


def write_reference(root: Path, relative: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"evidence for {relative}\n", encoding="utf-8")


def valid_reviews(root: Path) -> tuple[Path, Path]:
    references = ["artifacts/reviews/source.log"]
    for reference in references:
        write_reference(root, reference)
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
    policy_path.write_text(json.dumps(policy), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
    return policy_path, evidence_path


def test_m04_acceptance_and_gate_sets_are_stable() -> None:
    assert GENERATOR.ACCEPTANCE_IDS == tuple(
        f"M04-AC{number:02d}" for number in range(1, 11)
    )
    assert GENERATOR.GATE_IDS[:5] == (
        "01-compose-config",
        "02-build-api",
        "03-image-digest",
        "04-start-stack",
        "05-stack-state",
    )
    assert GENERATOR.GATE_IDS[-3:] == ("27-pytest", "28-pre-commit", "29-teardown")
    assert GENERATOR.PYTEST_GATES == {"18-integration-pytest", "27-pytest"}


def test_m04_expected_commands_bind_public_runtime_and_tested_commit() -> None:
    assert GENERATOR.expected_command("04-start-stack", TESTED_COMMIT)[-3:] == [
        "up",
        "-d",
        "--wait",
    ]
    assert GENERATOR.expected_command("11-http-ready", TESTED_COMMIT)[-3:] == [
        TESTED_COMMIT,
        "--expected-readiness",
        "ready",
    ]
    assert GENERATOR.expected_command("29-teardown", TESTED_COMMIT)[-3:] == [
        "down",
        "--volumes",
        "--remove-orphans",
    ]


def test_m04_reviews_require_exact_pass_go_roles_and_commit(tmp_path: Path) -> None:
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


@pytest.mark.parametrize(
    "mutation",
    [
        "no_go",
        "unresolved",
        "wrong_policy_role",
        "wrong_evidence_role",
        "missing_acceptance",
        "stale_policy_commit",
        "stale_evidence_commit",
    ],
)
def test_m04_reviews_fail_closed(tmp_path: Path, mutation: str) -> None:
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
    elif mutation == "missing_acceptance":
        evidence["acceptance"].pop("M04-AC10")
    elif mutation == "stale_policy_commit":
        policy["tested_commit"] = "b" * 40
    else:
        evidence["tested_commit"] = "b" * 40
    policy_path.write_text(json.dumps(policy), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
    with pytest.raises(GENERATOR.EvidenceError):
        GENERATOR.read_reviews(
            tmp_path,
            policy_path,
            evidence_path,
            tested_commit=TESTED_COMMIT,
        )


def test_m04_runtime_logs_require_real_health_revision_http_and_ping() -> None:
    stack = "\n".join(
        [
            "NAME IMAGE COMMAND SERVICE CREATED STATUS PORTS",
            f"{PROJECT}-api-1 app cmd api now Up (healthy) 127.0.0.1:8000->8000/tcp",
            f"{PROJECT}-worker-1 app cmd worker now Up (healthy) 8000/tcp",
            f"{PROJECT}-scheduler-1 app cmd scheduler now Up (healthy) 8000/tcp",
            f"{PROJECT}-db-1 db cmd db now Up (healthy) 5432/tcp",
            f"{PROJECT}-redis-1 redis cmd redis now Up (healthy) 6379/tcp",
        ]
    )
    GENERATOR.validate_runtime_log(
        "05-stack-state",
        stack,
        tested_commit=TESTED_COMMIT,
        project_name=PROJECT,
    )
    GENERATOR.validate_runtime_log(
        "07-pgvector-revision",
        "vector:0001_initial\n",
        tested_commit=TESTED_COMMIT,
        project_name=PROJECT,
    )
    GENERATOR.validate_runtime_log(
        "10-migration-head",
        "0001_initial (head)\n",
        tested_commit=TESTED_COMMIT,
        project_name=PROJECT,
    )
    for gate, readiness in (
        (
            "11-http-ready",
            {"components": {"database": "up", "redis": "up"}, "status": "ready"},
        ),
        (
            "13-http-redis-down",
            {"components": {"database": "up", "redis": "down"}, "status": "not_ready"},
        ),
        (
            "16-http-db-down",
            {"components": {"database": "down", "redis": "up"}, "status": "not_ready"},
        ),
    ):
        GENERATOR.validate_runtime_log(
            gate,
            json.dumps(
                {
                    "commit": TESTED_COMMIT,
                    "liveness": "live",
                    "readiness": readiness,
                    "version": "0.22.0",
                }
            ),
            tested_commit=TESTED_COMMIT,
            project_name=PROJECT,
        )
    GENERATOR.validate_runtime_log(
        "19-worker-ping",
        '{"nodes":["worker@worker"],"result":"pong"}\n',
        tested_commit=TESTED_COMMIT,
        project_name=PROJECT,
    )


@pytest.mark.parametrize(
    ("gate", "log"),
    [
        ("05-stack-state", "no healthy services"),
        ("07-pgvector-revision", "0001_initial"),
        ("10-migration-head", "base"),
        (
            "11-http-ready",
            '{"commit":"stale","liveness":"live","readiness":'
            '{"components":{"database":"up","redis":"up"},"status":"ready"}}',
        ),
        ("19-worker-ping", '{"nodes":[],"result":"pong"}'),
    ],
)
def test_m04_runtime_logs_fail_closed(gate: str, log: str) -> None:
    with pytest.raises(GENERATOR.EvidenceError):
        GENERATOR.validate_runtime_log(
            gate,
            log,
            tested_commit=TESTED_COMMIT,
            project_name=PROJECT,
        )


def test_m04_metadata_requires_private_ipv4_and_exact_schema(tmp_path: Path) -> None:
    capture = tmp_path / "artifacts/verification/capture"
    capture.mkdir(parents=True)
    manifest = capture / "manifest.tsv"
    manifest.write_text("manifest\n", encoding="utf-8")
    metadata = (
        "key\tvalue\n"
        "schema_version\t1\n"
        "run_label\tmain\n"
        f"tested_commit\t{TESTED_COMMIT}\n"
        "timestamp_utc\t2026-07-25T00:00:00Z\n"
        f"compose_project_name\t{PROJECT}\n"
        "network_subnet\t10.254.242.0/24\n"
        f"image_digest\tsha256:{'b' * 64}\n"
        "result\tPASS\n"
    )
    (capture / "metadata.tsv").write_text(metadata, encoding="utf-8")
    parsed, _ = GENERATOR.read_metadata(tmp_path, manifest, "main")
    assert parsed["network_subnet"] == "10.254.242.0/24"
    (capture / "metadata.tsv").write_text(
        metadata.replace("10.254.242.0/24", "8.8.8.0/24"),
        encoding="utf-8",
    )
    with pytest.raises(GENERATOR.EvidenceError):
        GENERATOR.read_metadata(tmp_path, manifest, "main")


def test_m04_placeholder_scan_rejects_markers_and_missing_files(tmp_path: Path) -> None:
    for relative in GENERATOR.PLACEHOLDER_SCOPE:
        write_reference(tmp_path, relative)
    target = tmp_path / GENERATOR.PLACEHOLDER_SCOPE[0]
    target.write_text("# FIXME\n", encoding="utf-8")
    assert any("unfinished-marker" in item for item in GENERATOR.placeholder_findings(tmp_path))
    (tmp_path / GENERATOR.PLACEHOLDER_SCOPE[-1]).unlink()
    assert any("missing:" in item for item in GENERATOR.placeholder_findings(tmp_path))


@pytest.mark.parametrize("status", [None, " M dirty.py\n"])
def test_m04_clean_checkout_rejects_missing_or_dirty_status(
    tmp_path: Path, status: str | None
) -> None:
    capture = tmp_path / "artifacts/verification/milestone-04-clean"
    capture.mkdir(parents=True)
    manifest = capture / "manifest.tsv"
    manifest.write_text("manifest\n", encoding="utf-8")
    if status is not None:
        (capture / "checkout-status.log").write_text(status, encoding="utf-8")
    with pytest.raises(GENERATOR.EvidenceError):
        GENERATOR.read_clean_checkout(tmp_path, manifest)


def test_m04_authoritative_gate_labels_require_clean_source_before_capture() -> None:
    wrapper = GATE_WRAPPER.read_text(encoding="utf-8")
    assert 'main|clean|preflight)' in wrapper
    assert 'if [[ "$run_label" == "preflight" ]]' in wrapper
    cleanliness_check = wrapper.index("    require_clean_source_tree\n")
    output_capture = wrapper.index('    mkdir -p "$output_dir/logs"\n')
    commit_capture = wrapper.index('    tested_commit="$(git rev-parse HEAD)"\n')
    first_gate = wrapper.index("    run_gate 01-compose-config")
    assert cleanliness_check < output_capture
    assert cleanliness_check < commit_capture
    assert cleanliness_check < first_gate
    assert "docker compose --profile dev down --volumes --remove-orphans" in wrapper
