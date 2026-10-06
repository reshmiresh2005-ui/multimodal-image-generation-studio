import random
import time
from functools import wraps


def is_retryable_exception(exc: Exception) -> bool:
    text = str(exc).lower()

    retry_words = (
        "timeout",
        "temporarily unavailable",
        "connection",
        "rate limit",
        "too many requests",
        "429",
        "500",
        "502",
        "503",
        "504",
    )

    return any(word in text for word in retry_words)


def retry_with_backoff(max_retries=4, base_backoff=1.0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except Exception as exc:
                    last_error = exc

                    if attempt >= max_retries:
                        raise

                    if not is_retryable_exception(exc):
                        raise

                    delay = base_backoff * (2 ** attempt)
                    jitter = random.uniform(0, delay * 0.35)
                    time.sleep(delay + jitter)

            raise last_error

        return wrapper

    return decorator
