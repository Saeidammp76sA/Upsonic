# ۱۰. ایمنی، قابلیت اتکا و ارزیابی

Upsonic برای استفاده production — خصوصاً در فین‌تک که اشتباه هزینه مالی دارد — چند لایه حفاظتی دارد.

## SafetyEngine (`src/upsonic/safety_engine`)

موتور سیاست‌گذاری ایمنی که ورودی‌ها، خروجی‌ها و عملیات عامل را بررسی می‌کند:

- بلاک کردن دستورات shell خطرناک در عامل خودمختار
- جلوگیری از Path Traversal خارج از workspace
- محافظت SSRF (`_ssrf.py`) در برابر درخواست‌های شبکه مخرب
- سیاست‌های سطح ابزار (Policy Manager در `agent/policy_manager.py`)

## ReliabilityLayer (`src/upsonic/reliability_layer`)

لایه‌ای که کیفیت خروجی مدل را تضمین می‌کند:

- اعتبارسنجی خروجی با `response_format` (Pydantic)
- بازتلاش خودکار با اصلاح پیام خطای validation
- محدودیت تعداد تلاش برای کنترل هزینه

مثال:

```python
from upsonic.reliability_layer.base import ReliabilityLayer

agent = Agent(
    model="anthropic/claude-sonnet-4-5",
    reliability_layer=ReliabilityLayer(max_retries=3),
)
```

## Reflection (`src/upsonic/reflection`)

عامل پس از تولید پاسخ، آن را بازبینی و در صورت لزوم اصلاح می‌کند. این چرخه «تولید → خودنقد → اصلاح» را برای تسک‌های پیچیده فعال کنید.

## Eval (`src/upsonic/eval`)

قابلیت‌های ارزیابی کمّی رفتار عامل:

- تعریف مجموعه تست/سنجه برای تسک‌ها
- مقایسه نسخه‌های مختلف prompt و model
- گزارش‌گیری برای CI

## HITL (انسان در حلقه)

در `tools/hitl.py`: قبل از اجرای ابزارهای حساس (مثلاً انتقال وجه یا ثبت سفارش) از کاربر تأیید می‌گیرد. الگوی پیشنهادی برای تمام عملیات write در فین‌تک.

## Usage Registry (`src/upsonic/usage_registry`)

ثبت متمرکز مصرف توکن و هزینه به تفکیک agent/task/model — پایه بودجه‌بندی و هشدار هزینه.

## Otel و Observability

ماژول `agent/otel_manager.py` پشتیبانی OpenTelemetry برای tracing اضافه کرده است؛ رویدادها در `agent/events.py` ثبت و در Session قابل مرورند.

## توصیه‌های عملیاتی

1. همیشه برای تسک‌های مالی `response_format` + `ReliabilityLayer` داشته باشید.
2. HITL را برای ابزارهای پولی اجباری کنید.
3. با `usage_registry` سقف هزینه هر agent را پایش کنید.
4. قبل از deploy، مجموعه `eval` را در CI اجرا کنید.
5. فایل `SECURITY.md` ریپو را برای گزارش آسیب‌پذیری بخوانید.

## لینک‌های مرتبط

- [۵. ابزارها و MCP](05-tools-mcp.md)
- [۹. معماری و ساختار کد](09-architecture.md)
