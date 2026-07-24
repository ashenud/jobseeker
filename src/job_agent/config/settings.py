from decimal import Decimal
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated runtime configuration with local, fail-closed defaults."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="JOB_AGENT_",
        extra="ignore",
        validate_default=True,
    )

    env: Literal["local", "development", "test", "production"] = "local"
    bind_host: str = "127.0.0.1"
    api_port: int = Field(default=8000, ge=1, le=65535)
    database_url: PostgresDsn = PostgresDsn(
        "postgresql+psycopg://job_agent:job_agent@db:5432/job_agent"
    )
    redis_url: RedisDsn = RedisDsn("redis://redis:6379/0")
    dependency_timeout_seconds: float = Field(default=2.0, ge=0.1, le=10.0)
    source_enabled: bool = False
    llm_enabled: bool = False
    api_write_enabled: bool = False
    browser_fill_enabled: bool = False
    outreach_sending_enabled: bool = False
    daily_cost_limit_usd: Decimal = Field(default=Decimal("1.00"), ge=0)
    commit_sha: str = Field(default="unknown", pattern=r"^(unknown|[0-9a-f]{40})$")
