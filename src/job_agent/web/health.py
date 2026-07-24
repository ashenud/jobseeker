from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from redis import Redis
from sqlalchemy import text

from job_agent.config.settings import Settings
from job_agent.db.session import build_engine


@dataclass(frozen=True)
class ComponentHealth:
    database: bool
    redis: bool

    @property
    def ready(self) -> bool:
        return self.database and self.redis

    def public_status(self) -> dict[str, str]:
        return {
            "database": "up" if self.database else "down",
            "redis": "up" if self.redis else "down",
        }


class ReadinessProbe(Protocol):
    def __call__(self) -> ComponentHealth: ...


def probe_dependencies(settings: Settings) -> ComponentHealth:
    """Perform bounded dependency I/O without returning exception or URL details."""

    database_up = False
    engine = build_engine(settings)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        database_up = True
    except Exception:
        database_up = False
    finally:
        engine.dispose()

    redis_up = False
    redis_client = Redis.from_url(
        str(settings.redis_url),
        socket_connect_timeout=settings.dependency_timeout_seconds,
        socket_timeout=settings.dependency_timeout_seconds,
    )
    try:
        redis_up = bool(redis_client.ping())
    except Exception:
        redis_up = False
    finally:
        redis_client.close()

    return ComponentHealth(database=database_up, redis=redis_up)
