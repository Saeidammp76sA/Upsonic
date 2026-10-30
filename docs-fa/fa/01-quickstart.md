# ۱. شروع سریع (Quickstart)

## پیش‌نیازها

- پایتون نسخه ۳.۱۰ یا بالاتر (پشتیبانی تا ۳.۱۳)
- یک کلید API از ارائه‌دهنده مدل زبانی (مانند Anthropic یا OpenAI)
- آشنایی مقدماتی با پایتون

## نصب

با استفاده از `uv` (توصیه می‌شود):

```bash
uv pip install upsonic
```

یا با pip:

```bash
pip install upsonic
```

### نصب با قابلیت‌های اختیاری

بر اساس نیاز خود می‌توانید افزونه‌ها را نصب کنید:

```bash
# برای اتصال به ابزارهای MCP
uv pip install "upsonic[mcp]"

# برای موتورهای OCR
uv pip install "upsonic[easyocr]"      # EasyOCR
uv pip install "upsonic[pytesseract]"  # Tesseract
uv pip install "upsonic[paddleocr]"    # PaddleOCR
uv pip install "upsonic[rapidocr]"     # RapidOCR

# برای پایگاه داده برداری ChromaDB
uv pip install "upsonic[chromadb]"

# برای ذخیره‌سازی ابری (Supabase)
uv pip install "upsonic[s3]"
```

## تنظیم کلیدهای API

Upsonic به‌طور خودکار فایل `.env` موجود در پوشه جاری (یا پوشه‌های بالاتر) را بارگذاری می‌کند:

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

## اولین عامل سنتی شما

```python
from upsonic import Agent, Task

# ساخت عامل با مدل Anthropic Claude
agent = Agent(model="anthropic/claude-sonnet-4-5", name="My First Agent")

# تعریف تسک
task = Task(description="What is the capital of Iran?")

# اجرا و چاپ نتیجه
result = agent.print_do(task)
```

روش‌های اجرای تسک:

| روش | توضیح |
|------|--------|
| `agent.do(task)` | اجرای همگام، بازگرداندن شیء `Response` |
| `agent.print_do(task)` | اجرای همگام + چاپ خروجی |
| `await agent.do_async(task)` | اجرای ناهمگام (async) |
| `agent.test_do(task)` | اجرای آزمایشی (بدون مصرف واقعی ابزارها در برخی سناریوها) |

## اولین عامل خودمختار شما

عامل خودمختار می‌تواند فایل بخواند/بنویسد و دستور shell اجرا کند — همه در یک workspace محدود و امن:

```python
from upsonic import AutonomousAgent, Task

agent = AutonomousAgent(
    model="anthropic/claude-sonnet-4-5",
    workspace="/path/to/workspace"
)

task = Task("Analyze server logs and detect anomaly patterns")

agent.print_do(task)
```

> امنیت: تمام عملیات فایل و shell فقط داخل `workspace` مجاز است. تلاش برای خروج از مسیر (Path Traversal) و دستورات خطرناک مسدود می‌شوند.

## تحلیل سهام با چندین تسک (مثال فین‌تک)

```python
from upsonic import Agent, Task
from pydantic import BaseModel

class StockAnalysis(BaseModel):
    ticker: str
    price: float
    recommendation: str  # buy / sell / hold

agent = Agent(model="anthropic/claude-sonnet-4-5", name="Stock Analyst")

task = Task(
    description="Analyze AAPL stock and give a recommendation",
    tools=[...],  # ابزارهای دریافت قیمت، مثلاً از MCP
    response_format=StockAnalysis,
)

response = agent.do(task)
analysis: StockAnalysis = response.result
print(analysis.recommendation)
```

مثال کامل‌تر در notebook پروژه موجود است: `notebooks/stock_report.ipynb`.

## گام‌های بعدی

- [۲. عامل خودمختار](02-autonomous-agent.md)
- [۳. عامل سنتی](03-traditional-agent.md)
- [۵. ابزارها و MCP](05-tools-mcp.md)
- مستندات رسمی: [docs.upsonic.ai](https://docs.upsonic.ai)
