import pytest
from typing import AsyncGenerator

from backend.app.schemas.documents import DocumentStatus
from backend.tests.documents_api.helpers import create_document, delete_documents, get_document_list


@pytest.fixture
async def created_documents() -> AsyncGenerator[list[dict], None]:
    docs = []
    for i in range(3):
        doc = await create_document(
            title=f"test document title {i}",
            content=f"test document content {i}",
        )
        docs.append(doc)

    yield docs

    await delete_documents([doc["id"] for doc in docs])


async def test_get_document_list(created_documents: list[dict]):
    result = await get_document_list()

    assert isinstance(result, list)
    assert len(result) >= len(created_documents)

    result_ids = {doc["id"] for doc in result}
    for created in created_documents:
        assert created["id"] in result_ids, f"Created document {created['id']} missing from list"

    for doc in result:
        assert isinstance(doc["id"], int)
        assert isinstance(doc["title"], str)
        assert isinstance(doc["content"], str)
        assert doc["status"] in [s.value for s in DocumentStatus]
