#!/usr/bin/env bash
set -euo pipefail
python -m pip install -e '.[dev]'
cp -n .env.example .env || true
