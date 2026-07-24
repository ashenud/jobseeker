from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType

import pytest


ROOT = Path(__file__).resolve().parents[1]
GATE_WRAPPER = ROOT / "scripts" / "run_milestone_03_gates.sh"


def load_generator() -> ModuleType:
    scripts = str(ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    path = ROOT / "scripts" / "generate_milestone_03_receipt.py"
    spec = importlib.util.spec_from_file_location("generate_milestone_03_receipt", path)
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
        "references": references,
        "unresolved_high_critical": [],
    }
    evidence = {
        "result": "PASS",
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


def test_m03_acceptance_and_gate_sets_are_stable() -> None:
    assert GENERATOR.ACCEPTANCE_IDS == (
        "M03-AC01",
        "M03-AC02",
        "M03-AC03",
        "M03-AC04",
        "M03-AC05",
        "M03-AC06",
    )
    assert GENERATOR.GATE_IDS[3] == "04-profile-validate"
    assert GENERATOR.GATE_IDS[-2:] == ("10-pytest", "11-pre-commit")


def test_m03_reviews_require_exact_pass_and_go(tmp_path: Path) -> None:
    policy, evidence = valid_reviews(tmp_path)
    review, acceptance, references = GENERATOR.read_reviews(tmp_path, policy, evidence)
    assert review["verdict"] == "GO"
    assert set(acceptance) == set(GENERATOR.ACCEPTANCE_IDS)
    assert references == ["artifacts/reviews/evidence.json"]


@pytest.mark.parametrize("mutation", ["no_go", "unresolved", "missing_acceptance"])
def test_m03_reviews_fail_closed(tmp_path: Path, mutation: str) -> None:
    policy_path, evidence_path = valid_reviews(tmp_path)
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if mutation == "no_go":
        policy["verdict"] = "NO-GO"
    elif mutation == "unresolved":
        policy["unresolved_high_critical"] = ["blocker"]
    else:
        evidence["acceptance"].pop("M03-AC06")
    policy_path.write_text(json.dumps(policy), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
    with pytest.raises(GENERATOR.EvidenceError):
        GENERATOR.read_reviews(tmp_path, policy_path, evidence_path)


def test_m03_placeholder_scan_rejects_markers_and_missing_files(tmp_path: Path) -> None:
    for relative in GENERATOR.PLACEHOLDER_SCOPE:
        write_reference(tmp_path, relative)
    target = tmp_path / GENERATOR.PLACEHOLDER_SCOPE[0]
    target.write_text("# FIXME\n", encoding="utf-8")
    assert any("unfinished-marker" in item for item in GENERATOR.placeholder_findings(tmp_path))
    (tmp_path / GENERATOR.PLACEHOLDER_SCOPE[-1]).unlink()
    assert any("missing:" in item for item in GENERATOR.placeholder_findings(tmp_path))


@pytest.mark.parametrize("status", [None, " M dirty.py\n"])
def test_m03_clean_checkout_rejects_missing_or_dirty_status(
    tmp_path: Path, status: str | None
) -> None:
    capture = tmp_path / "artifacts/verification/milestone-03-clean"
    capture.mkdir(parents=True)
    manifest = capture / "manifest.tsv"
    manifest.write_text("manifest\n", encoding="utf-8")
    if status is not None:
        (capture / "checkout-status.log").write_text(status, encoding="utf-8")
    with pytest.raises(GENERATOR.EvidenceError):
        GENERATOR.read_clean_checkout(tmp_path, manifest)


def test_m03_clean_checkout_accepts_empty_machine_status(tmp_path: Path) -> None:
    capture = tmp_path / "artifacts/verification/milestone-03-clean"
    capture.mkdir(parents=True)
    manifest = capture / "manifest.tsv"
    manifest.write_text("manifest\n", encoding="utf-8")
    (capture / "checkout-status.log").write_text("", encoding="utf-8")
    assert GENERATOR.read_clean_checkout(tmp_path, manifest) == (
        "artifacts/verification/milestone-03-clean/checkout-status.log"
    )


def test_m03_authoritative_gate_labels_require_clean_source_before_capture() -> None:
    wrapper = GATE_WRAPPER.read_text(encoding="utf-8")

    assert 'main|clean|preflight)' in wrapper
    assert 'if [[ "$run_label" == "preflight" ]]' in wrapper
    cleanliness_check = wrapper.index("    require_clean_source_tree\n")
    output_capture = wrapper.index('    mkdir -p "$output_dir/logs"\n')
    commit_capture = wrapper.index('    tested_commit="$(git rev-parse HEAD)"\n')
    first_application_gate = wrapper.index("    run_gate 01-compose-config")
    assert cleanliness_check < output_capture
    assert cleanliness_check < commit_capture
    assert cleanliness_check < first_application_gate
