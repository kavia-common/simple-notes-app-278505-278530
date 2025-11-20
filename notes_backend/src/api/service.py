"""Service layer for business logic and validation around Notes."""

from __future__ import annotations

import logging
from typing import List
from uuid import UUID

from fastapi import HTTPException, status

from .repository import InMemoryNoteRepository
from .schemas import Note, NoteCreate, NoteUpdate, new_note_from_create

logger = logging.getLogger(__name__)


class NoteService:
    """Service providing validated CRUD operations for notes."""

    def __init__(self, repo: InMemoryNoteRepository) -> None:
        self._repo = repo

    # PUBLIC_INTERFACE
    def list_notes(self) -> List[Note]:
        """Return all notes."""
        notes = self._repo.list_notes()
        logger.debug("Listing %d notes", len(notes))
        return notes

    # PUBLIC_INTERFACE
    def get_note(self, note_id: UUID) -> Note:
        """Return a single note or raise 404 if not found."""
        note = self._repo.get_note(note_id)
        if not note:
            logger.info("Note not found: %s", note_id)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
        return note

    # PUBLIC_INTERFACE
    def create_note(self, payload: NoteCreate) -> Note:
        """Validate and create a new note."""
        note = new_note_from_create(payload)
        created = self._repo.create_note(note)
        logger.info("Note created: %s", created.id)
        return created

    # PUBLIC_INTERFACE
    def update_note(self, note_id: UUID, payload: NoteUpdate) -> Note:
        """Validate and update an existing note."""
        updated = self._repo.update_note(note_id, title=payload.title, content=payload.content)
        if not updated:
            logger.info("Update attempted on missing note: %s", note_id)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
        logger.info("Note updated: %s", note_id)
        return updated

    # PUBLIC_INTERFACE
    def delete_note(self, note_id: UUID) -> None:
        """Delete note or raise 404 if not found."""
        ok = self._repo.delete_note(note_id)
        if not ok:
            logger.info("Delete attempted on missing note: %s", note_id)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
        logger.info("Note deleted: %s", note_id)
