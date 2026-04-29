"""Shared Gemini API client with retry logic"""
import logging
import os
import random
import re
import time
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

_gemini_client = None

_RETRYABLE_CODES = {"429", "500", "502", "503"}
_MAX_RETRIES = 4
_BASE_DELAY = 2.0


def _is_retryable(exc: Exception) -> bool:
    msg = str(exc)
    return any(code in msg for code in _RETRYABLE_CODES) or isinstance(exc, (ConnectionError, TimeoutError))


def _parse_retry_delay(exc: Exception) -> float | None:
    """Extract retryDelay (e.g. '50s') from the error message if present."""
    match = re.search(r"['\"]retryDelay['\"]\s*:\s*['\"](\d+(?:\.\d+)?)s['\"]", str(exc))
    if match:
        return float(match.group(1))
    return None


def get_gemini_client():
    """Get or create a google.genai Client instance."""
    global _gemini_client
    if _gemini_client is not None:
        return _gemini_client

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to your .env file."
        )

    from google import genai
    _gemini_client = genai.Client(api_key=api_key)
    logger.info("Gemini client initialised")
    return _gemini_client


def gemini_generate(model: str, contents, max_retries: int = _MAX_RETRIES):
    """Call generate_content with exponential backoff on transient errors."""
    client = get_gemini_client()
    for attempt in range(max_retries + 1):
        try:
            return client.models.generate_content(model=model, contents=contents)
        except Exception as e:
            if attempt < max_retries and _is_retryable(e):
                server_delay = _parse_retry_delay(e)
                backoff_delay = _BASE_DELAY * (2 ** attempt) + random.uniform(0, 1)
                delay = max(server_delay or 0, backoff_delay)
                logger.warning(f"Gemini request failed (attempt {attempt + 1}/{max_retries + 1}), retrying in {delay:.1f}s: {e}")
                time.sleep(delay)
            else:
                raise
