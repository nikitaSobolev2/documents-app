import httpx
import os
from sqlalchemy import select

from backend.app.database import get_db
from backend.app.models.documents import Document as DocumentModel

APP_URL = os.getenv("APP_URL")


async def create_document(title: str, content: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{APP_URL}/api/v1/documents",
            json={
                "title": title,
                "content": content,
            },
        )
        response.raise_for_status()
        return response.json()["data"]


async def get_document_list() -> list[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{APP_URL}/api/v1/documents")
        response.raise_for_status()
        return response.json()["data"]


async def get_document(document_id: int) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{APP_URL}/api/v1/documents/{document_id}")
        response.raise_for_status()
        return response.json()["data"]

async def change_document_status(document_id: int, status: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{APP_URL}/api/v1/documents/{document_id}/status/{status}",
        )
        response.raise_for_status()
        return response.json()["data"]


def delete_documents(document_ids: list[int]) -> None:
    db = next(get_db())
    
    try:
        query = select(DocumentModel).where(DocumentModel.id.in_(document_ids))
        result = db.execute(query)
        documents = result.scalars().all()

        for document in documents:
            db.delete(document)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
