"""Conversation memory built on Upsonic Memory + SqliteStorage.

Persists full session history (and optionally summaries) in data/memory.db
so the agent remembers context across restarts. Configuration lives in
config/settings.py -> MemorySettings (MEMORY_FULL / MEMORY_SUMMARY / ...).
"""

from __future__ import annotations

from typing import Optional

from upsonic.memory import Memory
from upsonic.storage.sqlite import SqliteStorage

from config.settings import DATA_DIR, settings


def get_storage() -> SqliteStorage:
    """Dedicated SQLite storage for conversation memory."""
    return SqliteStorage(db_file=str(DATA_DIR / "memory.db"))


def build_memory(
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Memory:
    cfg = settings.memory
    return Memory(
        storage=get_storage(),
        session_id=session_id or cfg.session_id,
        user_id=user_id or cfg.user_id,
        full_session_memory=cfg.full_session_memory,
        summary_memory=cfg.summary_memory,
        user_analysis_memory=cfg.user_analysis_memory,
        num_last_messages=cfg.num_last_messages,
        feed_tool_call_results=cfg.feed_tool_call_results,
    )
