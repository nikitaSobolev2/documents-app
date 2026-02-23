import httpx
import pytest
from typing import AsyncGenerator

from app.schemas.enums import DocumentProcessingTaskStatus
from tests.documents_api.helpers import (
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

    delete_documents([doc["document_id"]])


def test_create_document_valid(created_document: dict):
    assert isinstance(created_document["document_id"], int)
    assert isinstance(created_document["celery_task_id"], str)
    assert created_document["status"] == DocumentProcessingTaskStatus.PENDING.value


async def test_create_document_invalid():
    with pytest.raises(httpx.HTTPStatusError):
        await create_document(
            title="",
            content="test document content",
        )
