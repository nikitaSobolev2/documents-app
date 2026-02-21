import httpx
import pytest
from typing import AsyncGenerator

from backend.app.schemas.documents import DocumentStatus
from backend.tests.documents_api.helpers import (
    create_document,
    delete_documents,
)


@pytest.fixture
async def created_document() -> AsyncGenerator[dict, None]:
    doc = await create_document(
        title="test document title",
        content="test document content",
    )

    yield doc

    await delete_documents([doc["id"]])


def test_create_document_valid(created_document: dict):
    assert isinstance(created_document["id"], int)
    assert created_document["title"] == "test document title"
    assert created_document["content"] == "test document content"
    assert created_document["status"] == DocumentStatus.DRAFT.value


async def test_create_document_invalid():
    with pytest.raises(httpx.HTTPStatusError):
        await create_document(
            title="",
            content="test document content",
        )