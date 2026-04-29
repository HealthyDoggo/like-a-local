"""LLM-based category classifier using Gemini 2.5 Flash"""
import json
import logging
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from backend.database.models import Category
from backend.services.gemini_client import get_gemini_client

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-2.5-flash"


class LLMClassifier:
    """Classifies tips into categories using Gemini LLM calls."""

    def __init__(self):
        self.categories: Optional[List[Category]] = None
        self._category_map: dict = {}

    def load_categories(self, db: Session):
        self.categories = db.query(Category).order_by(Category.display_order).all()
        self._category_map = {c.id: c for c in self.categories}
        logger.info(f"LLMClassifier loaded {len(self.categories)} categories")

    def _build_prompt(self, tip_text: str) -> str:
        cat_lines = []
        for cat in self.categories:
            descs = ", ".join(cat.description) if isinstance(cat.description, list) else cat.description
            cat_lines.append(f'- "{cat.id}": {cat.title} — {descs}')
        categories_block = "\n".join(cat_lines)

        return f"""You are a travel tip classifier. Given a travel tip, pick the single best category from the list below.

Be liberal with your classifications — if a tip is even somewhat related to a category, assign it. Only return "none" if the tip truly does not fit any category at all.

Categories:
{categories_block}

Respond with ONLY a JSON object, no markdown fences:
{{"category_id": "<id or none>", "confidence": <0.0-1.0>}}

Tip: "{tip_text}"
"""

    def classify_tip(self, tip_text: str) -> Tuple[Optional[str], float]:
        """
        Classify a single tip via Gemini.

        Returns:
            (category_id, confidence) where category_id is None if "none".
        """
        if not self.categories:
            raise ValueError("Categories not loaded. Call load_categories() first.")

        client = get_gemini_client()
        prompt = self._build_prompt(tip_text)

        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
            )
            text = response.text.strip()
            # Strip markdown fences if the model adds them anyway
            if text.startswith("```"):
                text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

            result = json.loads(text)
            cat_id = result.get("category_id")
            confidence = float(result.get("confidence", 0.0))

            if cat_id == "none" or cat_id not in self._category_map:
                return None, confidence

            return cat_id, confidence

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse Gemini response for tip: {e}")
            return None, 0.0
        except Exception as e:
            logger.error(f"Gemini classification error: {e}")
            return None, 0.0

    def classify_batch(self, tips_with_text: List[Tuple[int, str]]) -> List[Tuple[int, Optional[str], float]]:
        """
        Classify a batch of tips sequentially.

        Args:
            tips_with_text: List of (tip_id, tip_text) tuples.

        Returns:
            List of (tip_id, category_id, confidence) tuples.
        """
        results = []
        for tip_id, text in tips_with_text:
            cat_id, confidence = self.classify_tip(text)
            results.append((tip_id, cat_id, confidence))
        return results

    def should_assign_category(self, confidence: float) -> bool:
        return confidence >= 0.4


_llm_classifier = None


def get_llm_classifier() -> LLMClassifier:
    global _llm_classifier
    if _llm_classifier is None:
        _llm_classifier = LLMClassifier()
    return _llm_classifier
