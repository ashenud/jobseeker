from __future__ import annotations

from pathlib import Path
import stat

import pytest
import yaml
from fastapi.testclient import TestClient
from pydantic import ValidationError

from job_agent.config.settings import Settings
from job_agent.db.base import Base
from job_agent.web.app import create_app
from job_agent.web.health import ComponentHealth, probe_dependencies
from job_agent.workers.app import create_celery_app

ROOT = Path(__file__).resolve().parents[1]


def test_settings_defaults_fail_closed() -> None:
    settings = Settings(_env_file=None)
    assert settings.source_enabled is False
    assert settings.llm_enabled is False
    assert settings.api_write_enabled is False
    assert settings.browser_fill_enabled is False
    assert settings.outreach_sending_enabled is False


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("JOB_AGENT_SOURCE_ENABLED", "sometimes"),
        ("JOB_AGENT_API_WRITE_ENABLED", "enabled"),
        ("JOB_AGENT_API_PORT", "not-a-port"),
        ("JOB_AGENT_DEPENDENCY_TIMEOUT_SECONDS", "60"),
        ("JOB_AGENT_DATABASE_URL", "sqlite:///unsafe.db"),
        ("JOB_AGENT_COMMIT_SHA", "not-a-commit-or-safe-default"),
    ],
)
def test_settings_reject_malformed_values(
    monkeypatch: pytest.MonkeyPatch, name: str, value: str
) -> None:
    monkeypatch.setenv(name, value)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_public_health_and_version_endpoints() -> None:
    commit_sha = "0123456789abcdef0123456789abcdef01234567"
    settings = Settings(_env_file=None, commit_sha=commit_sha)
    client = TestClient(
        create_app(
            settings=settings,
            readiness_probe=lambda: ComponentHealth(database=True, redis=True),
        )
    )

    assert client.get("/health/live").json() == {"status": "live"}
    assert client.get("/health/ready").json() == {
        "status": "ready",
        "components": {"database": "up", "redis": "up"},
    }
    assert client.get("/version").json() == {
        "version": "0.22.0",
        "commit": commit_sha,
    }


def test_readiness_is_503_and_secret_free_when_dependencies_fail() -> None:
    client = TestClient(
        create_app(readiness_probe=lambda: ComponentHealth(database=False, redis=True))
    )

    response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "components": {"database": "down", "redis": "up"},
    }
    assert "job_agent" not in response.text
    assert client.get("/health/live").status_code == 200


def test_real_readiness_probe_is_bounded_and_fails_closed() -> None:
    settings = Settings(
        _env_file=None,
        database_url="postgresql+psycopg://job_agent:secret@127.0.0.1:1/job_agent",
        redis_url="redis://:secret@127.0.0.1:1/0",
        dependency_timeout_seconds=0.1,
    )
    health = probe_dependencies(settings)
    assert health == ComponentHealth(database=False, redis=False)
    assert "secret" not in str(health.public_status())


def test_sqlalchemy_metadata_foundation_is_real_and_initially_empty() -> None:
    assert Base.metadata.tables == {}


def test_celery_application_uses_configured_broker_without_eager_tasks() -> None:
    settings = Settings(_env_file=None, redis_url="redis://redis:6379/9")
    celery_app = create_celery_app(settings)
    assert celery_app.conf.broker_url == "redis://redis:6379/9"
    assert celery_app.conf.task_always_eager is False
    assert celery_app.conf.enable_utc is True
    assert celery_app.conf.accept_content == ["json"]
    assert celery_app.conf.task_serializer == "json"


def test_compose_runtime_is_local_health_conditioned_and_persistent() -> None:
    compose = yaml.safe_load((ROOT / "compose.yaml").read_text(encoding="utf-8"))
    services = compose["services"]
    assert {"api", "worker", "scheduler", "db", "redis"} <= services.keys()
    assert services["api"]["ports"] == [
        "127.0.0.1:${JOB_AGENT_API_PORT:-8000}:8000"
    ]
    assert "ports" not in services["db"]
    assert "ports" not in services["redis"]
    for name in ("api", "worker", "scheduler", "db", "redis"):
        assert services[name]["healthcheck"]["test"]
        assert services[name]["cpus"]
        assert services[name]["mem_limit"]
    for name in ("api", "worker", "scheduler"):
        assert services[name]["depends_on"]["db"]["condition"] == "service_healthy"
        assert services[name]["depends_on"]["redis"]["condition"] == "service_healthy"
    assert set(compose["volumes"]) == {"postgres_data", "redis_data"}


def test_dependency_lock_and_build_context_are_not_placeholders() -> None:
    lock_text = (ROOT / "uv.lock").read_text(encoding="utf-8")
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    dockerignore = (ROOT / ".dockerignore").read_text(encoding="utf-8").splitlines()
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()

    assert lock_text.startswith("version = ")
    assert "placeholder" not in lock_text.lower()
    assert "uv sync --frozen" in dockerfile
    assert all(
        "@sha256:" in line
        for line in dockerfile.splitlines()
        if line.startswith("FROM ")
    )
    compose = (ROOT / "compose.yaml").read_text(encoding="utf-8")
    assert "pgvector/pgvector:pg16@sha256:" in compose
    assert "redis:7-alpine@sha256:" in compose
    assert ".env" in dockerignore
    assert "data/private" in dockerignore
    assert ".env" in gitignore
    assert "data/private/*" in gitignore


def test_required_wrappers_are_executable_compose_only_commands() -> None:
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    for target in (
        "bootstrap",
        "up",
        "down",
        "logs",
        "migrate",
        "test",
        "lint",
        "typecheck",
        "check",
    ):
        assert f"{target}:" in makefile

    recipe_lines = [
        line.strip()
        for line in makefile.splitlines()
        if line.startswith("\t") and line.strip()
    ]
    assert recipe_lines
    assert all(line.startswith("docker compose ") for line in recipe_lines)

    for relative in ("scripts/bootstrap.sh", "scripts/check.sh", "scripts/dev.sh"):
        path = ROOT / relative
        assert path.stat().st_mode & stat.S_IXUSR
        commands = [
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#!") and line.strip() != "set -euo pipefail"
        ]
        assert commands
        assert all(
            command.startswith("docker compose ")
            or command.startswith("exec docker compose ")
            for command in commands
        )
