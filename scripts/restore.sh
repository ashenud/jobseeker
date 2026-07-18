#!/usr/bin/env bash
set -euo pipefail
test -n "${1:-}" || { echo "usage: scripts/restore.sh backups/file.tgz"; exit 2; }
tar -xzf "$1"
