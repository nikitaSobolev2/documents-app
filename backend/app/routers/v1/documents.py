from fastapi import APIRouter, Depends, HTTPException, status as http_status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.system import AppBaseResponse
from app.schemas.documents import (
    DocumentCreate,
    DocumentList,
    Document as DocumentSchema,
    DocumentStatus,
)
from app.models.documents import Document


documents_router = APIRouter(prefix="/documents", tags=["documents"])


@documents_router.get(
    "/", status_code=http_status.HTTP_200_OK, response_model=AppBaseResponse[DocumentList]
)
def get_document_list(limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    documents = db.query(Document).offset(offset).limit(limit).all()
    return AppBaseResponse[DocumentList](
        status=http_status.HTTP_200_OK, message="success", data=documents
    )


@documents_router.post(
    "/",
    status_code=http_status.HTTP_201_CREATED,
    response_model=AppBaseResponse[DocumentSchema],
)
def create_document(document: DocumentCreate, db: Session = Depends(get_db)):
    new_document = Document(title=document.title, content=document.content)

    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    return AppBaseResponse[DocumentSchema](
        status=http_status.HTTP_201_CREATED, message="success", data=new_document
    )


@documents_router.get(
    "/{document_id}",
    status_code=http_status.HTTP_200_OK,
    response_model=AppBaseResponse[DocumentSchema],
)
def get_document(document_id: int, db: Session = Depends(get_db)):
    db_document = db.query(Document).filter(Document.id == document_id).first()
    if not db_document:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail={"message": "Document not found", "errors": [f"No document with id {document_id}"]},
        )

    return AppBaseResponse[DocumentSchema](
        status=http_status.HTTP_200_OK, message="success", data=db_document
    )


@documents_router.patch(
    "/{document_id}/status/{status}",
    status_code=http_status.HTTP_200_OK,
    response_model=AppBaseResponse[DocumentSchema],
)
def update_document_status(
    document_id: int, status: DocumentStatus, db: Session = Depends(get_db)
):
    db_document = db.query(Document).filter(Document.id == document_id).first()
    if not db_document:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail={"message": "Document not found", "errors": [f"No document with id {document_id}"]},
        )

    db_document.status = status

    db.commit()
    db.refresh(db_document)

    return AppBaseResponse[DocumentSchema](
        status=http_status.HTTP_200_OK, message="success", data=db_document
    )
