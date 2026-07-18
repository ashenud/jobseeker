#!/usr/bin/env python3
"""Validate status transitions and evidence-backed milestone completion."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "IMPLEMENTATION_STATUS.md"
ROW = re.compile(
    r"^\|\s*(\d{2})\s*\|.*?\|\s*(READY|PENDING|IN_PROGRESS|BLOCKED|DONE)\s*\|",
    re.MULTILINE,
)


def validate_receipt(number: str) -> list[str]:
    errors: list[str] = []
    path = ROOT / "artifacts" / "verification" / f"milestone-{number}.json"
    if not path.is_file():
        return [f"milestone {number} is DONE without {path.relative_to(ROOT)}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return [f"invalid receipt for milestone {number}: {exc}"]
    if str(data.get("milestone")) != number:
        errors.append(f"milestone {number} receipt has wrong milestone value")
    if data.get("result") != "PASS":
        errors.append(f"milestone {number} receipt result is not PASS")
    commands = data.get("commands")
    if not isinstance(commands, list) or not commands:
        errors.append(f"milestone {number} receipt has no commands")
    elif any(item.get("exit_code") != 0 for item in commands if isinstance(item, dict)):
        errors.append(f"milestone {number} receipt contains failed commands")
    acceptance = data.get("acceptance")
    if not isinstance(acceptance, dict) or not acceptance:
        errors.append(f"milestone {number} receipt has no acceptance results")
    elif any(item.get("result") != "PASS" for item in acceptance.values() if isinstance(item, dict)):
        errors.append(f"milestone {number} receipt contains failed acceptance IDs")
    if (data.get("review") or {}).get("verdict") != "GO":
        errors.append(f"milestone {number} receipt lacks independent GO")
    if (data.get("clean_checkout") or {}).get("result") != "PASS":
        errors.append(f"milestone {number} receipt lacks clean-checkout PASS")
    if data.get("placeholders") not in ([], None):
        errors.append(f"milestone {number} receipt lists production placeholders")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--milestone", type=str)
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()
    rows = ROW.findall(STATUS.read_text(encoding="utf-8"))
    errors: list[str] = []
    active = [number for number, state in rows if state in {"READY", "IN_PROGRESS", "BLOCKED"}]
    if len(active) != 1:
        errors.append(f"expected exactly one READY/IN_PROGRESS/BLOCKED milestone, found {active}")
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
