"""Pydantic schemas for Notes API."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class NoteBase(BaseModel):
    """Base attributes shared by Note create/update operations."""

    title: str = Field(..., min_length=1, max_length=200, description="Title of the note")
    content: str = Field(
        default="",
        max_length=10000,
        description="Content/body of the note (markdown/plaintext)",
    )

    @field_validator("title")
    @classmethod
    def title_trim_and_validate(cls, v: str) -> str:
        """Trim whitespace and validate non-empty title."""
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Title must not be empty")
        return trimmed

    @field_validator("content")
    @classmethod
    def content_sanitize(cls, v: str) -> str:
        """Basic normalization (trim trailing whitespace)."""
        return v.rstrip()


class NoteCreate(NoteBase):
    """Schema for creating a new note."""

    pass


class NoteUpdate(BaseModel):
    """Schema for partial update of a note."""

    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Updated title")
    content: Optional[str] = Field(None, max_length=10000, description="Updated content")

    @field_validator("title")
    @classmethod
    def title_optional_trim_and_validate(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Title must not be empty when provided")
        return trimmed

    @field_validator("content")
    @classmethod
    def content_optional_trim(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return v.rstrip()


class Note(NoteBase):
    """Schema representing a persisted note."""

    id: UUID = Field(..., description="Unique identifier for the note")
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC)")

    model_config = {
        "json_encoders": {
            UUID: lambda v: str(v),
            datetime: lambda v: v.isoformat(),
        }
    }


# PUBLIC_INTERFACE
def new_note_from_create(payload: NoteCreate) -> Note:
    """Create a new Note model from a NoteCreate payload with generated fields."""
    now = datetime.utcnow()
    return Note(id=uuid4(), title=payload.title, content=payload.content, created_at=now, updated_at=now)
