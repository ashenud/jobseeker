#!/usr/bin/env bash
set -euo pipefail
ruff check .
mypy src
pytest
job-agent release check
