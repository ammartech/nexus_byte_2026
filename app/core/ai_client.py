import random
import time

class AIServiceError(Exception):
    pass

class AIServiceTimeout(Exception):
    pass

def call_with_retry(service_name: str, fn, max_retries: int = 2, timeout_seconds: float = 3.0):
    """
    Calls fn() with up to max_retries retries and exponential backoff.
    Raises AIServiceTimeout if all attempts fail.
    """
    attempt = 0
    while attempt <= max_retries:
        try:
            return fn()
        except Exception:
            attempt += 1
            if attempt > max_retries:
                raise AIServiceTimeout(f"{service_name} failed after {max_retries} retries")
            time.sleep(0.5 * (2 ** (attempt - 1)))  # exponential backoff

def ats_scorer(cv_text: str) -> dict:
    # Mock: simulates Hufiza's ATSScore service
    return {
        "score": random.randint(50, 95),
        "subscores": {"structure": 80, "keywords": 65, "formatting": 90, "length": 70},
        "model_version": "ats-scorer-mock-0.1",
    }

def content_rewriter(cv_text: str) -> dict:
    # Mock: simulates Hufiza's PhraseBoost service
    return {
        "rewrites": ["Rewrote bullet point 1 with stronger action verbs."],
        "model_version": "content-rewriter-mock-0.1",
    }