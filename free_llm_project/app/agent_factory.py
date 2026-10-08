"""Assemble the full agent: proxy model (auto) + memory + RAG + tools + skills.

The single entry point used by main.py and the test-suite. All heavy wiring
happens here so the CLI/tests stay tiny.
"""

from __future__ import annotations

import time
from typing import Optional

from upsonic import Agent, Task

from app.database import db
from app.errors import retry_call
from app.memory import build_memory
from app.rag import build_knowledge_base
from app.skills import build_skills
from app.tools import get_custom_tools
from config.settings import apply_env, settings

apply_env()


def build_agent(with_rag: bool = True, with_skills: bool = True,
                session_id: Optional[str] = None) -> Agent:
    """Create the fully-wired assistant agent."""
    kb = build_knowledge_base() if with_rag else None
    agent = Agent(
        f"openai/{settings.proxy.model}",          # openai/auto -> proxy router
        description=(
            "You are Acme's in-house analyst assistant. Use the knowledge base "
            "for factual questions about Acme products, pricing, financials and "
            "security policy. Use tools for math/time/conversions. Follow the "
            "relevant skill format when writing reports or memos. Answer in the "
            "user's language."
        ),
        tools=get_custom_tools(),
        memory=build_memory(session_id=session_id),
        knowledge=[kb] if kb is not None else None,
        skills=build_skills() if with_skills else None,
    )
    return agent


def ask(agent: Agent, prompt: str, **task_kwargs) -> str:
    """Run one task through the agent with retry + audit logging."""
    t0 = time.time()
    task = Task(prompt, **task_kwargs)

    def _run():
        results = agent.run(task)
        r = results[0] if isinstance(results, list) else results
        return r.content if hasattr(r, "content") else str(r)

    try:
        out = retry_call(_run, what="agent.run")
        db.log_event("chat", session_id=settings.memory.session_id,
                     model=settings.proxy.model, duration_s=time.time() - t0,
                     detail={"prompt": prompt[:400], "answer": out[:400]})
        return out
    except Exception as exc:
        db.log_event("chat", session_id=settings.memory.session_id,
                     model=settings.proxy.model, duration_s=time.time() - t0,
                     success=False, detail={"error": str(exc)[:300]})
        raise
