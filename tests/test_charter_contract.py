from __future__ import annotations

import importlib.util
from pathlib import Path
import re
import shutil
from types import ModuleType

import pytest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_FILES = (
    "IMPLEMENTATION_STATUS.md",
    "README.md",
    "docs/PROJECT_CHARTER.md",
    "docs/adr/0001-human-in-the-loop-boundary.md",
    "docs/adr/0002-local-first-mvp.md",
    "docs/milestones/01-project-charter-and-scope.md",
    "docs/prompts/01-project-charter-and-scope.md",
)


def _load_validator() -> ModuleType:
    path = ROOT / "scripts" / "validate_docs.py"
    spec = importlib.util.spec_from_file_location("validate_docs_m01", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = _load_validator()


@pytest.fixture
def contract_root(tmp_path: Path) -> Path:
    for relative in CONTRACT_FILES:
        source = ROOT / relative
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return tmp_path


def _replace_once(root: Path, relative: str, old: str, new: str) -> None:
    path = root / relative
    content = path.read_text(encoding="utf-8")
    assert content.count(old) == 1
    path.write_text(content.replace(old, new, 1), encoding="utf-8")


def _replace_all(root: Path, relative: str, old: str, new: str) -> None:
    path = root / relative
    content = path.read_text(encoding="utf-8")
    assert old in content
    path.write_text(content.replace(old, new), encoding="utf-8")


def _assert_error(root: Path, expected: str) -> None:
    errors = VALIDATOR.validate_m01_semantics(root)
    assert any(expected in error for error in errors), errors


def test_repository_m01_charter_contract_is_valid() -> None:
    assert VALIDATOR.validate_m01_semantics(ROOT) == []


def test_rejects_approval_that_can_transmit(contract_root: Path) -> None:
    _replace_once(
        contract_root,
        "docs/PROJECT_CHARTER.md",
        "Approval never transmits",
        "Approval may transmit",
    )
    _assert_error(contract_root, "approval never transmits")


def test_rejects_named_integration_as_permission(contract_root: Path) -> None:
    _replace_once(
        contract_root,
        "docs/PROJECT_CHARTER.md",
        "Naming a provider or source grants no permission",
        "Naming a provider or source grants permission",
    )
    _assert_error(contract_root, "naming a provider or source grants no permission")


@pytest.mark.parametrize(
    ("name", "replacement"),
    (
        ("manual capture", "manual entry"),
        ("Jobicy RSS/API", "Jobicy"),
        ("Remote OK JSON/RSS", "Remote OK"),
        ("OpenAI Responses API structured output", "OpenAI output"),
    ),
)
def test_rejects_weakened_conditional_goal_names(
    contract_root: Path,
    name: str,
    replacement: str,
) -> None:
    _replace_all(contract_root, "docs/PROJECT_CHARTER.md", name, replacement)
    _assert_error(contract_root, name.casefold())


def test_rejects_host_native_application_tooling(contract_root: Path) -> None:
    _replace_once(
        contract_root,
        "docs/adr/0002-local-first-mvp.md",
        "All application builds, dependency resolution, Python commands",
        "Most application builds, dependency resolution, Python commands",
    )
    _assert_error(contract_root, "all application builds, dependency resolution, python commands")


def test_rejects_wrong_prompt_dependency(contract_root: Path) -> None:
    _replace_once(
        contract_root,
        "docs/prompts/01-project-charter-and-scope.md",
        "Dependencies recorded in the master index: **00**.",
        "Dependencies recorded in the master index: **None**.",
    )
    _assert_error(contract_root, "Prompt 01 dependency must be milestone 00")


def test_rejects_missing_demo_contract_context(contract_root: Path) -> None:
    _replace_once(
        contract_root,
        "docs/prompts/01-project-charter-and-scope.md",
        "- `docs/DEMO_ACCEPTANCE.md`",
        "- `docs/README.md`",
    )
    _assert_error(contract_root, "Prompt 01 required context")


def test_rejects_duplicate_acceptance_id(contract_root: Path) -> None:
    path = contract_root / "docs/milestones/01-project-charter-and-scope.md"
    path.write_text(
        path.read_text(encoding="utf-8") + "\nDuplicate marker: M01-AC01\n",
        encoding="utf-8",
    )
    _assert_error(contract_root, "exactly once")


def test_rejects_unresolved_owner_scope_decision(contract_root: Path) -> None:
    path = contract_root / "docs/PROJECT_CHARTER.md"
    path.write_text(
        path.read_text(encoding="utf-8") + "\nTBD: owner decision required.\n",
        encoding="utf-8",
    )
    _assert_error(contract_root, "unresolved decision marker")


def test_done_milestone_requires_accepted_adrs(contract_root: Path) -> None:
    status = contract_root / "IMPLEMENTATION_STATUS.md"
    updated, count = re.subn(
        r"(\| 01 \| Project charter and working-demo contract \| )"
        r"(?:READY|PENDING|IN_PROGRESS|BLOCKED|DONE)( \|)",
        r"\1DONE\2",
        status.read_text(encoding="utf-8"),
    )
    assert count == 1
    status.write_text(updated, encoding="utf-8")
    adr = contract_root / "docs/adr/0001-human-in-the-loop-boundary.md"
    proposed, count = re.subn(
        r"(## Status\s+)(?:Accepted|Proposed \(revalidation\))",
        r"\1Proposed (revalidation)",
        adr.read_text(encoding="utf-8"),
    )
    assert count == 1
    adr.write_text(proposed, encoding="utf-8")
    _assert_error(contract_root, "status must be Accepted")
