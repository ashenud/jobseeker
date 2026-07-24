from __future__ import annotations

import argparse
import os
from pathlib import Path

from job_agent.config.settings import Settings
from job_agent.web.health import probe_dependencies


def _process_is_running(pidfile: Path) -> bool:
    try:
        pid = int(pidfile.read_text(encoding="utf-8").strip())
        os.kill(pid, 0)
    except (OSError, ValueError):
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pidfile", type=Path, required=True)
    args = parser.parse_args()
    dependencies = probe_dependencies(Settings())
    return 0 if dependencies.ready and _process_is_running(args.pidfile) else 1


if __name__ == "__main__":
    raise SystemExit(main())
