---
name: memo-formatting
description: Format internal business memos (TO/FROM/DATE/SUBJECT) with clear action items. Use when the user asks to write, draft, or format a memo or announcement email. Do NOT use for financial reports or essays.
metadata:
  version: "1.0.0"
  author: free-llm-project
  tags: [writing, business, communication]
---

# Memo Formatting

## Structure
```
MEMORANDUM
TO:      <recipients>
FROM:    <sender>
DATE:    <YYYY-MM-DD>            # obtain via the current_time tool
SUBJECT: <one-line subject>

1. Purpose        — why this memo exists (1 sentence)
2. Background     — minimal context (max 3 bullets)
3. Details        — the core message
4. Action Items   — numbered, each with an owner and deadline
```

## Rules
- Tone: neutral-professional, no marketing language.
- Every action item must have an explicit owner ("@team" allowed).
- Total length ≤ 250 words.
