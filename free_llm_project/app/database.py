"""SQLite application database: audit log, usage stats, knowledge registry.

Separate from Upsonic's SqliteStorage (which stores conversation memory);
this module is the project's own relational DB powered by SQLAlchemy and
records every agent interaction for observability & analytics.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
    select,
)
from sqlalchemy.orm import DeclarativeBase, Session

from config.settings import settings


class Base(DeclarativeBase):
    pass


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ts = Column(DateTime, default=datetime.utcnow, index=True)
    event_type = Column(String(64), nullable=False)   # chat | tool | embedding | error | ingest
    actor = Column(String(128), default="user")
    session_id = Column(String(128), nullable=True)
    model = Column(String(128), nullable=True)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    duration_s = Column(Float, default=0.0)
    success = Column(Integer, default=1)
    detail = Column(Text, default="{}")               # JSON blob


class KnowledgeDoc(Base):
    """Registry of documents ingested into the RAG knowledge base."""

    __tablename__ = "knowledge_docs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String(512), unique=True, nullable=False)
    title = Column(String(256), default="")
    chunks = Column(Integer, default=0)
    ingested_at = Column(DateTime, default=datetime.utcnow)


class Database:
    def __init__(self, db_file=None) -> None:
        self.db_file = db_file or settings.db.db_file
        self.db_file.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(f"sqlite:///{self.db_file}", future=True)
        Base.metadata.create_all(self.engine)

    # ---------- writes ----------
    def log_event(
        self,
        event_type: str,
        *,
        actor: str = "user",
        session_id: Optional[str] = None,
        model: Optional[str] = None,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        cost_usd: float = 0.0,
        duration_s: float = 0.0,
        success: bool = True,
        detail: Optional[Dict[str, Any]] = None,
    ) -> None:
        with Session(self.engine) as s:
            s.add(AuditLog(
                event_type=event_type, actor=actor, session_id=session_id, model=model,
                prompt_tokens=prompt_tokens, completion_tokens=completion_tokens,
                cost_usd=cost_usd, duration_s=duration_s,
                success=int(success), detail=json.dumps(detail or {}, ensure_ascii=False),
            ))
            s.commit()

    def register_doc(self, path: str, title: str = "", chunks: int = 0) -> None:
        with Session(self.engine) as s:
            existing = s.scalar(select(KnowledgeDoc).where(KnowledgeDoc.path == str(path)))
            if existing:
                existing.chunks = chunks
                existing.ingested_at = datetime.utcnow()
            else:
                s.add(KnowledgeDoc(path=str(path), title=title, chunks=chunks))
            s.commit()

    # ---------- reads ----------
    def recent_events(self, limit: int = 20) -> List[Dict[str, Any]]:
        with Session(self.engine) as s:
            rows = s.scalars(
                select(AuditLog).order_by(AuditLog.id.desc()).limit(limit)
            ).all()
            return [
                {
                    "ts": r.ts.isoformat() if r.ts else None,
                    "event": r.event_type,
                    "model": r.model,
                    "tokens": (r.prompt_tokens or 0) + (r.completion_tokens or 0),
                    "success": bool(r.success),
                    "detail": r.detail,
                }
                for r in rows
            ]

    def usage_summary(self) -> Dict[str, Any]:
        with Session(self.engine) as s:
            rows = s.scalars(select(AuditLog)).all()
        total_prompt = sum(r.prompt_tokens or 0 for r in rows)
        total_completion = sum(r.completion_tokens or 0 for r in rows)
        errors = sum(1 for r in rows if not r.success)
        return {
            "events": len(rows),
            "prompt_tokens": total_prompt,
            "completion_tokens": total_completion,
            "total_tokens": total_prompt + total_completion,
            "errors": errors,
        }

    def list_docs(self) -> List[Dict[str, Any]]:
        with Session(self.engine) as s:
            rows = s.scalars(select(KnowledgeDoc)).all()
            return [{"path": r.path, "title": r.title, "chunks": r.chunks} for r in rows]


db = Database()
