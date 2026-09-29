import os
import datetime
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, Note

class DBManager:
    """Manages the SQLite connection and provides CRUD operations for notes."""
    
    def __init__(self, db_dir=None):
        if db_dir is None:
            # Default to ~/Library/Application Support/JoshuasNotes/
            self.db_dir = Path.home() / "Library" / "Application Support" / "JoshuasNotes"
        else:
            self.db_dir = Path(db_dir)
            
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.db_dir / "notes.sqlite"
        
        # Initialize SQLAlchemy
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_note(self, text: str, duration: float = 0.0, source_app: str = None) -> Note:
        """Add a new transcription note."""
        session = self.Session()
        try:
            note = Note(
                transcription_text=text,
                duration_seconds=duration,
                source_app=source_app
            )
            session.add(note)
            session.commit()
            session.refresh(note)
            return note
        finally:
            session.close()

    def get_all_notes(self):
        """Retrieve all non-deleted notes, newest first."""
        session = self.Session()
        try:
            notes = session.query(Note)\
                .filter_by(is_deleted=False)\
                .order_by(Note.created_at.desc())\
                .all()
            return [n.to_dict() for n in notes]
        finally:
            session.close()

    def delete_note(self, note_id: int):
        """Soft-delete a note."""
        session = self.Session()
        try:
            note = session.query(Note).get(note_id)
            if note:
                note.is_deleted = True
                note.deleted_at = datetime.datetime.utcnow()
                session.commit()
        finally:
            session.close()

    def toggle_star(self, note_id: int) -> bool:
        """Toggle the starred status of a note."""
        session = self.Session()
        try:
            note = session.query(Note).get(note_id)
            if note:
                note.is_starred = not note.is_starred
                session.commit()
                return note.is_starred
            return False
        finally:
            session.close()
