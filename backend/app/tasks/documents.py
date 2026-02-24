import time
from celery import Task
from redis import Redis
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.schemas.documents import DocumentProcessingTaskStatus, DocumentStatus
from app.models.documents import (
    Document,
    DocumentProcessingTask as DocumentProcessingTaskModel,
)
from app.redis import redis_client
from app.celery_app import celery_app


class DocumentProcessingTask(Task):
    name = "document_processing_task"
    max_retries = 3
    retry_backoff = 2
    retry_backoff_max = 60
    retry_jitter = True

    def before_start(self, task_id, args, kwargs):
        self.db: Session = SessionLocal()
        self.redis: Redis = redis_client

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        self.db.close()

    def run(self, task_row_id: int):
        is_retry = self.request.retries > 0
        stmt = (
            select(DocumentProcessingTaskModel)
            .where(DocumentProcessingTaskModel.id == task_row_id)
            .with_for_update()
        )
        task_row: DocumentProcessingTaskModel = self.db.execute(
            stmt
        ).scalar_one_or_none()

        self._validate_task_row(task_row_id, task_row, is_retry)

        if not is_retry:
            task_row.status = DocumentProcessingTaskStatus.PROCESSING
            task_row.celery_task_id = self.request.id
            self.db.commit()

        try:
            stmt = (
                select(Document)
                .where(Document.id == task_row.document_id)
                .with_for_update()
            )
            document: Document = self.db.execute(stmt).scalar_one_or_none()
            if not document:
                self.db.rollback()
                raise ValueError(f"Document {task_row.document_id} not found")

            time.sleep(5)
            result = f"processed document '{document.title}'"
            document.status = DocumentStatus.PUBLISHED

            task_row.status = DocumentProcessingTaskStatus.COMPLETED
            task_row.result = result
        except ValueError as exc:
            self.db.rollback()
            task_row.status = DocumentProcessingTaskStatus.FAILED
            task_row.error = str(exc)
            self.db.commit()
            raise
        except Exception as exc:
            self.db.rollback()
            try:
                raise self.retry(exc=exc)
            except self.MaxRetriesExceededError:
                task_row.status = DocumentProcessingTaskStatus.FAILED
                task_row.error = str(exc)
                self.db.commit()
                raise

        self.db.commit()
        self.redis.delete(f"document:{task_row.document_id}")

    def _validate_task_row(
        self, task_row_id: int, task_row: DocumentProcessingTaskModel, is_retry: bool
    ):
        if not task_row:
            self.db.rollback()
            raise ValueError(f"DocumentProcessingTask row {task_row_id} not found")

        if is_retry:
            if task_row.status not in [
                DocumentProcessingTaskStatus.PROCESSING,
                DocumentProcessingTaskStatus.FAILED,
            ]:
                self.db.rollback()
                raise ValueError(
                    f"DocumentProcessingTask row {task_row_id} is not processing or failed, it is {task_row.status}"
                )
        else:
            if task_row.status != DocumentProcessingTaskStatus.PENDING:
                self.db.rollback()
                raise ValueError(
                    f"DocumentProcessingTask row {task_row_id} is not pending, it is {task_row.status}"
                )

        if task_row.celery_task_id is not None and not is_retry:
            self.db.rollback()
            raise ValueError(
                f"DocumentProcessingTask row {task_row_id} already has a celery task id, it is {task_row.celery_task_id}"
            )

        if task_row.document_id is None:
            self.db.rollback()
            raise ValueError(
                f"DocumentProcessingTask row {task_row_id} does not have a document id"
            )

        return True


DocumentProcessingTask = celery_app.register_task(DocumentProcessingTask())
