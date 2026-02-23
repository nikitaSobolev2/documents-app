import httpx
import pytest
from typing import AsyncGenerator

from app.schemas.documents import DocumentStatus
from backend.tests.documents_api.helpers import (
    create_document,
    delete_documents,
    get_document,
)


@pytest.fixture
async def created_document() -> AsyncGenerator[dict, None]:
    doc = await create_document(
        title="test document title",
        content="test document content",
    )

    yield doc

    await delete_documents([doc["id"]])


async def test_get_document_valid(created_document: dict):
    result = await get_document(created_document["id"])

    assert result["id"] == created_document["id"]
    assert result["title"] == created_document["title"]
    assert result["content"] == created_document["content"]
    assert result["status"] in [s.value for s in DocumentStatus]

async def test_get_document_invalid():
    with pytest.raises(httpx.HTTPStatusError):
        await get_document(-1)