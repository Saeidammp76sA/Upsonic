# ۵. ابزارها و MCP

ابزارها دست‌های عامل شما هستند: با آن‌ها داده می‌گیرید، عملیات انجام می‌دهید و به دنیای بیرون متصل می‌شوید.

## انواع ابزار در Upsonic

| نوع | منبع کد | توضیح |
|-----|---------|-------|
| ابزار سفارشی (Python) | `@tool` در `upsonic.tools` | تابع پایتونی که با دکوریتور تبدیل به ابزار می‌شود |
| ابزار داخلی (Built-in) | `src/upsonic/tools/builtin_tools.py` | ابزارهای آماده مثل وب‌سرچ و فایل |
| ابزار MCP | `src/upsonic/tools/mcp.py` | اتصال به سرورهای Model Context Protocol |
| ابزارهای یکپارچه | `src/upsonic/integrations` | سرویس‌های آماده (مثل Gmail، GitHub و...) |

## تعریف ابزار سفارشی با `@tool`

```python
from upsonic.tools import tool

@tool
def get_stock_price(ticker: str) -> float:
    """
    Fetch the latest price of a stock by its ticker symbol.

    Args:
        ticker: Stock ticker, e.g. "AAPL"

    Returns:
        Latest price in USD
    """
    ...  # فراخوانی API مالی مورد نظر
    return 195.4
```

نکات:
- **Docstring مهم است:** مدل از توضیحات برای تصمیم‌گیری استفاده می‌کند؛ حتماً بنویسید ابزار چه می‌کند.
- **Type hints الزامی است:** ورودی/خروجی برای ساخت JSON Schema استفاده می‌شود (`schema.py`).
- سپس ابزار را به تسک بدهید: `Task(description=..., tools=[get_stock_price])`.

## ابزار MCP (Model Context Protocol)

MCP یک پروتکل استاندارد برای اتصال مدل‌ها به منابع بیرونی است. با نصب افزونه:

```bash
uv pip install "upsonic[mcp]"
```

کلاس‌های اصلی در `src/upsonic/tools/mcp.py` عبارتند از: `MCPHandler` (اتصال به یک سرور)، `MultiMCPHandler` (چند سرور هم‌زمان) و `MCPTool` (نماینده هر ابزار سرور).

### اتصال به سرور MCP محلی با stdio

```python
from upsonic import Agent, Task
from upsonic.tools.mcp import MCPHandler

fs_handler = MCPHandler(
    command="npx -y @modelcontextprotocol/server-filesystem /tmp",
    transport="stdio",
)

agent = Agent(model="anthropic/claude-sonnet-4-5", mcp_tools=[fs_handler])
agent.print_do(Task("List files in /tmp"))
```

### اتصال به سرور MCP از راه دور (SSE / Streamable HTTP)

```python
from upsonic.tools.mcp import MCPHandler, SSEClientParams

remote = MCPHandler(
    url="https://mcp.example.com/sse",
    transport="sse",
    server_params=SSEClientParams(url="https://mcp.example.com/sse"),
)
```

پارامترهای مفید `MCPHandler`: `include_tools` / `exclude_tools` (فیلتر ابزارها)، `tool_name_prefix` (پیشوند نام برای جلوگیری از تداخل)، `timeout_seconds` و `env`.

> با ابزارهای MCP به هزاران سرویس خارجی (دیتابیس، مرورگر، ایمیل، کریپتو و...) متصل شوید بدون اینکه کد بنویسید.

## اجرای ابزار و HITL (انسان در حلقه)

ماژول `src/upsonic/tools/hitl.py` امکان تأیید انسانی قبل از اجرای ابزارهای حساس را فراهم می‌کند — مناسب عملیات مالی مانند ارسال سفارش خرید/فروش.

## سیاست ابزارها (Tool Policy)

در `src/upsonic/agent/tool_policy_manager.py` می‌توان محدودیت‌هایی روی مجوز استفاده از ابزارها برای هر تسک/عامل تعریف کرد.

## پایش و متریک ابزارها

`src/upsonic/tools/metrics.py` آمار فراخوانی، خطا و زمان اجرای ابزارها را ثبت می‌کند و در Session قابل مشاهده است.

## بهترین تمرین‌ها

1. ابزارها را کوچک و تک‌وظیفه طراحی کنید.
2. برای ابزارهای پولی/حساس، HITL فعال کنید.
3. خروجی ابزار را ساختاریافته برگردانید (dict/Pydantic) تا خطای تفسیر کاهش یابد.
4. از `test_do` برای تست سناریوها بدون اثر جانبی استفاده کنید.

## لینک‌های مرتبط

- [۴. تسک‌ها و خروجی ساختاریافته](04-tasks-output.md)
- [۹. معماری و ساختار کد](09-architecture.md)
- [۱۰. ایمنی و ارزیابی](10-safety-eval.md)
