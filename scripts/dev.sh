#!/usr/bin/env bash
set -euo pipefail
exec docker compose --profile dev up --build api
