from __future__ import annotations

from collections.abc import Callable
from importlib.metadata import PackageNotFoundError, version

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from job_agent.config.settings import Settings
from job_agent.web.health import ComponentHealth, probe_dependencies


def _application_version() -> str:
    try:
        return version("job-agent")
    except PackageNotFoundError:
        return "unknown"


def create_app(
    *,
    settings: Settings | None = None,
    readiness_probe: Callable[[], ComponentHealth] | None = None,
) -> FastAPI:
    runtime_settings = settings or Settings()
    probe = readiness_probe or (lambda: probe_dependencies(runtime_settings))
    application = FastAPI(
        title="Jobseeker",
        version=_application_version(),
        docs_url=None,
        redoc_url=None,
    )

    @application.get("/health/live")
    def liveness() -> dict[str, str]:
        return {"status": "live"}

    @application.get("/health/ready")
    def readiness() -> JSONResponse:
        components = probe()
        status_code = 200 if components.ready else 503
        status = "ready" if components.ready else "not_ready"
        return JSONResponse(
            status_code=status_code,
            content={"status": status, "components": components.public_status()},
        )

    @application.get("/version")
    def application_version() -> dict[str, str]:
        return {
            "version": application.version,
            "commit": runtime_settings.commit_sha,
        }

    return application


app = create_app()
