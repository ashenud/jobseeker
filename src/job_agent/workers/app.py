from celery import Celery

from job_agent.config.settings import Settings


def create_celery_app(settings: Settings | None = None) -> Celery:
    runtime_settings = settings or Settings()
    application = Celery(
        "job_agent",
        broker=str(runtime_settings.redis_url),
    )
    application.conf.update(
        accept_content=["json"],
        broker_connection_retry_on_startup=True,
        broker_connection_timeout=runtime_settings.dependency_timeout_seconds,
        broker_transport_options={
            "socket_connect_timeout": runtime_settings.dependency_timeout_seconds,
            "socket_timeout": runtime_settings.dependency_timeout_seconds,
        },
        enable_utc=True,
        result_serializer="json",
        task_serializer="json",
        task_always_eager=False,
        task_ignore_result=True,
        timezone="UTC",
    )
    return application


celery_app = create_celery_app()
