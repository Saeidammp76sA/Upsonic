# ۳. عامل سنتی (Traditional Agent)

عامل سنتی، الگوی کلاسیک «LLM + ابزار» است: شما یک `Agent` می‌سازید، برای او `Task` تعریف می‌کنید و ابزارهای مجاز را مشخص می‌نمایید. عامل تصمیم می‌گیرد کدام ابزار را کی صدا بزند و پاسخ نهایی را برمی‌گرداند.

## ساخت عامل

```python
from upsonic import Agent, Task

agent = Agent(
    model="anthropic/claude-sonnet-4-5",
    name="Stock Analyst Agent",
)

task = Task(description="Analyze the current market trends")
agent.print_do(task)
```

پارامترهای مهم `Agent` (بر اساس امضای واقعی `src/upsonic/agent/agent.py`):

| پارامتر | توضیح |
|---------|-------|
| `model` | مدل زبانی؛ فرمت `provider/model` مثل `openai/gpt-4o` یا `ollama/llama3` (پیش‌فرض: `openai/gpt-4o`) |
| `name`, `role`, `goal`, `instructions` | هویت و نقش عامل |
| `system_prompt` | پرامپت سیستمی سفارشی |
| `memory` | شیء `Memory` برای حافظه بلندمدت |
| `db`, `session_id`, `user_id` | ذخیره‌سازی و شناسه نشست/کاربر |
| `reflection` | فعال‌سازی خودبازتاب روی پاسخ‌ها |
| `context_management` + `context_management_keep_recent` | فشرده‌سازی خودکار context گفتگو |
| `reliability_layer` | لایه بازتلاش و اعتبارسنجی خروجی |
| `retry`, `mode` (`RetryMode`) | سیاست تکرار اجرا |
| `company_name/url/objective/description` | زمینه سازمانی برای پرامپت |
| `canvas`, `debug`, `debug_level`, `print` | بصری‌سازی و دیباگ |

## اجرای تسک‌ها

```python
# همگام
response = agent.do(task)
print(response.result)      # نتیجه (متن یا شیء Pydantic)
print(response.cost)        # هزینه تقریبی توکن

# ناهمگام
import asyncio
response = asyncio.run(agent.do_async(task))

# چند تسک با هم
tasks = [Task("Summarize BTC news"), Task("Check ETH price")]
results = agent.do(tasks)   # اجرا به‌صورت موازی
```

## گفتگو (Chat) و تاریخچه

برای مکالمه پیوسته با یک عامل از `Chat` استفاده می‌شود (`src/upsonic/chat`):

```python
from upsonic import Agent, Chat, Task

agent = Agent(model="anthropic/claude-sonnet-4-5", name="Assistant")
chat = Chat(agent=agent)

chat.print_do(Task("Hello, who are you?"))
chat.print_do(Task("What did I ask before?"))  # تاریخچه حفظ می‌شود
```

## Session (نشست)

`Session` مجموعه‌ای از چت‌ها و رویدادها را برای تحلیل و دیباگ ذخیره می‌کند (`src/upsonic/session`). با CLI می‌توان نشست‌های ذخیره‌شده را مرور کرد.

## Deep Agents و Pipeline

در نسخه‌های جدید، ماژول‌های تکمیلی اضافه شده‌اند:

- `src/upsonic/agent/deepagent/` — اجرای چندمرحله‌ای عمیق‌تر با برنامه‌ریزی مجدد
- `src/upsonic/agent/pipeline/` — خط لوله اجرای تسک با مراحل قابل تنظیم
- `src/upsonic/agent/context_managers/` — مدیریت زمینه (context) گفتگو

## مثال عملی: ماشین‌حساب با ابزار سفارشی

```python
from upsonic import Agent, Task
from upsonic.tools import tool

@tool
def sum_tool(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

task = Task(description="Calculate 15 + 27", tools=[sum_tool])
agent = Agent(model="anthropic/claude-sonnet-4-5", name="Calculator Agent")
agent.print_do(task)
```

جزئیات بیشتر ابزارها: [۵. ابزارها و MCP](05-tools-mcp.md)

## لینک‌های مرتبط

- [۴. تسک‌ها و خروجی ساختاریافته](04-tasks-output.md)
- [۶. تیم و گفتگو](06-team-chat.md)
- [۱۱. مدل‌ها و ارائه‌دهنده‌ها](11-models-providers.md)
