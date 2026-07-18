#!/usr/bin/env python3
"""Validate status transitions and evidence-backed milestone completion."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "IMPLEMENTATION_STATUS.md"
ROW = re.compile(
    r"^\|\s*(\d{2})\s*\|.*?\|\s*(READY|PENDING|IN_PROGRESS|BLOCKED|DONE)\s*\|",
    re.MULTILINE,
)
ACCEPTANCE_ID = re.compile(r"M(?P<milestone>\d{2})-AC\d{2}")
COMMIT = re.compile(r"[0-9a-f]{40}")
DIGEST = re.compile(r"sha256:[0-9a-f]{64}")


def _nonempty_strings(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, str) and bool(item.strip()) for item in value
    )


def _reference_errors(root: Path, value: Any, label: str) -> list[str]:
    """Require repository-relative, traversal-free references to regular files."""
    if not _nonempty_strings(value):
        return [f"{label} lacks references"]
    errors: list[str] = []
    resolved_root = root.resolve()
    for reference in value:
        relative = Path(reference)
        if relative.is_absolute() or ".." in relative.parts:
            errors.append(f"{label} has unsafe reference: {reference}")
            continue
        resolved = (resolved_root / relative).resolve()
        try:
            resolved.relative_to(resolved_root)
        except ValueError:
            errors.append(f"{label} reference escapes repository: {reference}")
            continue
        if not resolved.is_file():
            errors.append(f"{label} reference is not a regular file: {reference}")
    return errors


def _documented_acceptance(root: Path, number: str) -> set[str]:
    matches = sorted((root / "docs" / "milestones").glob(f"{number}-*.md"))
    if len(matches) != 1:
        return set()
    return {
        match.group(0)
        for match in ACCEPTANCE_ID.finditer(matches[0].read_text(encoding="utf-8"))
        if match.group("milestone") == number
    }


def _validate_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value.endswith("Z"):
        return False
    try:
        parsed = datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() == UTC.utcoffset(parsed)


def validate_receipt(number: str, root: Path = ROOT) -> list[str]:
    """Return every schema or acceptance error for one milestone receipt."""
    errors: list[str] = []
    path = root / "artifacts" / "verification" / f"milestone-{number}.json"
    if not path.is_file():
        return [f"milestone {number} is DONE without {path.relative_to(root)}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return [f"invalid receipt for milestone {number}: {exc}"]
    if not isinstance(data, dict):
        return [f"milestone {number} receipt root is not an object"]

    if data.get("milestone") != number:
        errors.append(f"milestone {number} receipt has wrong milestone value")
    if not isinstance(data.get("tested_commit"), str) or not COMMIT.fullmatch(
        data["tested_commit"]
    ):
        errors.append(f"milestone {number} receipt lacks a full tested commit SHA")
    if not _validate_timestamp(data.get("timestamp_utc")):
        errors.append(f"milestone {number} receipt lacks a valid UTC timestamp")
    if not isinstance(data.get("image_digest"), str) or not DIGEST.fullmatch(
        data["image_digest"]
    ):
        errors.append(f"milestone {number} receipt lacks a sha256 image digest")
    if data.get("result") != "PASS":
        errors.append(f"milestone {number} receipt result is not PASS")

    commands = data.get("commands")
    if not isinstance(commands, list) or not commands:
        errors.append(f"milestone {number} receipt has no commands")
    else:
        for index, item in enumerate(commands, start=1):
            label = f"milestone {number} command {index}"
            if not isinstance(item, dict):
                errors.append(f"{label} is not an object")
                continue
            command = item.get("command")
            if not isinstance(command, str) or not command.strip():
                errors.append(f"{label} lacks command text")
            if item.get("exit_code") != 0:
                errors.append(f"{label} exit_code is not zero")
            duration = item.get("duration_seconds")
            if not isinstance(duration, (int, float)) or isinstance(duration, bool) or duration < 0:
                errors.append(f"{label} lacks a nonnegative duration_seconds")
            log_errors = _reference_errors(root, item.get("log_refs"), label)
            errors.extend(error.replace("lacks references", "lacks log references") for error in log_errors)
            if isinstance(command, str) and re.search(r"(^|\s)pytest(?:\s|$)", command):
                test_count = item.get("test_count")
                if not isinstance(test_count, int) or isinstance(test_count, bool) or test_count <= 0:
                    errors.append(f"{label} requires a nonzero test_count")

    acceptance = data.get("acceptance")
    documented = _documented_acceptance(root, number)
    if not documented:
        errors.append(f"milestone {number} has no documented acceptance IDs")
    if not isinstance(acceptance, dict) or not acceptance:
        errors.append(f"milestone {number} receipt has no acceptance results")
    else:
        actual = set(acceptance)
        missing = sorted(documented - actual)
        unexpected = sorted(actual - documented)
        if missing:
            errors.append(f"milestone {number} receipt misses acceptance IDs: {', '.join(missing)}")
        if unexpected:
            errors.append(
                f"milestone {number} receipt has undocumented acceptance IDs: "
                + ", ".join(unexpected)
            )
        for acceptance_id, item in acceptance.items():
            if not isinstance(item, dict):
                errors.append(f"milestone {number} acceptance {acceptance_id} is not an object")
                continue
            if item.get("result") != "PASS":
                errors.append(f"milestone {number} acceptance {acceptance_id} is not PASS")
            errors.extend(
                _reference_errors(
                    root,
                    item.get("references"),
                    f"milestone {number} acceptance {acceptance_id}",
                )
            )

    review = data.get("review")
    if not isinstance(review, dict) or review.get("verdict") != "GO":
        errors.append(f"milestone {number} receipt lacks independent GO")
    else:
        if not isinstance(review.get("reviewer"), str) or not review["reviewer"].strip():
            errors.append(f"milestone {number} receipt lacks an independent reviewer")
        errors.extend(
            _reference_errors(root, review.get("references"), f"milestone {number} review")
        )
        if review.get("unresolved_high_critical") != []:
            errors.append(f"milestone {number} review has unresolved high/critical findings")

    clean_checkout = data.get("clean_checkout")
    if not isinstance(clean_checkout, dict) or clean_checkout.get("result") != "PASS":
        errors.append(f"milestone {number} receipt lacks clean-checkout PASS")
    else:
        errors.extend(
            _reference_errors(
                root,
                clean_checkout.get("references"),
                f"milestone {number} clean-checkout result",
            )
        )

    placeholders = data.get("placeholders")
    if not isinstance(placeholders, dict) or placeholders.get("result") != "PASS":
        errors.append(f"milestone {number} receipt lacks a passing placeholder scan")
    else:
        if placeholders.get("matches") != []:
            errors.append(f"milestone {number} receipt lists production placeholders")
        errors.extend(
            _reference_errors(
                root,
                placeholders.get("references"),
                f"milestone {number} placeholder scan",
            )
        )
    limitations = data.get("known_limitations")
    if not isinstance(limitations, list) or not all(isinstance(item, str) for item in limitations):
        errors.append(f"milestone {number} receipt lacks a known_limitations list")
    return errors


def validate_status(root: Path = ROOT) -> list[str]:
    status = root / "IMPLEMENTATION_STATUS.md"
    if not status.is_file():
        return ["IMPLEMENTATION_STATUS.md is missing"]
    rows = ROW.findall(status.read_text(encoding="utf-8"))
    errors: list[str] = []
    if len(rows) != 23 or {number for number, _ in rows} != {
        f"{number:02d}" for number in range(23)
    }:
        errors.append("status ledger must contain exactly milestones 00 through 22")
    active = [number for number, state in rows if state in {"READY", "IN_PROGRESS", "BLOCKED"}]
    if len(active) != 1:
        errors.append(f"expected exactly one READY/IN_PROGRESS/BLOCKED milestone, found {active}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--milestone", type=str)
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()
    rows = ROW.findall(STATUS.read_text(encoding="utf-8"))
    errors = validate_status()
    targets = [number for number, state in rows if state == "DONE"]
    if args.milestone:
        targets = [args.milestone]
    elif not args.all:
        parser.error("use --all or --milestone NN")
    for number in targets:
        if not re.fullmatch(r"\d{2}", number):
            errors.append(f"invalid milestone ID: {number}")
            continue
        errors.extend(validate_receipt(number))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("milestone validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
