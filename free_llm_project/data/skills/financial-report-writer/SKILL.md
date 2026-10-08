---
name: financial-report-writer
description: Write structured financial reports (quarterly review, P&L summary, budget variance). Use when the user asks for a financial report, earnings summary, or budget analysis. Do NOT use for simple arithmetic or unit conversion.
metadata:
  version: "1.0.0"
  author: free-llm-project
  tags: [finance, writing, reports]
---

# Financial Report Writer

Produce a professional financial report using this exact structure:

## Format
1. **Title block** — report name, period, prepared date (use the current_time tool for the date).
2. **Executive Summary** — 3-5 sentences covering headline numbers and the single most important takeaway.
3. **Key Metrics table** — markdown table with columns: Metric | Current | Prior | Change (%).
4. **Analysis** — short sections explaining revenue, costs, and margin drivers. Reference the knowledge base when company-specific data exists there.
5. **Risks & Outlook** — bullet list.
6. **Recommendations** — max 3 actionable items.

## Rules
- Never invent numbers; if data is missing, mark it as `[DATA NEEDED]`.
- Round monetary values to whole units and percentages to one decimal.
- Keep the full report under 600 words unless asked otherwise.
