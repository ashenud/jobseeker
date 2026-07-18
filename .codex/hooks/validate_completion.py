#!/usr/bin/env python3
"""Block a turn from ending with evidence-free DONE milestone rows."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys


DONE_ROW = re.compile(r"^\|\s*(\d{2})\s*\|.*\|\s*DONE\s*\|", re.MULTILINE)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        root = Path(str(payload.get("cwd") or ".")).resolve()
    except (json.JSONDecodeError, OSError):
        root = Path.cwd()
    status = root / "IMPLEMENTATION_STATUS.md"
    if not status.exists():
        return 0
    done = DONE_ROW.findall(status.read_text(encoding="utf-8"))
    missing = [
        item
        for item in done
        if not (root / "artifacts" / "verification" / f"milestone-{item}.json").is_file()
    ]
    if missing:
        result = {
            "decision": "block",
            "reason": (
                "Milestones marked DONE lack verification receipts: "
                + ", ".join(missing)
                + ". Restore an honest state or generate validated evidence from real Docker results."
            ),
        }
        print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
