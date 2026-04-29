"""LLM-based category classifier using Gemini 2.5 Flash"""
import json
import logging
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from backend.database.models import Category
from backend.services.gemini_client import gemini_generate

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

    def _categories_block(self) -> str:
        cat_lines = []
        for cat in self.categories:
            descs = ", ".join(cat.description) if isinstance(cat.description, list) else cat.description
            cat_lines.append(f'- "{cat.id}": {cat.title} — {descs}')
        return "\n".join(cat_lines)

    def _build_prompt(self, tip_text: str) -> str:
        return f"""You are a travel tip classifier. Given a travel tip, pick the single best category from the list below.

Be liberal with your classifications — if a tip is even somewhat related to a category, assign it. Only return "none" if the tip truly does not fit any category at all.

Categories:
{self._categories_block()}

Respond with ONLY a JSON object, no markdown fences:
{{"category_id": "<id or none>", "confidence": <0.0-1.0>}}

Tip: "{tip_text}"
"""

    def _build_batch_prompt(self, tips: List[Tuple[int, str]]) -> str:
        tip_lines = []
        for tip_id, text in tips:
            tip_lines.append(f'{{"id": {tip_id}, "text": "{text}"}}')
        tips_block = ",\n  ".join(tip_lines)

        return f"""You are a travel tip classifier. For EACH tip below, pick the single best category from the category list.

Be liberal with your classifications — if a tip is even somewhat related to a category, assign it. Only return "none" if the tip truly does not fit any category at all.

Categories:
{self._categories_block()}

Tips:
[
  {tips_block}
]

Respond with ONLY a JSON array (one entry per tip, same order), no markdown fences:
[
  {{"id": <tip_id>, "category_id": "<id or none>", "confidence": <0.0-1.0>}},
  ...
]
"""

    @staticmethod
    def _strip_fences(text: str) -> str:
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

    def classify_tip(self, tip_text: str) -> Tuple[Optional[str], float]:
        """Classify a single tip via Gemini (1 API call)."""
        if not self.categories:
            raise ValueError("Categories not loaded. Call load_categories() first.")

        prompt = self._build_prompt(tip_text)

        try:
            response = gemini_generate(model=GEMINI_MODEL, contents=prompt)
            result = json.loads(self._strip_fences(response.text))
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
        Classify tips in a single Gemini call.

        Args:
            tips_with_text: List of (tip_id, tip_text) tuples.

        Returns:
            List of (tip_id, category_id, confidence) tuples.
        """
        if not tips_with_text:
            return []

        if len(tips_with_text) == 1:
            tip_id, text = tips_with_text[0]
            cat_id, confidence = self.classify_tip(text)
            return [(tip_id, cat_id, confidence)]

        if not self.categories:
            raise ValueError("Categories not loaded. Call load_categories() first.")

        prompt = self._build_batch_prompt(tips_with_text)
        tip_ids = {tip_id for tip_id, _ in tips_with_text}

        try:
            response = gemini_generate(model=GEMINI_MODEL, contents=prompt)
            items = json.loads(self._strip_fences(response.text))
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse batch Gemini response: {e}")
            return [(tid, None, 0.0) for tid, _ in tips_with_text]
        except Exception as e:
            logger.error(f"Gemini batch classification error: {e}")
            return [(tid, None, 0.0) for tid, _ in tips_with_text]

        results_map: dict[int, Tuple[Optional[str], float]] = {}
        for item in items:
            try:
                tid = int(item["id"])
                cat_id = item.get("category_id")
                confidence = float(item.get("confidence", 0.0))
                if cat_id == "none" or cat_id not in self._category_map:
                    cat_id = None
                results_map[tid] = (cat_id, confidence)
            except (KeyError, ValueError, TypeError) as e:
                logger.warning(f"Skipping malformed batch item: {item} ({e})")

        results = []
        for tip_id, _ in tips_with_text:
            cat_id, confidence = results_map.get(tip_id, (None, 0.0))
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
