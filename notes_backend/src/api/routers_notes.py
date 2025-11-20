"""FastAPI router for Notes CRUD."""

from __future__ import annotations

import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from .repository import InMemoryNoteRepository
from .schemas import Note, NoteCreate, NoteUpdate
from .service import NoteService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notes", tags=["Notes"])


# module-level optional singleton storage
_SERVICE_SINGLETON: NoteService | None = None


def get_service() -> NoteService:
    """Dependency provider for NoteService (singleton-ish for process)."""
    global _SERVICE_SINGLETON
    if _SERVICE_SINGLETON is not None:
        return _SERVICE_SINGLETON
    repo = InMemoryNoteRepository()
    _SERVICE_SINGLETON = NoteService(repo)
    return _SERVICE_SINGLETON


@router.get(
    "",
    summary="List notes",
    description="Retrieve all notes. Optionally supports simple search by title substring.",
    response_model=List[Note],
    status_code=status.HTTP_200_OK,
)
def list_notes(q: str | None = Query(default=None, description="Optional title substring filter"), service: NoteService = Depends(get_service)) -> List[Note]:
    """List notes, with optional simple filtering."""
    notes = service.list_notes()
    if q:
        q_norm = q.strip().lower()
        notes = [n for n in notes if q_norm in n.title.lower()]
    return notes


@router.get(
    "/{note_id}",
    summary="Get a note",
    description="Retrieve a single note by its UUID.",
    response_model=Note,
    status_code=status.HTTP_200_OK,
)
def get_note(note_id: UUID, service: NoteService = Depends(get_service)) -> Note:
    """Get a single note by ID."""
    return service.get_note(note_id)


@router.post(
    "",
    summary="Create a note",
    description="Create a new note with title and content.",
    response_model=Note,
    status_code=status.HTTP_201_CREATED,
)
def create_note(payload: NoteCreate, service: NoteService = Depends(get_service)) -> Note:
    """Create a new note."""
    return service.create_note(payload)


@router.patch(
    "/{note_id}",
    summary="Update a note",
    description="Partially update an existing note.",
    response_model=Note,
    status_code=status.HTTP_200_OK,
)
def update_note(note_id: UUID, payload: NoteUpdate, service: NoteService = Depends(get_service)) -> Note:
    """Update an existing note."""
    return service.update_note(note_id, payload)


@router.delete(
    "/{note_id}",
    summary="Delete a note",
    description="Delete a note by its UUID.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_note(note_id: UUID, service: NoteService = Depends(get_service)) -> None:
    """Delete a note by ID."""
    service.delete_note(note_id)
    return None
