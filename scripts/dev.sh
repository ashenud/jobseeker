#!/usr/bin/env bash
set -euo pipefail
uvicorn job_agent.web.app:create_app --factory --host 127.0.0.1 --port 8000 --reload
