"""Custom Upsonic EmbeddingProvider backed by the FreeLLMAPI proxy.

The proxy exposes an OpenAI-compatible /v1/embeddings endpoint; with
model="auto" it routes to the best available embedding family and returns
3072-dimensional vectors. This class plugs into upsonic's KnowledgeBase /
RAG stack exactly like OpenAIEmbedding does — but always uses "auto".
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI
from pydantic import Field

from upsonic.embeddings.base import EmbeddingConfig, EmbeddingMode, EmbeddingProvider

from config.settings import settings
from app.errors import retry_call


class FreeLLMEmbeddingConfig(EmbeddingConfig):
    """Configuration for the proxy-backed embedding provider."""

    api_key: Optional[str] = None
    base_url: Optional[str] = None
    # The proxy expects model="auto"; skip the base-class validator by
    # overriding the field without validation constraints.
    model_name: str = Field(default=settings.proxy.embedding_model)
    dimension: int = Field(default=settings.proxy.embedding_dim)
    request_timeout: float = Field(default=settings.retry.timeout_seconds)


class FreeLLMEmbedding(EmbeddingProvider):
    """Async embedding provider that talks to the FreeLLMAPI proxy."""

    config: FreeLLMEmbeddingConfig

    def __init__(self, config: Optional[FreeLLMEmbeddingConfig] = None, **kwargs: Any) -> None:
        if config is None:
            config = FreeLLMEmbeddingConfig(**kwargs)
        super().__init__(config=config)
        self.client = AsyncOpenAI(
            api_key=config.api_key or os.getenv("OPENAI_API_KEY") or settings.proxy.api_key,
            base_url=config.base_url or os.getenv("OPENAI_BASE_URL") or settings.proxy.base_url,
            timeout=config.request_timeout,
        )

    async def _embed_batch(
        self, texts: List[str], mode: EmbeddingMode = EmbeddingMode.DOCUMENT
    ) -> List[List[float]]:
        """Embed one batch via the proxy (with retry/backoff on transient errors)."""

        def _call() -> List[List[float]]:
            import asyncio

            async def _run() -> List[List[float]]:
                resp = await self.client.embeddings.create(
                    model=self.config.model_name,  # "auto"
                    input=texts,
                )
                return [item.embedding for item in resp.data]

            # _embed_batch is invoked from async context by the base class,
            # so bridge through a fresh loop only when needed.
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None
            if loop and loop.is_running():
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor(1) as pool:
                    return pool.submit(asyncio.run, _run()).result()
            return asyncio.run(_run())

        return retry_call(_call, what="embeddings(auto)")

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "model_name": self.config.model_name,
            "provider": "FreeLLMAPI proxy",
            "type": "embedding",
            "dimensions": self.config.dimension,
            "max_tokens": 8191,
            "description": "Proxy-routed embeddings, model='auto'",
        }

    @property
    def supported_modes(self) -> List[EmbeddingMode]:
        return [EmbeddingMode.DOCUMENT, EmbeddingMode.QUERY]

    @property
    def pricing_info(self) -> Dict[str, float]:
        return {"per_million_tokens": 0.0, "currency": "USD", "updated": "2026-10-08"}
