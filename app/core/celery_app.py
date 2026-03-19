from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.scraper.tasks", "app.scraper.discovery"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Manila",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    worker_pool=settings.CELERY_WORKER_POOL,
    worker_concurrency=settings.CELERY_WORKER_CONCURRENCY,
    beat_schedule_filename=settings.CELERY_BEAT_SCHEDULE_FILE,
)
