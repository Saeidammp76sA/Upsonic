"""Central configuration for the FreeLLMAPI + Upsonic project.

Everything is tunable through environment variables / a local `.env` file.
The proxy is 100% OpenAI-compatible: its API key authenticates every request
and the model is always "auto" (the router picks the best available model).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"

load_dotenv(PROJECT_ROOT / ".env")


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


@dataclass(frozen=True)
class ProxySettings:
    """Credentials & endpoints of the FreeLLMAPI proxy."""

    api_key: str = field(default_factory=lambda: os.getenv(
        "FREE_LLM_API_KEY",
        "freellmapi-dd5eb674960bf7d792609ce354c9e0f481cf82af376bcf08",
    ))
    base_url: str = field(default_factory=lambda: os.getenv(
        "FREE_LLM_BASE_URL", "http://194.5.206.69:3001/v1",
    ))
    model: str = field(default_factory=lambda: os.getenv("FREE_LLM_MODEL", "auto"))
    embedding_model: str = field(default_factory=lambda: os.getenv("FREE_LLM_EMBEDDING_MODEL", "auto"))
    embedding_dim: int = field(default_factory=lambda: _int("FREE_LLM_EMBEDDING_DIM", 3072))

    # Endpoints exposed by the proxy
    @property
    def chat_completions_url(self) -> str:
        return f"{self.base_url}/chat/completions"

    @property
    def responses_url(self) -> str:
        return f"{self.base_url}/responses"

    @property
    def messages_url(self) -> str:
        """Anthropic (Claude)-compatible endpoint."""
        return f"{self.base_url}/messages"

    @property
    def embeddings_url(self) -> str:
        return f"{self.base_url}/embeddings"


@dataclass(frozen=True)
class RetrySettings:
    """Error-management: retry policy applied to every LLM/embedding call."""

    max_attempts: int = field(default_factory=lambda: _int("RETRY_MAX_ATTEMPTS", 4))
    initial_delay: float = field(default_factory=lambda: _float("RETRY_INITIAL_DELAY", 1.0))
    backoff_factor: float = field(default_factory=lambda: _float("RETRY_BACKOFF_FACTOR", 2.0))
    max_delay: float = field(default_factory=lambda: _float("RETRY_MAX_DELAY", 30.0))
    timeout_seconds: float = field(default_factory=lambda: _float("REQUEST_TIMEOUT", 120.0))
    # HTTP status codes considered transient (worth retrying)
    retry_on_status: tuple = (408, 409, 425, 429, 500, 502, 503, 504)


@dataclass(frozen=True)
class MemorySettings:
    """Conversation-memory configuration."""

    session_id: str = field(default_factory=lambda: os.getenv("SESSION_ID", "default-session"))
    user_id: str = field(default_factory=lambda: os.getenv("USER_ID", "default-user"))
    full_session_memory: bool = field(default_factory=lambda: os.getenv("MEMORY_FULL", "1") == "1")
    summary_memory: bool = field(default_factory=lambda: os.getenv("MEMORY_SUMMARY", "1") == "1")
    user_analysis_memory: bool = field(default_factory=lambda: os.getenv("MEMORY_USER_ANALYSIS", "0") == "1")
    num_last_messages: int = field(default_factory=lambda: _int("MEMORY_LAST_MESSAGES", 20))
    feed_tool_call_results: bool = field(default_factory=lambda: os.getenv("MEMORY_FEED_TOOL_RESULTS", "1") == "1")


@dataclass(frozen=True)
class RagSettings:
    """RAG / knowledge-base configuration."""

    knowledge_dir: Path = DATA_DIR / "knowledge"
    chroma_path: Path = Path(os.getenv("CHROMA_PATH", str(DATA_DIR / "chroma")))
    collection_name: str = field(default_factory=lambda: os.getenv("CHROMA_COLLECTION", "free_llm_kb"))
    top_k: int = field(default_factory=lambda: _int("RAG_TOP_K", 4))
    similarity_threshold: float = field(default_factory=lambda: _float("RAG_SIM_THRESHOLD", 0.0))


@dataclass(frozen=True)
class SkillsSettings:
    """Skills directory configuration."""

    skills_dir: Path = Path(os.getenv("SKILLS_DIR", str(DATA_DIR / "skills")))


@dataclass(frozen=True)
class DatabaseSettings:
    """SQLite application database (audit log, usage stats, RAG registry)."""

    db_file: Path = Path(os.getenv("SQLITE_DB_FILE", str(DATA_DIR / "app.db")))


@dataclass(frozen=True)
class AppSettings:
    proxy: ProxySettings = field(default_factory=ProxySettings)
    retry: RetrySettings = field(default_factory=RetrySettings)
    memory: MemorySettings = field(default_factory=MemorySettings)
    rag: RagSettings = field(default_factory=RagSettings)
    skills: SkillsSettings = field(default_factory=SkillsSettings)
    db: DatabaseSettings = field(default_factory=DatabaseSettings)
    log_dir: Path = LOG_DIR


settings = AppSettings()


def apply_env() -> None:
    """Point standard OpenAI env vars at the proxy.

    Upsonic's `openai` provider reads OPENAI_API_KEY / OPENAI_BASE_URL, so after
    calling this any "openai/..." model string transparently talks to the proxy
    with model="auto".
    """
    os.environ["OPENAI_API_KEY"] = settings.proxy.api_key
    os.environ["OPENAI_BASE_URL"] = settings.proxy.base_url
    os.environ["UPSONIC_LOGS_TO_FILE"] = "false"
