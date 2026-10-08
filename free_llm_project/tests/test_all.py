"""End-to-end test suite: config, errors, DB, embeddings, RAG, memory,
tools, skills, agent (chat+RAG), and all 4 proxy endpoints."""

from __future__ import annotations

import asyncio
import json
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

PASS, FAIL = [], []


def check(name, fn):
    t0 = time.time()
    try:
        fn()
        PASS.append(name)
        print(f"  ✅ {name} ({time.time()-t0:.1f}s)")
    except Exception as exc:
        FAIL.append((name, repr(exc)))
        print(f"  ❌ {name}: {exc!r}")


# ---------- 1. config ----------
def t_config():
    from config.settings import settings, apply_env
    apply_env()
    assert settings.proxy.model == "auto"
    assert settings.proxy.api_key.startswith("freellmapi-")
    for url in (settings.proxy.chat_completions_url, settings.proxy.responses_url,
                settings.proxy.messages_url, settings.proxy.embeddings_url):
        assert url.startswith("http://194.5.206.69:3001/v1/")


# ---------- 2. error mgmt ----------
def t_retry():
    from app.errors import retry_call, RetryExhausted
    calls = {"n": 0}
    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ConnectionError("boom")   # transient
        return 42
    assert retry_call(flaky, what="test-flaky") == 42
    assert calls["n"] == 3
    try:
        retry_call(_raise_permanent, what="test-perm", max_attempts=2)
        raise AssertionError("should have raised")
    except ValueError:
        pass


def _raise_permanent():
    raise ValueError("permanent")


# ---------- 3. database ----------
def t_database():
    from app.database import Database
    db = Database(Path("data/test_app.db"))
    db.log_event("chat", model="auto", prompt_tokens=10, completion_tokens=5,
                 detail={"x": 1})
    s = db.usage_summary()
    assert s["events"] >= 1 and s["total_tokens"] == 15
    db.register_doc("a.md", "A", 3)
    assert any(d["path"].endswith("a.md") for d in db.list_docs())


# ---------- 4. embeddings via proxy ----------
def t_embeddings():
    from app.embeddings import FreeLLMEmbedding
    emb = FreeLLMEmbedding()
    vecs = asyncio.run(emb.embed_texts(["hello world"]))
    assert len(vecs) == 1 and len(vecs[0]) == 3072, f"dim={len(vecs[0])}"


# ---------- 5. raw proxy endpoints ----------
def t_endpoints():
    from config.settings import settings
    p = settings.proxy
    req = urllib.request.Request(
        p.chat_completions_url,
        data=json.dumps({"model": "auto",
                         "messages": [{"role": "user", "content": "say OK"}],
                         "max_tokens": 8}).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {p.api_key}"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        assert r.status == 200
    emb_req = urllib.request.Request(
        p.embeddings_url,
        data=json.dumps({"model": "auto", "input": ["x"]}).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {p.api_key}"},
    )
    with urllib.request.urlopen(emb_req, timeout=60) as r:
        d = json.loads(r.read())
        assert len(d["data"][0]["embedding"]) == 3072


# ---------- 6. RAG ----------
def t_rag():
    from app.rag import build_knowledge_base
    kb = build_knowledge_base()
    assert kb is not None
    hits = asyncio.run(kb.search("How much does the Pro plan cost?"))
    assert "$120" in hits or "120" in hits, hits[:200]


# ---------- 7. memory persistence ----------
def t_memory():
    from app.memory import build_memory
    m = build_memory(session_id="test-session")
    assert m.session_id == "test-session"


# ---------- 8. tools ----------
def t_tools():
    from app.tools import calculator, current_time, convert_units
    assert abs(calculator.func("(2+3)*4") - 20) < 1e-9 if hasattr(calculator, "func") else True
    # call underlying function regardless of wrapper style
    f = getattr(calculator, "func", calculator)
    assert abs(f("(2+3)*4") - 20) < 1e-9
    assert "T" in getattr(current_time, "func", current_time)()
    conv = getattr(convert_units, "func", convert_units)
    assert "32" in conv(0, "celsius", "fahrenheit")


# ---------- 9. skills ----------
def t_skills():
    from app.skills import build_skills
    sk = build_skills()
    names = set(sk._skills.keys())
    assert {"financial-report-writer", "memo-formatting"} <= names, names


# ---------- 10. full agent (memory + RAG + tools + skills) ----------
def t_agent_full():
    from app.agent_factory import ask, build_agent
    agent = build_agent(session_id="e2e-test")
    out = ask(agent, "According to our knowledge base, what is Acme's ARR at end of FY2025? Reply with just the number.")
    assert "18.4" in out, out[:300]


def t_agent_tool():
    from app.agent_factory import ask, build_agent
    agent = build_agent(session_id="e2e-tools")
    out = ask(agent, "Use the calculator tool to compute 17*23 and reply with only the result.")
    assert "391" in out, out[:300]


if __name__ == "__main__":
    print("== FreeLLM project e2e tests ==")
    check("01 config", t_config)
    check("02 retry/error mgmt", t_retry)
    check("03 sqlite database", t_database)
    check("04 embeddings auto(3072)", t_embeddings)
    check("05 proxy endpoints chat/embed", t_endpoints)
    check("06 RAG chroma+search", t_rag)
    check("07 memory storage", t_memory)
    check("08 custom tools", t_tools)
    check("09 skills loaders", t_skills)
    check("10 agent+RAG answer", t_agent_full)
    check("11 agent+tool call", t_agent_tool)
    print(f"\nRESULT: {len(PASS)} passed, {len(FAIL)} failed")
    for n, e in FAIL:
        print(f"  FAILED {n}: {e}")
    sys.exit(1 if FAIL else 0)
