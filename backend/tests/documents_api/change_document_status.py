import httpx
import pytest
from typing import AsyncGenerator

from app.schemas.documents import DocumentStatus
from backend.tests.documents_api.helpers import (
    create_document,
    delete_documents,
    change_document_status,
)


@pytest.fixture
async def created_document() -> AsyncGenerator[dict, None]:
    doc = await create_document(
        title="test document title",
        content="test document content",
    )

    yield doc
    
    await delete_documents([doc["id"]])


@pytest.mark.parametrize("status", [s.value for s in DocumentStatus])
async def test_change_document_status_valid(created_document: dict, status: str):
    result = await change_document_status(created_document["id"], status)

    assert result["id"] == created_document["id"]
    assert result["title"] == created_document["title"]
    assert result["content"] == created_document["content"]
    assert result["status"] == status


async def test_change_document_status_invalid(created_document: dict):
    with pytest.raises(httpx.HTTPStatusError):
        await change_document_status(created_document["id"], "invalid_status_value")
