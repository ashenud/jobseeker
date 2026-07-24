from __future__ import annotations

from math import ceil

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from job_agent.config.settings import Settings


def build_engine(settings: Settings, *, pool_pre_ping: bool = True) -> Engine:
    timeout = max(1, ceil(settings.dependency_timeout_seconds))
    return create_engine(
        str(settings.database_url),
        connect_args={
            "connect_timeout": timeout,
            "options": f"-c statement_timeout={timeout * 1000}",
        },
        pool_pre_ping=pool_pre_ping,
    )


def session_factory(settings: Settings) -> sessionmaker[Session]:
    return sessionmaker(bind=build_engine(settings), expire_on_commit=False)
