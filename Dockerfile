# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:0.8.14@sha256:f3660c56d5b08d6c516360981bedc439f499b9bf37f46a216018da3777a74011 AS uv
FROM python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7

RUN apt-get update \
    && apt-get install --yes --no-install-recommends curl git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=uv /uv /uvx /usr/local/bin/

ENV PATH="/opt/job-agent-venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/job-agent-venv

COPY pyproject.toml uv.lock README.md /app/
RUN uv sync --frozen --no-install-project --extra dev

COPY src /app/src
RUN uv sync --frozen --extra dev --no-editable

COPY .agents /app/.agents
COPY .codex /app/.codex
COPY config /app/config
COPY docs /app/docs
COPY scripts /app/scripts
COPY tests /app/tests
COPY .pre-commit-config.yaml AGENTS.md CHANGELOG.md IMPLEMENTATION_STATUS.md Makefile /app/

EXPOSE 8000
CMD ["uvicorn", "job_agent.web.app:app", "--host", "0.0.0.0", "--port", "8000"]
