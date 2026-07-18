#!/usr/bin/env bash
set -euo pipefail
mkdir -p backups
stamp=$(date -u +%Y%m%dT%H%M%SZ)
tar --exclude='data/private/cache' -czf "backups/job-agent-$stamp.tgz" config data/private docs
printf 'created backups/job-agent-%s.tgz\n' "$stamp"
