# مستندات فارسی Upsonic

به مستندات فارسی فریم‌ورک **Upsonic** خوش آمدید. Upsonic یک فریم‌ورک پایتون برای ساخت **عامل‌های هوشمند (AI Agents)** است که هم از عامل‌های خودمختار (Autonomous) و هم از عامل‌های سنتی ابزارمحور (Traditional) پشتیبانی می‌کند و تمرکز ویژه‌ای بر حوزه **فین‌تک** دارد.

> نسخه: 0.77.3 | مجوز: MIT | وب‌سایت مستندات انگلیسی: [docs.upsonic.ai](https://docs.upsonic.ai)

## فهرست مطالب

| بخش | توضیح |
|------|--------|
| [۱. شروع سریع](fa/01-quickstart.md) | نصب، راه‌اندازی اولیه و اولین عامل شما |
| [۲. عامل خودمختار](fa/02-autonomous-agent.md) | ساخت عامل‌هایی با دسترسی فایل و shell در workspace امن |
| [۳. عامل سنتی](fa/03-traditional-agent.md) | Agent، Task و اجرای تسک‌ها |
| [۴. تسک‌ها و خروجی ساختاریافته](fa/04-tasks-output.md) | تعریف تسک، پارامترها و پاسخ‌های Pydantic |
| [۵. ابزارها و MCP](fa/05-tools-mcp.md) | ابزارهای سفارشی، داخلی و اتصال به سرویس‌های خارجی |
| [۶. تیم و گفتگو](fa/06-team-chat.md) | همکاری چند عامل، حافظه و Session |
| [۷. OCR و پردازش سند](fa/07-ocr.md) | لوله OCR چندلایه و موتورهای پشتیبانی‌شده |
| [۸. حافظه، RAG و پایگاه دانش](fa/08-memory-rag.md) | KnowledgeBase، VectorDB و Embeddings |
| [۹. معماری و ساختار کد](fa/09-architecture.md) | نقشه ماژول‌های `src/upsonic` |
| [۱۰. ایمنی و ارزیابی](fa/10-safety-eval.md) | SafetyEngine، ReliabilityLayer، Reflection و Eval |
| [۱۱. مدل‌ها و ارائه‌دهنده‌ها](fa/11-models-providers.md) | Anthropic، OpenAI، Ollama و غیره |
| [۱۲. توسعه و مشارکت](fa/12-contributing.md) | محیط توسعه، تست‌ها و نحوه مشارکت |

## شروع سریع در یک نگاه

```python
from upsonic import Agent, Task

agent = Agent(model="anthropic/claude-sonnet-4-5", name="Stock Analyst Agent")
task = Task(description="Analyze the current market trends")

agent.print_do(task)
```

نصب:

```bash
uv pip install upsonic
# یا: pip install upsonic
```

## راهنمای مطالعه

- اگر تازه‌کار هستید: از [شروع سریع](fa/01-quickstart.md) شروع کنید.
- اگر می‌خواهید عاملی با دسترسی به فایل و ترمینال بسازید: [عامل خودمختار](fa/02-autonomous-agent.md).
- اگر با اسناد مالی (فاکتور، صورتحساب) کار می‌کنید: [OCR](fa/07-ocr.md).
- اگر توسعه‌دهنده هسته پروژه هستید: [معماری](fa/09-architecture.md).

## سلب مسئولیت

این مستندات ترجمه/بازنویسی فارسی مستندات رسمی است. برای اطمینان از تطابق با آخرین نسخه API، به [مستندات رسمی](https://docs.upsonic.ai) مراجعه کنید.
