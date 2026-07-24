from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from job_agent.config.settings import Settings
from job_agent.db.session import build_engine
from job_agent.web.app import create_app

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("JOB_AGENT_RUN_INTEGRATION") != "true",
        reason="requires Compose PostgreSQL and Redis services",
    ),
]


def test_public_readiness_uses_real_postgres_and_redis() -> None:
    client = TestClient(create_app(settings=Settings(_env_file=None)))
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "components": {"database": "up", "redis": "up"},
    }


def test_postgres_has_pgvector_and_expected_alembic_revision() -> None:
    engine = build_engine(Settings(_env_file=None))
    try:
        with engine.connect() as connection:
            extension = connection.scalar(
                text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
            )
            revision = connection.scalar(text("SELECT version_num FROM alembic_version"))
    finally:
        engine.dispose()
    assert extension == "vector"
    assert revision == "0001_initial"
