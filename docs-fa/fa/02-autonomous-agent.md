# ۲. عامل خودمختار (Autonomous Agent)

عامل خودمختار نوعی از عامل است که برخلاف عامل سنتی (که فقط ابزارهای مشخص‌شده را صدا می‌زند)، **دسترسی مستقیم به سیستم فایل و اجرای دستور shell** دارد؛ اما همه این عملیات در یک محیط ایزوله و کنترل‌شده انجام می‌شود. این الگو مشابه OpenClaw و Claude Cowork است.

## ساخت عامل خودمختار

```python
from upsonic import AutonomousAgent, Task

agent = AutonomousAgent(
    model="anthropic/claude-sonnet-4-5",
    workspace="/path/to/workspace",   # ریشه مجاز عملیات فایل/shell
)

task = Task("Read all .log files in the workspace and summarize errors")
agent.print_do(task)
```

پارامترهای مهم سازنده (بر اساس امضای واقعی `autonomous_agent.py`):

| پارامتر | توضیح |
|---------|-------|
| `model` | مدل زبانی عامل، به فرمت `provider/model-name` (پیش‌فرض `openai/gpt-4o`) |
| `workspace` | پوشه‌ای که تمام عملیات فایل و shell فقط داخل آن مجاز است |
| `enable_filesystem` / `enable_shell` | فعال/غیرفعال کردن toolkit فایل و shell |
| `shell_timeout`, `shell_max_output` | محدودیت زمان و خروجی دستورات |
| `blocked_commands` | فهرست دستورات مسدودشده اضافی |
| `tool_call_limit` | سقف فراخوانی ابزار در هر اجرا |
| `skills` | مجموعه مهارت‌ها (`Skills`) قابل اتصال |
| `user_policy` | سیاست‌های سفارشی ایمنی (`Policy`) |
| `storage`, `memory`, `db`, `session_id`, `user_id` | حافظه و ذخیره‌سازی نشست |
| `full_session_memory`, `summary_memory`, `user_analysis_memory` | ویژگی‌های حافظه |
| `tools`, `system_prompt`, `reflection`, `reliability_layer` | مانند Agent سنتی |

## Toolkit فایل و Shell

دو toolkit داخلی در کد وجود دارد:

```text
src/upsonic/agent/autonomous_agent/filesystem_toolkit.py  # خواندن/نوشتن فایل (امن)
src/upsonic/agent/autonomous_agent/shell_toolkit.py       # اجرای دستور shell (محدود)
```

## مدل امنیتی Workspace

- **محدودیت مسیر:** هر خواندن/نوشتن/اجرا فقط زیر `workspace` مجاز است.
- **مسدودسازی Path Traversal:** تلاش‌هایی مانند `../../etc/passwd` رد می‌شوند.
- **فیلتر دستورات خطرناک:** دستورات مخرب shell (مانند حذف سیستماتیک) بلاک می‌شوند.
- **ثبت رویدادها (Events):** عملیات عامل قابل رصد است (`src/upsonic/agent/events.py`).

ماژول‌های مرتبط در کد:

```text
src/upsonic/agent/autonomous_agent/   # منطق عامل خودمختار و sandbox
src/upsonic/safety_engine/            # موتور ایمنی و سیاست‌ها
src/upsonic/_ssrf.py                  # محافظت در برابر SSRF
```

## سندباکس ابری (E2B)

برای اجرای ایزوله کد و دستورات در فضای ابری، از ToolKit آماده `E2BTools` در `src/upsonic/tools/custom_tools/e2b.py` استفاده کنید:

```python
from upsonic import Agent, Task
from upsonic.tools.custom_tools.e2b import E2BTools

e2b = E2BTools()  # نیازمند E2B_API_KEY

task = Task(
    description="Run a python snippet in the cloud sandbox and return output",
    tools=[e2b],
)
agent.print_do(task)
```

ابزارهای موجود: `e2b_run_code`, `e2b_run_command`, `e2b_upload_file`, `e2b_download_file`, `e2b_list_files`, `e2b_write_file`, `e2b_read_file`, `e2b_install_packages`, `e2b_get_sandbox_info`, `e2b_shutdown_sandbox` (نسخه async با پیشوند `a`).

مزیت: کدها و دستورات عامل روی VM ابری موقت اجرا می‌شوند و سیستم میزبان در امان می‌ماند.

## عوامل خودمختار آماده (Prebuilt)

پروژه مجموعه‌ای از عوامل آماده دارد که هرکدام یک Skill، پرامپت سیستمی و پیام اول را بسته‌بندی کرده‌اند (`src/upsonic/prebuilt`). در حال حاضر کلاس `AppliedScientist` در دسترس است:

```python
from upsonic.prebuilt import AppliedScientist

scientist = AppliedScientist(model="openai/gpt-4o", workspace="./research")
exp = scientist.new_experiment(
    name="tabpfn_adult",
    research_source="...",
    current_notebook="...",
)
exp.run()                       # یا run_in_background() / run_async()
print(scientist.experiments["tabpfn_adult"].summary)
```

راهنمای افزودن prebuilt جدید: `documents/ai/guides/new_prebuilt_agent_adding.md`.

## Skills (مهارت‌ها)

سیستم `skills` در Upsonic اجازه می‌دهد دانش/دستورالعمل‌های ماژولار (مشابه Agent Skills با فایل `SKILL.md`) به عامل اضافه شوند:

```text
src/upsonic/skills/
```

یک Skill معمولاً شامل توضیح کاربرد، اسکریپت‌ها و منابع کمکی است که عامل هنگام نیاز بارگذاری می‌کند.

## نکات کاربردی

- برای دیباگ، لاگ‌ها را در `workspace` نگه دارید و از متدهای بصری‌سازی (CLI) استفاده کنید: `upsonic cli` (پوشه `src/upsonic/cli`).
- اگر تسک نیاز به اینترنت دارد، از طریق ابزارهای MCP متصل کنید تا کنترل و ثبت دقیق‌تر باشد.
- همیشه برای کارهای پرخطر از سندباکس ابری استفاده کنید.

## لینک‌های مرتبط

- [۱. شروع سریع](01-quickstart.md)
- [۵. ابزارها و MCP](05-tools-mcp.md)
- [۱۰. ایمنی و ارزیابی](10-safety-eval.md)
