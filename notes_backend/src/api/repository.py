"""Thread-safe in-memory repository for Note entities."""

from __future__ import annotations

import logging
from datetime import datetime
from threading import RLock
from typing import Dict, List, Optional
from uuid import UUID

from .schemas import Note

logger = logging.getLogger(__name__)


class InMemoryNoteRepository:
    """A simple, thread-safe in-memory repository for notes."""

    def __init__(self) -> None:
        self._items: Dict[UUID, Note] = {}
        self._lock = RLock()

    # PUBLIC_INTERFACE
    def list_notes(self) -> List[Note]:
        """Return a list of all notes."""
        with self._lock:
            return list(self._items.values())

    # PUBLIC_INTERFACE
    def get_note(self, note_id: UUID) -> Optional[Note]:
        """Get a note by ID, or None if not found."""
        with self._lock:
            return self._items.get(note_id)

    # PUBLIC_INTERFACE
    def create_note(self, note: Note) -> Note:
        """Persist a new Note."""
        with self._lock:
            self._items[note.id] = note
            logger.debug("Note created in repository: %s", note.id)
            return note

    # PUBLIC_INTERFACE
    def update_note(self, note_id: UUID, title: Optional[str], content: Optional[str]) -> Optional[Note]:
        """Update fields of an existing Note, returning the updated Note or None if not found."""
        with self._lock:
            existing = self._items.get(note_id)
            if not existing:
                return None
            updated_title = existing.title if title is None else title
            updated_content = existing.content if content is None else content
            updated = Note(
                id=existing.id,
                title=updated_title,
                content=updated_content,
                created_at=existing.created_at,
                updated_at=datetime.utcnow(),
            )
            self._items[note_id] = updated
            logger.debug("Note updated in repository: %s", note_id)
            return updated

    # PUBLIC_INTERFACE
    def delete_note(self, note_id: UUID) -> bool:
        """Delete note by ID. Returns True if deleted, False if not found."""
        with self._lock:
            if note_id in self._items:
                del self._items[note_id]
                logger.debug("Note deleted in repository: %s", note_id)
                return True
            return False
