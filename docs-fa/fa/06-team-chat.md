# ۶. تیم، گفتگو و حافظه

## Team (تیم عوامل)

وقتی یک عامل کافی نیست، چند عامل را در یک `Team` سازماندهی کنید (`src/upsonic/team`). هر عضو نقش خودش را دارد و تیم تسک را بین اعضا توزیع می‌کند.

```python
from upsonic import Agent, Task
from upsonic.team import Team

researcher = Agent(model="anthropic/claude-sonnet-4-5", name="Researcher")
analyst   = Agent(model="openai/gpt-4o", name="Analyst")
writer    = Agent(model="anthropic/claude-sonnet-4-5", name="Writer")

# حالت‌های تیم: "sequential" (پشت‌سرهم)، "coordinate" (با رهبر) و "route" (با مسیریاب)
team = Team(entities=[researcher, analyst, writer], name="Market Desk", mode="sequential")

task = Task(description="Produce a weekly crypto market report")
team.print_do(task)
```

پارامترهای کلیدی `Team`: `entities` (عامل‌ها یا تیم‌های تودرتو)، `mode`، `leader` (در حالت coordinate)، `router` (در حالت route)، `ask_other_team_members`، `memory`، `skills` و `tasks`.

کاربردهای تیم در فین‌تک: تیم تحلیل سبد سهام (عامل داده‌جمع‌کن + عامل ریسک + عامل گزارش‌نویس).

## Chat (گفتگو)

`Chat` یک مکالمه stateful با یک عامل است (`src/upsonic/chat`). امضای واقعی: `Chat(session_id, user_id, agent)` — شناسه نشست و کاربر الزامی‌اند:

```python
from upsonic import Agent, Task
from upsonic.chat import Chat

agent = Agent(model="anthropic/claude-sonnet-4-5", name="Assistant")
chat = Chat(session_id="s1", user_id="u1", agent=agent)

chat.print_do(Task("Hello, who are you?"))
chat.print_do(Task("What did I ask before?"))  # تاریخچه همان نشست حفظ می‌شود
```

- تاریخچه پیام‌ها بر اساس `session_id`/`user_id` ذخیره و بازیابی می‌شود.
- گزینه‌های حافظه: `full_session_memory`, `summary_memory`, `user_analysis_memory`.
- مدیریت طول context با `context_management` روی خود Agent انجام می‌شود.

## Session (نشست‌ها)

`Session` تمام چت‌ها، تسک‌ها، رویدادها و متریک‌ها را برای بازیابی و دیباگ ثبت می‌کند (`src/upsonic/session`). این قابلیت پایه ابزار CLI پروژه است:

```bash
upsonic sessions list      # مشاهده نشست‌های ذخیره‌شده
```

## Memory (حافظه بلندمدت)

ماژول `src/upsonic/memory` شیء `Memory` را فراهم می‌کند که با پارامتر `memory=` به Agent داده می‌شود تا ترجیحات کاربر و واقعیات کلیدی بین جلسات باقی بمانند.

## Knowledge Base و RAG

برای پرس‌وجو از اسناد خودتان، از `KnowledgeBase` استفاده کنید (جزئیات در [بخش ۸](08-memory-rag.md)).

## Graph / Workflow

برای ارکستراسیون دقیق‌تر (DAG مراحل)، ماژول‌های `graph` و `graphv2` جریان کار چندمرحله‌ای با شرط‌ها و حلقه‌ها را ارائه می‌دهند:

```text
src/upsonic/graph/    # نسخه اول گراف اجرا
src/upsonic/graphv2/  # نسخه دوم با API مدرن‌تر
src/upsonic/run/      # موتور اجرای workflow
```

## Culture

ماژول `culture` دانش مشترک تیمی (قواعد، لحن، استانداردهای سازمانی) را بین عوامل منتشر می‌کند تا رفتار یکدست بماند.

## لینک‌های مرتبط

- [۳. عامل سنتی](03-traditional-agent.md)
- [۸. حافظه، RAG و پایگاه دانش](08-memory-rag.md)
