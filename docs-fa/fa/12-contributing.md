# ۱۲. توسعه و مشارکت

## ساختار ریپازیتوری

```text
Upsonic/
├── src/upsonic/            # کد اصلی بسته
├── tests/                  # unit / integration / smoke
├── examples/               # مثال‌های پایتونی
├── notebooks/              # نوتبوک‌ها (مثلاً stock_report.ipynb)
├── benchmarks/             # سنجش عملکرد
├── overhead_analysis/      # تحلیل سربار framework
├── Docs/                   # مستندات انگلیسی
├── docs-fa/                # همین مستندات فارسی
├── pyproject.toml          # پیکربندی بسته (hatchling + uv)
├── Makefile                # دستورات توسعه
└── CONTRIBUTING.md         # راهنمای مشارکت
```

## راه‌اندازی محیط توسعه

پروژه از `uv` استفاده می‌کند:

```bash
# نصب uv (یک‌بار)
pip install uv

# clone
git clone https://github.com/Upsonic/Upsonic.git
cd Upsonic

# نصب وابستگی‌ها + dev dependencies
uv sync --all-extras

# فعال‌سازی محیط
source .venv/bin/activate
```

## دستورات Makefile (خلاصه)

```bash
make test        # اجرای تست‌ها
make lint        # بررسی کد (ruff)
make format      # قالب‌بندی کد
make docs        # ساخت مستندات
```

> جزئیات کامل را در `Makefile` و `CONTRIBUTING.md` ببینید.

## نوشتن و اجرای تست

```bash
pytest tests/unit -q              # تست‌های واحد
pytest tests/integration -m slow  # تست‌های یکپارچه‌سازی
pytest tests/smoke                # دوده‌آتش (سریع‌ترین کنترل سالم بودن)
```

پیکربندی pytest در `pytest.ini` است. نشان‌های (markers) مختلف برای دسته‌بندی اجرا می‌شوند.

## قوانین سبک کد

- Python 3.10+ با type hints کامل (بسته `py.typed` دارد).
- Pydantic v2 برای مدل‌های داده.
- Ruff برای lint/format.
- Docstring گوگل‌استایل برای APIها (ابزار `_griffe.py` برای مستندسازی خودکار).

## فرآیند مشارکت

1. Issue باز کنید یا روی یک issue موجود کار بگیرید.
2. Branch از `master` بزنید: `feat/...` یا `fix/...`.
3. Commitها با Conventional Commits (`feat:`, `fix:`, `docs:`) — پروژه release-please دارد و نسخه از روی changelog خودکار ساخته می‌شود.
4. تست‌ها را پاس کنید و PR بفرستید.
5. `CODE_OF_CONDUCT.md` را رعایت کنید.

## انتشار (برای Maintainerها)

- `release-please-config.json` تغییرات را به CHANGELOG و bump نسخه ترجمه می‌کند.
- ماژول `cli` هنگام build نسخه را از `__init__.py` (تگ `x-release-please-version`) می‌خواند.
- انتشار روی PyPI با نام `upsonic`.

## افزودن عامل آماده (Prebuilt)

برای اضافه کردن عامل خودمختار آماده به `src/upsonic/prebuilt` PR بزنید؛ هر prebuilt شامل skill + system prompt + پیام اول است.

## حمایت

- Discord: https://discord.gg/pmYDMSQHqY
- Issues: https://github.com/Upsonic/Upsonic/issues
- مستندات رسمی: https://docs.upsonic.ai

## لینک‌های مرتبط

- [۹. معماری و ساختار کد](09-architecture.md)
- [فهرست مستندات](../README.md)
