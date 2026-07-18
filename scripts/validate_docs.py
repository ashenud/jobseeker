#!/usr/bin/env python3
"""Validate the canonical milestone/prompt documentation structure."""

from __future__ import annotations

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
LINK = re.compile(r"\[[^]]*\]\(([^)]+)\)")


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
