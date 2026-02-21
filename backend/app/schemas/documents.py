from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator


class DocumentStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class DocumentCreate(BaseModel):
    title: str
    content: Optional[str] = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title cannot be empty")
        return v


class Document(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    status: DocumentStatus = DocumentStatus.DRAFT
    content: Optional[str] = None

type DocumentList = list[Document]
