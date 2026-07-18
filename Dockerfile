FROM python:3.12-slim

RUN apt-get update \
    && apt-get install --yes --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml README.md /app/
COPY src /app/src
RUN pip install --no-cache-dir --disable-pip-version-check -e ".[dev]"
COPY .agents /app/.agents
COPY .codex /app/.codex
COPY config /app/config
COPY docs /app/docs
COPY scripts /app/scripts
COPY tests /app/tests
COPY .pre-commit-config.yaml AGENTS.md CHANGELOG.md IMPLEMENTATION_STATUS.md Makefile /app/

EXPOSE 8000
CMD ["uvicorn", "job_agent.web.app:create_app", "--factory", "--host", "127.0.0.1", "--port", "8000"]
