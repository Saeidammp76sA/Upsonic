# ۱۱. مدل‌ها و ارائه‌دهنده‌ها

در Upsonic مدل زبانی با رشته‌ای به فرمت `provider/model-name` انتخاب می‌شود:

```python
agent = Agent(model="anthropic/claude-sonnet-4-5")
```

## ارائه‌دهنده‌های پشتیبانی‌شده (مبتنی بر ماژول‌های `providers` و `models`)

| Provider | نمونه مقدار `model` | کلید محیطی |
|----------|---------------------|------------|
| Anthropic | `anthropic/claude-sonnet-4-5`, `anthropic/claude-opus-4-1` | `ANTHROPIC_API_KEY` |
| OpenAI | `openai/gpt-4o`, `openai/o3` | `OPENAI_API_KEY` |
| Google Gemini | `gemini/gemini-2.0-flash` | `GEMINI_API_KEY` |
| Groq | `groq/llama-3.3-70b-versatile` | `GROQ_API_KEY` |
| DeepSeek | `deepseek/deepseek-chat` | `DEEPSEEK_API_KEY` |
| Mistral | `mistral/mistral-large` | `MISTRAL_API_KEY` |
| xAI | `xai/grok-3` | `XAI_API_KEY` |
| Cerebras | `cerebras/llama-3.1-70b` | `CEREBRAS_API_KEY` |
| Perplexity | `perplexity/sonar` | `PERPLEXITY_API_KEY` |
| Ollama (لوکال) | `ollama/llama3` | - (سرور محلی) |
| OpenRouter | `openrouter/anthropic/claude-sonnet-4-5` | `OPENROUTER_API_KEY` |

> برای فهرست دقیق و به‌روز، کد `src/upsonic/providers` و `src/upsonic/models` را ببینید؛ این جدول خلاصه رایج‌ترین‌هاست.

## تنظیم کلیدها

ترتیب اولویت بارگذاری متغیرهای محیطی:

1. متغیرهای محیطی سیستم
2. فایل `.env` در پوشه اجرای اسکریپت (Upsonic خودکار load می‌کند)

```bash
echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env
```

## مدل لوکال با Ollama

```bash
ollama serve
ollama pull llama3.1
```

```python
agent = Agent(model="ollama/llama3.1", name="Local Agent")
```

مناسب حریم خصوصی داده‌های مالی و کاهش هزینه.

## انتخاب مدل — راهنمای سریع

| سناریو | پیشنهاد |
|--------|----------|
| استدلال پیچیده تحلیل مالی | Claude Sonnet/Opus یا o3 |
| تسک ساده و پرسرعت | Haiku / GPT-4o-mini / Groq |
| حساسیت به داده (لوکال) | Ollama |
| مقایسه چند مدل | OpenRouter |

## Model Routing و هرج‌ومرج

ماژول `models` امکان انتزاع یکسان روی همه providerها و مدیریت fallback را فراهم می‌کند. در صورت خطای rate-limit یا invalid key، استثناهای مربوطه از `exceptions.py` (`InvalidModelNameError`, `MissingApiKeyError`, `RateLimitError`, ...) مطرح می‌شوند.

## Multi-model در تیم

هر عضو Team می‌تواند مدل متفاوت داشته باشد؛ مثلاً جمع‌آوری داده با مدل ارزان و نتیجه‌گیری با مدل قوی:

```python
collector = Agent(model="groq/llama-3.3-70b-versatile", name="Collector")
advisor   = Agent(model="anthropic/claude-opus-4-1", name="Advisor")
Team(agents=[collector, advisor])
```

## لینک‌های مرتبط

- [۳. عامل سنتی](03-traditional-agent.md)
- [۶. تیم، گفتگو و حافظه](06-team-chat.md)
