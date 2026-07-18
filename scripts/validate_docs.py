#!/usr/bin/env python3
"""Validate the canonical milestone/prompt documentation structure."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
LINK = re.compile(r"\[[^]]*\]\(([^)]+)\)")
M00_ACCEPTANCE = re.compile(r"\bM00-AC(\d{2})\b")
M01_ACCEPTANCE = re.compile(r"\bM01-AC(\d{2})\b")
MILESTONE_01_STATE = re.compile(
    r"^\|\s*01\s*\|.*?\|\s*(READY|PENDING|IN_PROGRESS|BLOCKED|DONE)\s*\|",
    re.MULTILINE,
)


def _normalized(text: str) -> str:
    return " ".join(text.casefold().split())


def _require_phrases(
    text: str,
    phrases: tuple[str, ...],
    label: str,
) -> list[str]:
    normalized = _normalized(text)
    return [
        f"{label} lacks required M01 semantic: {phrase}"
        for phrase in phrases
        if phrase not in normalized
    ]


def _read_required(root: Path, relative: str, errors: list[str]) -> str:
    path = root / relative
    if not path.is_file():
        errors.append(f"missing M01 contract file: {relative}")
        return ""
    return path.read_text(encoding="utf-8")


def validate_m01_semantics(root: Path = ROOT) -> list[str]:
    """Validate the frozen M01 charter across its milestone, prompt, ADRs, and README."""
    errors: list[str] = []
    files = {
        "milestone": _read_required(
            root, "docs/milestones/01-project-charter-and-scope.md", errors
        ),
        "prompt": _read_required(root, "docs/prompts/01-project-charter-and-scope.md", errors),
        "charter": _read_required(root, "docs/PROJECT_CHARTER.md", errors),
        "adr1": _read_required(root, "docs/adr/0001-human-in-the-loop-boundary.md", errors),
        "adr2": _read_required(root, "docs/adr/0002-local-first-mvp.md", errors),
        "readme": _read_required(root, "README.md", errors),
        "status": _read_required(root, "IMPLEMENTATION_STATUS.md", errors),
    }
    if errors:
        return errors

    expected_ids = [f"{number:02d}" for number in range(1, 5)]
    milestone_ids = M01_ACCEPTANCE.findall(files["milestone"])
    all_ids = M01_ACCEPTANCE.findall("\n".join(files.values()))
    if sorted(milestone_ids) != expected_ids or len(milestone_ids) != len(expected_ids):
        errors.append("milestone 01 must define M01-AC01 through M01-AC04 exactly once")
    if sorted(all_ids) != expected_ids or len(all_ids) != len(expected_ids):
        errors.append("M01 acceptance IDs must occur only once in the milestone document")

    prompt = _normalized(files["prompt"])
    if "dependencies recorded in the master index: **00**." not in prompt:
        errors.append("Prompt 01 dependency must be milestone 00")
    if "docs/demo_acceptance.md" not in prompt:
        errors.append("Prompt 01 required context must include docs/DEMO_ACCEPTANCE.md")

    charter = files["charter"]
    errors.extend(
        _require_phrases(
            charter,
            (
                "approval never transmits",
                "owner leaves the application",
                "no official write connector is part of the mvp demo",
                "manual capture",
                "jobicy rss/api",
                "remote ok json/rss",
                "openai responses api structured output",
                "naming a provider or source grants no permission",
                "credential",
                "spend",
                "endpoint selection",
                "model selection",
                "write authorization",
                "milestone 02 is authoritative",
                "milestone 08 is authoritative",
                "milestone 10 is authoritative",
                "behance and upwork remain manual capture and manual owner submission",
                "zero duplicate normalized jobs",
                "zero unsupported proposal claims",
                "zero unapproved external actions",
                "all application builds, dependency resolution, python commands",
                "host may run only git, docker/compose orchestration",
                "these are downstream inputs, not open scope questions",
            ),
            "project charter",
        )
    )
    flow_match = re.search(
        r"## Ordered user-visible demo flow\s+(.*?)(?=\n## )",
        charter,
        re.DOTALL,
    )
    if flow_match is None:
        errors.append("project charter lacks the ordered user-visible demo flow")
    else:
        steps = [int(item) for item in re.findall(r"(?m)^(\d+)\.\s", flow_match.group(1))]
        if steps != list(range(1, 13)):
            errors.append("project charter demo flow must contain ordered steps 1 through 12")

    forbidden_open_decisions = (
        "scope ambiguities requiring owner approval",
        "owner decision required",
        "to be decided",
        "unresolved owner decision",
        "tbd",
    )
    normalized_charter = _normalized(charter)
    for phrase in forbidden_open_decisions:
        if phrase in normalized_charter:
            errors.append(f"project charter contains an unresolved decision marker: {phrase}")

    state_match = MILESTONE_01_STATE.search(files["status"])
    if state_match is None:
        errors.append("implementation status lacks the Milestone 01 state")
        expected_adr_status = "proposed (revalidation)"
    else:
        expected_adr_status = (
            "accepted" if state_match.group(1) == "DONE" else "proposed (revalidation)"
        )
    for name in ("adr1", "adr2"):
        normalized_adr = _normalized(files[name])
        if f"## status {expected_adr_status}" not in normalized_adr:
            errors.append(f"{name} status must be {expected_adr_status.title()}")
    errors.extend(
        _require_phrases(
            files["adr1"],
            (
                "approval is not transmission",
                "demo ends at manual owner submission",
                "single-use per-action confirmation token",
            ),
            "ADR 0001",
        )
    )
    errors.extend(
        _require_phrases(
            files["adr2"],
            (
                "mvp is local-first and docker-only",
                "all application builds, dependency resolution, python commands",
                "host may run git, docker/compose orchestration",
                "host python environments are not part of the workflow",
            ),
            "ADR 0002",
        )
    )
    errors.extend(
        _require_phrases(
            files["readme"],
            (
                "approval never transmits",
                "no official write connector is part of the mvp demo",
                "single-use per-action confirmation token",
                "audit record containing the action id",
                "all application builds, dependency resolution, python commands",
                "host is limited to git, docker/compose orchestration",
            ),
            "README",
        )
    )
    return errors


def expected_files(folder: Path) -> tuple[dict[str, Path], list[str]]:
    result: dict[str, Path] = {}
    duplicates: list[str] = []
    for path in folder.glob("[0-2][0-9]-*.md"):
        number = path.name[:2]
        if number in result:
            duplicates.append(f"{number}: {result[number].name}, {path.name}")
        result[number] = path
    return result, duplicates


def main() -> int:
    errors: list[str] = []
    errors.extend(validate_m01_semantics())
    milestone_files, milestone_duplicates = expected_files(DOCS / "milestones")
    prompt_files, prompt_duplicates = expected_files(DOCS / "prompts")
    errors.extend(f"duplicate milestone IDs: {item}" for item in milestone_duplicates)
    errors.extend(f"duplicate prompt IDs: {item}" for item in prompt_duplicates)
    expected = {f"{number:02d}" for number in range(23)}
    for label, files in (("milestone", milestone_files), ("prompt", prompt_files)):
        missing = sorted(expected - files.keys())
        extra = sorted(files.keys() - expected)
        if missing:
            errors.append(f"missing {label} IDs: {', '.join(missing)}")
        if extra:
            errors.append(f"unexpected {label} IDs: {', '.join(extra)}")

    for number in sorted(expected):
        if number == "00":
            continue
        milestone = milestone_files.get(number)
        prompt = prompt_files.get(number)
        if milestone and "## Recovery gate" not in milestone.read_text(encoding="utf-8"):
            errors.append(f"{milestone.relative_to(ROOT)} lacks Recovery gate")
        if milestone and "## Codex execution prompt" in milestone.read_text(encoding="utf-8"):
            errors.append(f"{milestone.relative_to(ROOT)} embeds a duplicate execution prompt")
        if prompt:
            text = prompt.read_text(encoding="utf-8")
            if prompt.name != milestone.name:
                errors.append(
                    f"prompt/milestone slug mismatch for {number}: {prompt.name} != {milestone.name}"
                )
            if "$jobseeker-milestone" not in text:
                errors.append(f"{prompt.relative_to(ROOT)} does not invoke the repo skill")
            if f"artifacts/verification/milestone-{number}.json" not in text:
                errors.append(f"{prompt.relative_to(ROOT)} has no milestone-specific receipt")

    milestone_zero = milestone_files.get("00")
    prompt_zero = prompt_files.get("00")
    if milestone_zero:
        ids = M00_ACCEPTANCE.findall(milestone_zero.read_text(encoding="utf-8"))
        expected_ids = [f"{number:02d}" for number in range(1, 11)]
        if sorted(set(ids)) != expected_ids or len(ids) != len(expected_ids):
            errors.append("milestone 00 must define M00-AC01 through M00-AC10 exactly once")
    if prompt_zero and M00_ACCEPTANCE.search(prompt_zero.read_text(encoding="utf-8")):
        errors.append("Prompt 00 must remain execution-only; M00 acceptance belongs in the milestone")

    for number in range(23):
        duplicates = list(DOCS.glob(f"{number:02d}-*.md"))
        if duplicates:
            errors.append(f"root milestone duplicate exists: {duplicates[0].relative_to(ROOT)}")

    for path in DOCS.rglob("*.md"):
        content = path.read_text(encoding="utf-8")
        for target in LINK.findall(content):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            clean = target.split("#", 1)[0].strip("<>")
            if clean and not (path.parent / clean).resolve().exists():
                errors.append(f"broken link in {path.relative_to(ROOT)}: {target}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("documentation validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
