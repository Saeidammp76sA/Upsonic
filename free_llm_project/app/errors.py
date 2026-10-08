"""Error management: exponential-backoff retry helper + structured logging.

All LLM / embedding / HTTP calls in the project go through `retry_call`, which:
  * retries transient failures (network errors, 4xx rate limits, 5xx proxy errors)
  * uses exponential backoff with jitter (configurable via config/settings.py)
  * records every attempt and failure in logs/app.log for diagnostics
"""

from __future__ import annotations

import functools
import logging
import random
import time
from pathlib import Path
from typing import Any, Callable, Iterable, Type

from config.settings import settings

LOG_DIR = Path(settings.log_dir)
LOG_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("free_llm_project")


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure console + file logging (idempotent)."""
    if logger.handlers:
        return logger
    logger.setLevel(level)
    fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(name)s | %(message)s")

    fh = logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    sh.setLevel(logging.WARNING)  # keep console clean; details go to the log file
    logger.addHandler(sh)
    return logger


class RetryExhausted(RuntimeError):
    """Raised when all retry attempts failed."""


def is_transient(exc: Exception, retry_on_status: Iterable[int]) -> bool:
    """Decide whether an exception is worth retrying."""
    # openai / httpx style errors expose a status_code attribute
    status = getattr(exc, "status_code", None) or getattr(
        getattr(exc, "response", None), "status_code", None
    )
    if isinstance(status, int):
        return status in tuple(retry_on_status)
    # network-level errors are always transient
    transient_types: tuple[Type[Exception], ...] = (
        ConnectionError,
        TimeoutError,
    )
    try:
        import httpx
        transient_types = transient_types + (httpx.TransportError,)
    except ImportError:  # pragma: no cover
        pass
    try:
        import openai
        transient_types = transient_types + (
            openai.APIConnectionError,
            openai.RateLimitError,
            openai.InternalServerError,
        )
    except ImportError:  # pragma: no cover
        pass
    return isinstance(exc, transient_types)


def retry_call(
    fn: Callable[..., Any],
    *args: Any,
    what: str = "operation",
    max_attempts: int | None = None,
    **kwargs: Any,
) -> Any:
    """Run `fn` with exponential-backoff retry according to RetrySettings."""
    cfg = settings.retry
    attempts = max_attempts or cfg.max_attempts
    delay = cfg.initial_delay
    last_exc: Exception | None = None

    for attempt in range(1, attempts + 1):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001 — we re-raise below if not transient
            last_exc = exc
            if not is_transient(exc, cfg.retry_on_status):
                logger.error("%s failed with non-transient error: %s: %s",
                             what, type(exc).__name__, exc)
                raise
            if attempt == attempts:
                break
            sleep_for = min(delay, cfg.max_delay) + random.uniform(0, 0.5)
            logger.warning("%s attempt %d/%d failed (%s: %s); retrying in %.1fs",
                           what, attempt, attempts, type(exc).__name__, exc, sleep_for)
            time.sleep(sleep_for)
            delay *= cfg.backoff_factor

    logger.critical("%s exhausted all %d attempts. Last error: %s", what, attempts, last_exc)
    raise RetryExhausted(f"{what} failed after {attempts} attempts") from last_exc


def with_retry(what: str = "") -> Callable:
    """Decorator form of retry_call."""

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return retry_call(fn, *args, what=what or fn.__name__, **kwargs)
        return wrapper
    return decorator


setup_logging()
