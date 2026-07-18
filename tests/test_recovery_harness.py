from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import shlex
import shutil
import subprocess
from types import ModuleType
from typing import Any, Callable

import pytest


ROOT = Path(__file__).resolve().parents[1]


def load_module(relative: str, name: str) -> ModuleType:
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def receipt_root(tmp_path: Path) -> Path:
    (tmp_path / "artifacts" / "verification").mkdir(parents=True)
    (tmp_path / "docs" / "milestones").mkdir(parents=True)
    acceptance = "\n".join(f"- M00-AC{number:02d}" for number in range(1, 11))
    (tmp_path / "docs" / "milestones" / "00-index.md").write_text(
        f"# Milestone 00\n\n{acceptance}\n", encoding="utf-8"
    )
    return tmp_path


def valid_receipt() -> dict[str, Any]:
    return {
        "milestone": "00",
        "tested_commit": "a" * 40,
        "timestamp_utc": "2026-07-19T12:00:00Z",
        "image_digest": "sha256:" + "b" * 64,
        "result": "PASS",
        "commands": [
            {
                "command": "docker compose --profile dev run --rm --no-deps api pytest -q",
                "exit_code": 0,
                "duration_seconds": 1.25,
                "log_refs": ["artifacts/logs/pytest.log"],
                "test_count": 12,
            }
        ],
        "acceptance": {
            f"M00-AC{number:02d}": {
                "result": "PASS",
                "references": [f"artifacts/logs/ac-{number:02d}.log"],
            }
            for number in range(1, 11)
        },
        "review": {
            "verdict": "GO",
            "reviewer": "policy-release-reviewer",
            "references": ["artifacts/reviews/milestone-00.md"],
            "unresolved_high_critical": [],
        },
        "clean_checkout": {
            "result": "PASS",
            "references": ["artifacts/logs/clean-checkout.log"],
        },
        "placeholders": {
            "result": "PASS",
            "matches": [],
            "references": ["artifacts/logs/placeholder-scan.log"],
        },
        "known_limitations": [],
    }


def write_receipt(root: Path, receipt: dict[str, Any]) -> None:
    path = root / "artifacts" / "verification" / "milestone-00.json"
    path.write_text(json.dumps(receipt), encoding="utf-8")


def materialize_references(root: Path, value: Any) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"log_refs", "references"} and isinstance(item, list):
                for reference in item:
                    path = root / reference
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(f"evidence for {reference}\n", encoding="utf-8")
            else:
                materialize_references(root, item)
    elif isinstance(value, list):
        for item in value:
            materialize_references(root, item)


def test_complete_receipt_passes(receipt_root: Path) -> None:
    validator = load_module("scripts/validate_milestone.py", "receipt_validator_valid")
    receipt = valid_receipt()
    materialize_references(receipt_root, receipt)
    write_receipt(receipt_root, receipt)
    assert validator.validate_receipt("00", receipt_root) == []


@pytest.mark.parametrize(
    "mutate, expected",
    [
        (lambda data: data.pop("tested_commit"), "tested commit"),
        (lambda data: data.update(timestamp_utc="2026-07-19T12:00:00"), "UTC timestamp"),
        (lambda data: data.update(image_digest="latest"), "sha256 image digest"),
        (lambda data: data["commands"][0].update(log_refs=[]), "log references"),
        (lambda data: data["commands"][0].update(test_count=0), "nonzero test_count"),
        (lambda data: data["acceptance"].pop("M00-AC10"), "misses acceptance IDs"),
        (lambda data: data["review"].update(verdict="NO-GO"), "independent GO"),
        (lambda data: data["clean_checkout"].update(result="FAIL"), "clean-checkout PASS"),
        (lambda data: data["placeholders"].update(matches=["src/fake.py"]), "placeholders"),
        (lambda data: data.pop("known_limitations"), "known_limitations"),
    ],
)
def test_incomplete_receipt_is_rejected(
    receipt_root: Path,
    mutate: Callable[[dict[str, Any]], Any],
    expected: str,
) -> None:
    validator = load_module("scripts/validate_milestone.py", f"receipt_validator_{expected}")
    receipt = deepcopy(valid_receipt())
    materialize_references(receipt_root, receipt)
    mutate(receipt)
    write_receipt(receipt_root, receipt)
    errors = validator.validate_receipt("00", receipt_root)
    assert errors
    assert any(expected in error for error in errors)


def test_missing_receipt_is_rejected(receipt_root: Path) -> None:
    validator = load_module("scripts/validate_milestone.py", "receipt_validator_missing")
    assert "without artifacts/verification/milestone-00.json" in validator.validate_receipt(
        "00", receipt_root
    )[0]


@pytest.mark.parametrize(
    "reference",
    ["../outside.log", "/tmp/outside.log", "artifacts/logs/missing.log"],
)
def test_receipt_references_must_be_regular_files_inside_repository(
    receipt_root: Path, reference: str
) -> None:
    validator = load_module("scripts/validate_milestone.py", "receipt_validator_reference")
    receipt = valid_receipt()
    materialize_references(receipt_root, receipt)
    receipt["commands"][0]["log_refs"] = [reference]
    write_receipt(receipt_root, receipt)
    errors = validator.validate_receipt("00", receipt_root)
    assert any("unsafe reference" in error or "not a regular file" in error for error in errors)


def test_completion_hook_rejects_done_with_incomplete_receipt(receipt_root: Path) -> None:
    (receipt_root / "scripts").mkdir()
    shutil.copy2(ROOT / "scripts" / "validate_milestone.py", receipt_root / "scripts")
    (receipt_root / "IMPLEMENTATION_STATUS.md").write_text(
        "| ID | Milestone | Status | Assets | Evidence |\n"
        "|---:|---|---|---|---|\n"
        "| 00 | Harness | DONE | implemented | missing |\n",
        encoding="utf-8",
    )
    write_receipt(receipt_root, {"milestone": "00", "result": "PASS"})
    completion = load_module(".codex/hooks/validate_completion.py", "completion_hook")
    errors = completion.incomplete_done(receipt_root)
    assert errors
    assert any("tested commit" in error for error in errors)


@pytest.mark.parametrize("payload_location", ["nested/path", "../outside"])
def test_completion_hook_cwd_cannot_bypass_done_evidence(
    receipt_root: Path, payload_location: str
) -> None:
    (receipt_root / "scripts").mkdir()
    shutil.copy2(ROOT / "scripts" / "validate_milestone.py", receipt_root / "scripts")
    (receipt_root / ".codex" / "hooks").mkdir(parents=True)
    hook_path = receipt_root / ".codex" / "hooks" / "validate_completion.py"
    hook_path.write_text("# hook location marker\n", encoding="utf-8")
    (receipt_root / "IMPLEMENTATION_STATUS.md").write_text(
        "| ID | Milestone | Status | Assets | Evidence |\n"
        "|---:|---|---|---|---|\n"
        "| 00 | Harness | DONE | implemented | missing |\n",
        encoding="utf-8",
    )
    payload_cwd = (receipt_root / payload_location).resolve()
    payload_cwd.mkdir(parents=True, exist_ok=True)
    completion = load_module(".codex/hooks/validate_completion.py", "completion_hook_root")
    resolved = completion.repository_root(payload_cwd, hook_path)
    assert resolved == receipt_root
    assert completion.incomplete_done(resolved)


@pytest.mark.parametrize(
    "command, denied",
    [
        ("pytest -q", "pytest"),
        ("env TESTING=1 python -m pytest", "python"),
        ("command ruff check .", "ruff"),
        ("bash -c 'mypy src'", "mypy"),
        ("echo $(python scripts/validate_docs.py)", "python"),
        ("find . -exec python -m pytest {} ;", "python"),
        ("printf '%s\\n' src | xargs mypy", "mypy"),
        ("docker run --rm tooling pytest", "docker run"),
        ("docker --context remote run --rm tooling pytest", "docker run"),
        ("docker --host unix:///tmp/docker.sock exec api pytest", "docker exec"),
        ("docker --context remote build .", "docker build"),
        ("docker container run --rm tooling pytest", "docker container run"),
        ("docker container exec api pytest", "docker container exec"),
        ("docker buildx build .", "docker buildx build"),
        ("./scripts/custom-check.sh", "scripts/custom-check.sh"),
        ("make db-reset", "make"),
        ("make host-check", "make"),
    ],
)
def test_host_toolchain_and_wrapper_bypasses_are_denied(command: str, denied: str) -> None:
    boundary = load_module(".codex/hooks/enforce_docker_boundary.py", "docker_boundary_denied")
    assert boundary.blocked_segment(command) == denied


@pytest.mark.parametrize(
    "command",
    [
        "docker compose --profile dev run --rm --no-deps api pytest -q",
        "docker compose --profile dev build api",
        "docker --context local compose --profile dev build api",
        "git diff --check",
        "rg 'pytest' docs",
        "echo 'python and pytest are harmless text here'",
        "bash scripts/check.sh",
        "make type",
    ],
)
def test_compose_git_files_and_approved_wrappers_are_allowed(command: str) -> None:
    boundary = load_module(".codex/hooks/enforce_docker_boundary.py", "docker_boundary_allowed")
    assert boundary.blocked_segment(command) is None


def test_destructive_make_target_cannot_reenter_approved_wrappers() -> None:
    boundary = load_module(".codex/hooks/enforce_docker_boundary.py", "docker_boundary_make")
    assert "db-reset" not in boundary.APPROVED_MAKE_TARGETS
    assert boundary.blocked_segment("make db-reset") == "make"
    for target in ("lint", "type", "test"):
        assert boundary.blocked_segment(f"make {target}") is None


def write_gate_capture(root: Path, test_count: int = 12) -> Path:
    capture = root / "artifacts" / "verification" / "capture"
    logs = capture / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    metadata = (
        "key\tvalue\n"
        "schema_version\t1\n"
        "run_label\tmain\n"
        f"tested_commit\t{'a' * 40}\n"
        "timestamp_utc\t2026-07-19T12:00:00Z\n"
        "compose_project_name\ttest_m00\n"
        f"image_digest\tsha256:{'b' * 64}\n"
        "result\tPASS\n"
    )
    (capture / "metadata.tsv").write_text(metadata, encoding="utf-8")
    rows = [
        "gate_id\tcommand\texit_code\tduration_seconds\tlog_ref\ttest_count\tresult"
    ]
    gate_ids = (
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
    compose = ["docker", "compose", "--profile", "dev"]
    commands = {
        "01-compose-config": [*compose, "config", "--quiet"],
        "02-build-api": [*compose, "build", "api"],
        "03-image-digest": [
            "docker",
            "image",
            "inspect",
            "test_m00-api",
            "--format",
            "{{.Id}}",
        ],
        "04-validate-docs": [
            *compose, "run", "--rm", "--no-deps", "api", "python", "scripts/validate_docs.py"
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
    for gate_id in gate_ids:
        log = logs / f"{gate_id}.log"
        content = "sha256:" + "b" * 64 if gate_id == "03-image-digest" else "gate passed"
        log.write_text(content + "\n", encoding="utf-8")
        count = str(test_count) if gate_id == "09-pytest" else ""
        rows.append(
            f"{gate_id}\t{shlex.join(commands[gate_id])}\t0\t1\t"
            f"{log.relative_to(root)}\t{count}\tPASS"
        )
    manifest = capture / "manifest.tsv"
    manifest.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return manifest


def test_receipt_generator_rejects_zero_test_capture(tmp_path: Path) -> None:
    generator = load_module(
        "scripts/generate_milestone_00_receipt.py", "milestone_receipt_generator_zero"
    )
    manifest = write_gate_capture(tmp_path, test_count=0)
    with pytest.raises(generator.EvidenceError, match="pytest count is not positive"):
        generator.read_manifest(tmp_path, manifest, "main")


def test_receipt_generator_rejects_missing_log_reference(tmp_path: Path) -> None:
    generator = load_module(
        "scripts/generate_milestone_00_receipt.py", "milestone_receipt_generator_missing"
    )
    manifest = write_gate_capture(tmp_path)
    missing = tmp_path / "artifacts" / "verification" / "capture" / "logs" / "07-ruff.log"
    missing.unlink()
    with pytest.raises(generator.EvidenceError, match="not a regular file"):
        generator.read_manifest(tmp_path, manifest, "main")


def test_gate_runner_separates_physical_output_from_log_references(tmp_path: Path) -> None:
    runner = ROOT / "scripts" / "run_milestone_00_gates.sh"
    clean_checkout = tmp_path / "clean-checkout"
    physical_log = (
        tmp_path
        / "main-repository"
        / "artifacts"
        / "verification"
        / "milestone-00-clean"
        / "logs"
        / "09-pytest.log"
    )
    logical = "artifacts/verification/milestone-00-clean"
    shell = """
source "$1"
repo_root="$2"
reference_dir="$3"
reference_dir_set=true
validate_reference_dir "$reference_dir"
reference_for "$4" "09-pytest"
"""
    result = subprocess.run(
        [
            "bash",
            "-c",
            shell,
            "runner-reference-test",
            str(runner),
            str(clean_checkout),
            logical,
            str(physical_log),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout == f"{logical}/logs/09-pytest.log"


@pytest.mark.parametrize(
    "logical",
    ["", "/absolute/reference", "../escape", "artifacts/../escape"],
)
def test_gate_runner_rejects_unsafe_log_reference_directories(
    tmp_path: Path, logical: str
) -> None:
    runner = ROOT / "scripts" / "run_milestone_00_gates.sh"
    result = subprocess.run(
        ["bash", str(runner), "--reference-dir", logical],
        check=False,
        capture_output=True,
        cwd=tmp_path,
        text=True,
    )
    assert result.returncode == 2


@pytest.mark.parametrize(
    "option",
    ["--output-dir", "--reference-dir", "--project-name", "--run-label"],
)
def test_gate_runner_rejects_missing_option_values_before_git(
    tmp_path: Path, option: str
) -> None:
    runner = ROOT / "scripts" / "run_milestone_00_gates.sh"
    result = subprocess.run(
        ["bash", str(runner), option],
        check=False,
        capture_output=True,
        cwd=tmp_path,
        text=True,
    )
    assert result.returncode == 2


def test_gate_runner_default_reference_behavior_is_preserved(tmp_path: Path) -> None:
    runner = ROOT / "scripts" / "run_milestone_00_gates.sh"
    physical_log = tmp_path / "artifacts" / "verification" / "main" / "logs" / "07-ruff.log"
    shell = """
source "$1"
repo_root="$2"
reference_dir=""
reference_dir_set=false
reference_for "$3" "07-ruff"
"""
    result = subprocess.run(
        [
            "bash",
            "-c",
            shell,
            "runner-reference-test",
            str(runner),
            str(tmp_path),
            str(physical_log),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout == "artifacts/verification/main/logs/07-ruff.log"


def test_codex_controls_are_structurally_valid() -> None:
    controls = load_module("scripts/validate_codex_controls.py", "codex_controls")
    validations = (
        controls.validate_skill,
        controls.validate_agents,
        controls.validate_config_and_rules,
        controls.validate_hooks,
        controls.validate_wrappers,
        controls.validate_tooling_configuration,
        controls.validate_evidence_automation,
        controls.validate_boundary_cases,
    )
    assert {validation.__name__: validation() for validation in validations} == {
        validation.__name__: [] for validation in validations
    }
