from celery import Celery
from app.config import config
from app.celery_app.config import celery_config
from app.tasks.documents import DocumentProcessingTask


celery_app = Celery(config.APP_NAME)
celery_app.conf.update(
    broker_url=celery_config.CELERY_BROKER_URL,
    result_backend=celery_config.CELERY_RESULT_BACKEND,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

celery_app.autodiscover_tasks(["app.tasks"])
celery_app.register_task(DocumentProcessingTask())