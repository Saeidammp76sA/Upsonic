# ۸. حافظه، RAG و پایگاه دانش

RAG (تولید مثل شواهد) به عامل شما اجازه می‌دهد از اسناد، داده‌ها و دانش داخلی خودتان پاسخ بگیرد. Upsonic اجزای زیر را برای این کار دارد:

```text
src/upsonic/knowledge_base/   # KnowledgeBase
src/upsonic/vectordb/         # پایگاه‌های برداری (ChromaDB و...)
src/upsonic/embeddings/       # ارائه‌دهنده‌های Embedding
src/upsonic/text_splitter/    # تکه‌بندی متن
src/upsonic/loaders/          # بارگذاری فایل‌ها/اسناد
src/upsonic/memory/           # حافظه بلندمدت عامل
src/upsonic/cache/            # کش نتایج (CacheManager)
src/upsonic/storage/          # ذخیره‌سازها (سوپابیس/S3 و...)
```

## پایگاه دانش (KnowledgeBase)

`KnowledgeBase` کل چرخه زندگی اسناد را مدیریت می‌کند: بارگذاری، تکه‌بندی، embedding، ذخیره برداری و بازیابی (جستجوی dense/full-text/hybrid). امضا واقعی آن در کد: `sources`, `vectordb`, `embedding_provider`, `splitters`, `loaders`, `use_case`, `quality_preference`.

```python
from upsonic.knowledge_base import KnowledgeBase
from upsonic.vectordb import ChromaProvider          # طبق کد src/upsonic/vectordb
from upsonic.embeddings.factory import OpenAIEmbedding

kb = KnowledgeBase(
    sources=["docs/", "README.md"],       # فایل، پوشه یا رشته متنی
    vectordb=ChromaProvider(config=chroma_config),
    embedding_provider=OpenAIEmbedding(),
    use_case="rag_retrieval",
)

await kb.setup_async()                     # پردازش و ایندکس اسناد
results = await kb.query_async("What is the project about?")
```

اتصال به عامل: `KnowledgeBase` پروتکل `get_tools()` دارد، بنابراین می‌توان ابزارهای جست‌وجوی آن را مستقیماً به Agent/Task داد.

## Vector DB

ماژول `vectordb` با ارائه‌دهنده‌های مختلف کار می‌کند. برای ChromaDB:

```bash
uv pip install "upsonic[chromadb]"
```

## Embeddings

`embeddings/factory.py` ارائه‌دهنده‌های مختلف embedding (OpenAI و غیره) را مدیریت می‌کند. انتخاب ارائه‌دهنده روی کیفیت بازیابی تأثیر مستقیم دارد.

## Text Splitter

برای اسناد بزرگ، `text_splitter` متن را به قطعه‌هایی با اندازه مناسب (با overlap) تقسیم می‌کند تا retrieval دقیق‌تر شود.

## Memory (حافظه عامل)

حافظه برخلاف RAG، دانش **بین‌جلسه‌ای** درباره کاربر و الگوهای گفتگو نگه می‌دارد. با فعال‌سازی `memory_config` روی Agent، عامل ترجیحات و واقعیات مهم را به‌خاطر می‌سپارد.

## Cache

`CacheManager` (`src/upsonic/cache`) پاسخ‌های تکراری را کش می‌کند تا هزینه و تأخیر کاهش یابد — مفید برای پرسش‌های پرتکرار بازار.

## Storage

ذخیره‌سازی state و داده‌ها روی Supabase/S3 با افزونه:

```bash
uv pip install "upsonic[s3]"
```

## مثال فین‌تک: دستیار تحقیق بازار

```python
kb = KnowledgeBase(documents=["sec_filings/*.pdf"], embedder="openai", vector_db="chromadb")

agent = Agent(model="anthropic/claude-sonnet-4-5", name="Research Bot")
answer = agent.print_do(Task(
    description="Summarize key risks of {ticker} from filings",
    context="Ticker: TSLA",
    use_knowledge_base=True,
    knowledge_base=kb,
))
```

## لینک‌های مرتبط

- [۶. تیم، گفتگو و حافظه](06-team-chat.md)
- [۹. معماری و ساختار کد](09-architecture.md)
