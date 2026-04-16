from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text
from src.api.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class LearningStat(Base):
    __tablename__ = "learning_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    documents_processed = Column(Integer, default=0)
    questions_asked = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class DocumentRecord(Base):
    __tablename__ = "document_records"

    document_id = Column(String(50), primary_key=True, index=True) # UUID hex
    filename = Column(String(255))         # Original filename (without UUID prefix)
    file_path = Column(String(512))        # Full filename on disk (with UUID prefix)
    size_bytes = Column(Integer, default=0) # File size in bytes
    total_pages = Column(Integer)
    processing_time_ms = Column(Integer)
    model_used = Column(String(50))
    # Note: Using Text to store the large serialized JSON of DocumentAnalysisResponse
    full_json_response = Column(Text(length=16777215)) # LONGTEXT ~ 16MB limit
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
