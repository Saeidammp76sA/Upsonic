# ۷. OCR و پردازش سند

Upsonic یک رابط یکپارچه OCR با معماری **چندلایه** ارائه می‌دهد:

- **Layer 0 (آماده‌سازی سند):** تبدیل PDF به تصویر، پیش‌پردازش تصویر و بهبود کیفیت.
- **Layer 1 (موتور OCR):** استخراج متن از تصویر با موتور انتخابی شما.

## نصب

```bash
uv pip install "upsonic[ocr]"
# یا موتور خاص:
uv pip install "upsonic[easyocr]" "upsonic[pytesseract]" "upsonic[paddleocr]" "upsonic[rapidocr]"
```

## استفاده سریع

```python
from upsonic.ocr import OCR
from upsonic.ocr.layer_1.engines import EasyOCREngine

engine = EasyOCREngine(languages=["en"])
ocr = OCR(layer_1_ocr_engine=engine)

text = ocr.get_text("invoice.pdf")
print(text)
```

## موتورهای پشتیبانی‌شده

| موتور | بسته اختیاری | ویژگی |
|-------|--------------|-------|
| EasyOCR | `easyocr` | دقت بالا، چندزبانه از جمله فارسی (`languages=["fa","en"]`) |
| Tesseract (pytesseract) | `pytesseract` | سبک، مبتنی بر داده آموزش‌دیده قدیمی |
| PaddleOCR | `paddleocr` | مناسب اسناد واقعی و جدول |
| RapidOCR | `rapidocr` | مبتنی بر ONNX، سریع و سبک |
| DeepSeek OCR | - | مدل زبانی برای OCR نسل جدید |
| DeepSeek via Ollama | `ollama` | اجرای لوکال مدل OCR زبانی |

> نکته فارسی: برای اسناد فارسی، EasyOCR با `languages=["fa"]` گزینه مناسبی است؛ برای ترکیب فارسی/انگلیسی هر دو کد را بدهید.

## ساختار ماژول در کد

```text
src/upsonic/ocr/
├── layer_0_preprocessing/   # تبدیل PDF→تصویر و پیش‌پردازش
└── layer_1_engines/         # موتورهای OCR (EasyOCR, Tesseract, ...)
```

## ترکیب OCR با عامل‌ها (سناریوی فین‌تک)

OCR را می‌توان به‌عنوان ابزار به یک تسک داد تا عامل خودش تصمیم بگیرد چه زمانی سند را بخواند:

```python
from upsonic.tools import tool
from upsonic.ocr import OCR
from upsonic.ocr.layer_1.engines import EasyOCREngine

ocr = OCR(layer_1_ocr_engine=EasyOCREngine(languages=["en"]))

@tool
def read_invoice(path: str) -> str:
    """Extract raw text from an invoice PDF or image."""
    return ocr.get_text(path)

task = Task(
    description="Extract vendor, total amount and due date from {file}",
    context="File: invoice.pdf",
    tools=[read_invoice],
    response_format=InvoiceSchema,
)
agent.print_do(task)
```

## Layer 0 — تنظیمات پیش‌پردازش

در لایه صفر می‌توان رزولوشن تبدیل PDF، آستانه‌های کیفیت و نرمال‌سازی را پیکربندی کرد تا دقت موتور OCR بالا برود (جزئیات API: `src/upsonic/ocr/layer_0_preprocessing`).

## لینک‌های مرتبط

- [۴. تسک‌ها و خروجی ساختاریافته](04-tasks-output.md)
- [۸. حافظه، RAG و پایگاه دانش](08-memory-rag.md)
- مستندات رسمی: [docs.upsonic.ai/concepts/ocr/overview](https://docs.upsonic.ai/concepts/ocr/overview)
