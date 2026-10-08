"""FreeLLMAPI + Upsonic full project — interactive CLI.

Usage:
    python main.py                 # chat loop (memory + RAG + tools + skills)
    python main.py -p "question"   # one-shot prompt
    python main.py --stats         # DB usage summary + recent audit events
    python main.py --docs          # list ingested knowledge documents
    python main.py --ingest FILE   # add a document to the knowledge base
"""

from __future__ import annotations

import argparse
import json
import sys

from app.agent_factory import ask, build_agent
from app.database import db
from app.errors import RetryExhausted
from config.settings import settings


def _banner() -> None:
    p = settings.proxy
    print(f"[proxy] {p.base_url}  model={p.model}  key={p.api_key[:12]}…")
    print("[stack] memory(sqlite) + rag(chroma/auto-embeddings) + tools + skills\n")


def cmd_stats() -> None:
    print(json.dumps(db.usage_summary(), indent=2))
    print("\nrecent events:")
    for e in db.recent_events(10):
        print(f"  {e['ts']} | {e['event']:9s} | ok={e['success']} | {str(e['detail'])[:80]}")


def cmd_docs() -> None:
    for d in db.list_docs():
        print(f"  {d['path']}  ({d['title']})")


def cmd_ingest(path: str) -> None:
    from app.rag import ingest_file
    kb = ingest_file(path)
    print(f"Rebuilt KB with {len(kb.sources)} sources." if kb else "No sources found.")


def chat_loop(one_shot: str | None) -> int:
    _banner()
    agent = build_agent()
    if one_shot:
        try:
            print(ask(agent, one_shot))
        except RetryExhausted as exc:
            print(f"ERROR: {exc}", file=sys.stderr); return 1
        return 0

    print("چت آزاد — exit/quit برای خروج\n")
    while True:
        try:
            user = input("شما > ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if user.lower() in {"exit", "quit"}:
            break
        if not user:
            continue
        try:
            print(f"\nدستیار > {ask(agent, user)}\n")
        except RetryExhausted as exc:
            print(f"خطا (پس از تلاش‌های مجدد): {exc}\n", file=sys.stderr)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Upsonic agent on FreeLLMAPI proxy")
    ap.add_argument("-p", "--prompt", help="one-shot prompt")
    ap.add_argument("--stats", action="store_true", help="usage stats from DB")
    ap.add_argument("--docs", action="store_true", help="list knowledge docs")
    ap.add_argument("--ingest", metavar="FILE", help="add file to knowledge base")
    args = ap.parse_args()

    if args.stats:
        cmd_stats(); return 0
    if args.docs:
        cmd_docs(); return 0
    if args.ingest:
        cmd_ingest(args.ingest); return 0
    return chat_loop(args.prompt)


if __name__ == "__main__":
    raise SystemExit(main())
