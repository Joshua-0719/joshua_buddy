import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Note(Base):
    __tablename__ = 'notes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    transcription_text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    duration_seconds = Column(Float, default=0.0)
    source_app = Column(String, nullable=True)
    
    is_starred = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    tags = Column(String, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.transcription_text,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "duration": self.duration_seconds,
            "is_starred": self.is_starred
        }
