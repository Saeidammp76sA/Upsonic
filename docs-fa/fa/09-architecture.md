# ۹. معماری و ساختار کد

این صفحه نقشه کامل ماژول‌های `src/upsonic` را نشان می‌دهد تا توسعه‌دهندگان بدانند هر قابلیت در کدام پوشه زندگی می‌کند.

## نمای کلی بسته

```text
src/upsonic/
├── __init__.py            # Exportهای عمومی + بارگذاری lazy + load_dotenv
├── agent/                 # Agent، AutonomousAgent، base، events، otel_manager،
│   ├── autonomous_agent/  #    sandbox providers (محلی/ابری)
│   ├── deepagent/         #    اجرای عمیق چندمرحله‌ای
│   ├── pipeline/          #    خط لوله اجرای تسک
│   └── context_managers/  #    مدیریت context گفتگو
├── tasks/                 # کلاس Task (توصیف، context، tools، response_format)
├── team/                  # Team: هماهنگی چند عامل
├── chat/                  # Chat stateful و تاریخچه پیام
├── session/               # ثبت نشست‌ها برای دیباگ/CLI
├── tools/                 # @tool، builtin_tools، mcp.py، hitl، metrics، registry، schema
├── integrations/          # اتصال‌های آماده به سرویس‌های ثالث
├── toolsets/              # Toolsetها (LocalMCPServerStdioToolset و...)
├── models/                # انتزاع مدل‌های زبانی و routing
├── providers/             # ارائه‌دهنده‌های API (Anthropic/OpenAI/Ollama/...)
├── interfaces/            # رابط‌های API (REST و...)
├── graph/ , graphv2/      # ارکستراسیون workflow گرافی (دو نسخه)
├── run/                   # موتور اجرای workflow/graph
├── memory/                # حافظه بلندمدت عامل
├── knowledge_base/        # RAG روی اسناد کاربر
├── vectordb/              # لایه دیتابیس برداری (ChromaDB و...)
├── embeddings/            # کارخانه embedding providerها
├── text_splitter/         # تکه‌بندی متن برای retrieval
├── loaders/               # بارگذاری فایل/سند
├── ocr/                   # لوله OCR: layer_0_preprocessing + layer_1_engines
├── skills/                # سیستم مهارت‌ها (SKILL.md و اسکریپت‌ها)
├── prebuilt/              # عوامل خودمختار آماده (applied_scientist و...)
├── culture/               # دانش/قواعد مشترک تیمی
├── safety_engine/         # سیاست‌های ایمنی ورودی/خروجی/دستورات
├── reliability_layer/     # بازتلاش و اعتبارسنجی خروجی مدل
├── reflection/            # خودبازتاب و اصلاح پاسخ
├── eval/                  # ابزارهای ارزیابی کیفیت عامل
├── usage_registry/        # ثبت مصرف توکن/هزینه
├── cache/                 # CacheManager
├── storage/               # بک‌اند ذخیره‌سازی (Supabase/S3)
├── db/                    # لایه دیتابیس داخلی
├── schemas/, messages/    # مدل‌های داده و انواع پیام
├── context/               # مدیریت زمینه اجرا
├── profiles/              # پروفایل رفتار عامل
├── simulation/            # شبیه‌سازی سناریوها
├── canvas/                # بوم تعاملی/بصری
├── uel/                   # Upsonic Execution Language (DSL اجرای تسک)
├── ralph/                 # حلقه تکرار/بهبود خودکار
├── cli/                   # دستور `upsonic` (session list، visualizations)
├── direct.py              # اجرای سریع بدون ساخت Agent
├── output.py, usage.py    # کمک‌متدهای خروجی و مصرف
└── _json_schema.py, _parts_manager.py, _ssrf.py, _utils.py  # ابزار داخلی
```

## نحوه export عمومی (`__init__.py`)

بسته از **lazy import** استفاده می‌کند تا سرعت import اولیه بالا بماند؛ کلاس‌هایی مثل `Agent`, `Task`, `AutonomousAgent`, `Chat`, `Team`, `KnowledgeBase` هنگام اولین استفاده import می‌شوند. همچنین `.env` از پوشه جاری کاربر بارگذاری می‌شود.

## جریان اجرای یک تسک (Traditional)

```text
Task → Agent.do()
  → ReliabilityLayer (اعتبارسنجی/بازتلاش)
  → SafetyEngine (فیلتر ورودی/خروجی)
  → Model Provider (Anthropic/OpenAI/...)
  → Tool Calls (registry → execution → HITL در صورت نیاز)
  → Output Parsing (Pydantic response_format)
  → Response (result, cost, history) → Session
```

## جریان عامل خودمختار

```text
AutonomousAgent(workspace=...)
  → File/Shell tools داخل sandbox (محلی یا E2B)
  → Policy checks (safety_engine + path guards)
  → Loop: plan → act → observe → reflect
```

## تست‌ها و بنچمارک‌ها

```text
tests/unit/ tests/integration/ tests/smoke/   # تست‌ها
benchmarks/                                    # سنجش عملکرد
overhead_analysis/                             # تحلیل سربار framework
```

## لینک‌های مرتبط

- [۱۰. ایمنی و ارزیابی](10-safety-eval.md)
- [۱۲. توسعه و مشارکت](12-contributing.md)
