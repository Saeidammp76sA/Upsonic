"""RAG stack: ChromaDB vector store + proxy embeddings (model="auto").

Knowledge sources are plain files under data/knowledge/. The KnowledgeBase is
exposed to the agent as a retrieval *tool*, and documents ingested are
registered in the app database for observability.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from upsonic.knowledge_base import KnowledgeBase
from upsonic.vectordb.config import ChromaConfig, ConnectionConfig, Mode
from upsonic.vectordb.providers.chroma import ChromaProvider

from app.database import db
from app.embeddings import FreeLLMEmbedding
from config.settings import settings


def _chroma_provider() -> ChromaProvider:
    cfg = settings.rag
    cfg.chroma_path.mkdir(parents=True, exist_ok=True)
    return ChromaProvider(config=ChromaConfig(
        vector_size=settings.proxy.embedding_dim,   # 3072 for model="auto"
        connection=ConnectionConfig(mode=Mode.EMBEDDED, db_path=str(cfg.chroma_path)),
    ))


def build_knowledge_base(sources: Optional[List[Path]] = None) -> Optional[KnowledgeBase]:
    """Create (and index) a KnowledgeBase over data/knowledge/*."""
    cfg = settings.rag
    if sources is None:
        sources = sorted(
            p for p in cfg.knowledge_dir.glob("*")
            if p.is_file() and p.suffix.lower() in {".md", ".txt"}
        )
    if not sources:
        return None

    kb = KnowledgeBase(
        name="project_docs",
        description=(
            "Project knowledge base: product documentation, policies and "
            "reference material. Search it before answering factual questions."
        ),
        sources=[str(p) for p in sources],
        vectordb=_chroma_provider(),
        embedding_provider=FreeLLMEmbedding(),
    )
    for p in sources:
        db.register_doc(path=str(p), title=p.stem)
    return kb


def ingest_file(path: Path) -> KnowledgeBase:
    """Add one document to the knowledge dir and rebuild the KB."""
    path = Path(path)
    dest = settings.rag.knowledge_dir / path.name
    if dest != path.resolve():
        dest.write_bytes(path.read_bytes())
    return build_knowledge_base()
