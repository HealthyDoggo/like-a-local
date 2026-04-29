"""Shared Gemini API client"""
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

_gemini_client = None


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
