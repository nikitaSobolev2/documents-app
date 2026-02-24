from fastapi import APIRouter, Depends, HTTPException, status as http_status
from sqlalchemy.orm import Session
from redis import Redis

from app.database import get_db
from app.schemas.system import AppBaseResponse
from app.schemas.documents import (
    DocumentCreate,
    DocumentCreateResponse,
    DocumentList,
    Document as DocumentSchema,
    DocumentProcessingTaskStatus,
    DocumentStatus,
)
from app.models.documents import (
    Document,
    DocumentProcessingTask as DocumentProcessingTaskModel,
)
from app.redis import get_redis
from app.tasks.documents import DocumentProcessingTask


documents_router = APIRouter(prefix="/documents", tags=["documents"])


@documents_router.get(
    "/",
    status_code=http_status.HTTP_200_OK,
    response_model=AppBaseResponse[DocumentList],
)
def get_document_list(limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    documents = db.query(Document).offset(offset).limit(limit).all()
    return AppBaseResponse[DocumentList](
        status=http_status.HTTP_200_OK, message="success", data=documents
    )


@documents_router.get(
    "/{document_id}",
    status_code=http_status.HTTP_200_OK,
    response_model=AppBaseResponse[DocumentSchema],
)
def get_document(
    document_id: int, db: Session = Depends(get_db), redis: Redis = Depends(get_redis)
):
    redis_document = redis.get(f"document:{document_id}")
    if redis_document:
        return AppBaseResponse[DocumentSchema](
            status=http_status.HTTP_200_OK,
            message="success",
            data=DocumentSchema.model_validate_json(redis_document),
        )

    db_document: Document = (
        db.query(Document).filter(Document.id == document_id).first()
    )
    if not db_document:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Document not found",
                "errors": [f"No document with id {document_id}"],
            },
        )

    redis.set(
        f"document:{document_id}",
        DocumentSchema.model_validate(db_document).model_dump_json(),
        ex=60,
    )

    return AppBaseResponse[DocumentSchema](
        status=http_status.HTTP_200_OK, message="success", data=db_document
    )


@documents_router.post(
    "/",
    status_code=http_status.HTTP_201_CREATED,
    response_model=AppBaseResponse[DocumentCreateResponse],
)
def create_document(document: DocumentCreate, db: Session = Depends(get_db)):
    new_document = Document(title=document.title, content=document.content)
    db.add(new_document)
    db.flush()

    task_row = DocumentProcessingTaskModel(document_id=new_document.id)
    db.add(task_row)
    db.commit()

    try:
        celery_result = DocumentProcessingTask.delay(task_row.id)
    except Exception as e:
        task_row.status = DocumentProcessingTaskStatus.FAILED
        task_row.error = str(e)
        db.commit()
        raise HTTPException(
            status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"message": "Message broker unavailable, try again later"},
        )

    data = DocumentCreateResponse(
        celery_task_id=celery_result.id,
        document_id=new_document.id,
        status=DocumentProcessingTaskStatus.PENDING,
    )
    return AppBaseResponse[DocumentCreateResponse](
        status=http_status.HTTP_201_CREATED, message="success", data=data
    )


@documents_router.patch(
    "/{document_id}/status/{status}",
    status_code=http_status.HTTP_200_OK,
    response_model=AppBaseResponse[DocumentSchema],
)
def update_document_status(
    document_id: int,
    status: DocumentStatus,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    db_document = db.query(Document).filter(Document.id == document_id).first()
    if not db_document:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Document not found",
                "errors": [f"No document with id {document_id}"],
            },
        )

    db_document.status = status

    db.commit()
    db.refresh(db_document)

    redis.delete(f"document:{document_id}")

    return AppBaseResponse[DocumentSchema](
        status=http_status.HTTP_200_OK, message="success", data=db_document
    )
