# ۴. تسک‌ها و خروجی ساختاریافته

`Task` واحد کار شماست: یک توصیف متنی، به‌همراه ابزارها، پارامترها و قالب خروجی دلخواه.

## ساخت تسک

امضای واقعی `Task` در `src/upsonic/tasks/tasks.py`: پارامتر اول `description` است و سپس `attachments`, `tools`, `skills`, `response_format`, `context`, `response_lang`, `guardrail`, `enable_cache` و گزینه‌های جستجوی برداری.

```python
from upsonic import Task

task = Task(
    description="Write a summary of the given article",
    tools=[search_tool, summarize_tool],   # ابزارهای مجاز برای این تسک
    response_format=MySchema,              # خروجی ساختاریافته (اختیاری)
    attachments=["article.pdf"],           # فایل‌های پیوست (متن/تصویر استخراج می‌شود)
    context="...extra context...",         # زمینه اضافه
    guardrail=my_validator,                # تابع اعتبارسنجی خروجی + guardrail_retries
    enable_cache=True,                     # کش نتیجه تسک
)
```

### پارامترهای مفید دیگر

| پارامتر | توضیح |
|---------|-------|
| `response_lang` | زبان پاسخ مورد نظر (مثلاً `"fa"` برای فارسی) |
| `skills` | مهارت‌های قابل استفاده در تسک |
| `vector_search_top_k`, `vector_search_alpha`, `vector_search_filter` | تنظیمات retrieval پایگاه دانش |
| `query_knowledge_base` | فعال/غیرفعال کردن پرس‌وجوی KB (پیش‌فرض True) |
| `policy_apply_to_*` | اعمال سیاست‌های ایمنی روی توصیف/context/خروجی ابزارها |

### انتقال داده در توصیف

برای تزریق داده به تسک، از `context` (رشته آماده) یا `attachments` (مسیر فایل‌ها) استفاده کنید:

```python
task = Task(
    description="Give investment advice with this budget in context",
    context=f"Ticker: AAPL, Budget: 10000 USD",
)
```

## خروجی ساختاریافته (Pydantic)

اگر `response_format` را روی یک کلاس Pydantic بگذارید، پاسخ عامل به آن اسکیما تبدیل می‌شود:

```python
from pydantic import BaseModel
from upsonic import Agent, Task

class Weather(BaseModel):
    temperature: float
    condition: str
    humidity: int

task = Task(description="Tell me about weather in Paris", response_format=Weather)
response = agent.do(task)
weather: Weather = response.result
print(weather.temperature)
```

پیش‌فرض `response_format` برابر `str` است.

## کلاس‌به‌عنوان-تسک (Class-based Tasks)

می‌توانید کل منطق تسک را در یک زیرکلاس از `Task` بنویسید:

```python
from upsonic.tasks.tasks import Task

class StockReportTask(Task):
    def __init__(self, ticker: str):
        super().__init__(
            description=f"Create a full report for {ticker}",
            response_format=ReportSchema,
        )
        self.ticker = ticker
```

## زنجیره تسک‌ها (Sequential Tasks)

خروجی یک تسک را به‌عنوان context تسک بعدی استفاده کنید:

```python
t1 = Task(description="Find top 3 AI startups")
r1 = agent.do(t1)
t2 = Task(description="Write an email to these companies", context=str(r1.result))
agent.do(t2)
```

## Guardrails (گاردیل)

با پارامتر `guardrail` یک تابع اعتبارسنجی به تسک بدهید تا خروجی قبل از پذیرش بررسی شود و در صورت رد شدن، تا `guardrail_retries` بار دوباره تلاش گردد:

```python
def must_be_json(text: str) -> bool:
    return text.strip().startswith("{")

task = Task(description="...", guardrail=must_be_json, guardrail_retries=2)
```

## Response

نتیجه اجرا یک شیء `Response` است:

| فیلد | توضیح |
|------|-------|
| `result` | خروجی نهایی (متن یا نمونه Pydantic) |
| `cost` | هزینه مصرف مدل |
| `usage` | آمار توکن‌ها (register در `usage_registry`) |
| `history` | تاریخچه فراخوانی ابزارها |

## نکات

- توصیف واضح و مرحله‌به‌مرحله کیفیت خروجی را به‌شدت بالا می‌برد.
- برای داده‌های حساس مالی، حتماً از `response_format` استفاده کنید تا خروجی قابل اتکا و type-safe باشد.
- از `ReliabilityLayer` برای بازتلاش خودکار در صورت نامطابقت خروجی با اسکیما استفاده کنید (بخش ۱۰).

## لینک‌های مرتبط

- [۳. عامل سنتی](03-traditional-agent.md)
- [۵. ابزارها و MCP](05-tools-mcp.md)
- [۱۰. ایمنی و ارزیابی](10-safety-eval.md)
