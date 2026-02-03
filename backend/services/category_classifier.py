"""Category classification service using vector embeddings"""
import logging
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from backend.database.models import Category
from backend.services.embedding import get_embedding_service
from dotenv import load_dotenv
import os
load_dotenv()
logger = logging.getLogger(__name__)
CATEGORY_CONFIDENCE_THRESHOLD = float(os.getenv("CATEGORY_CONFIDENCE_THRESHOLD", "0.65"))

class CategoryClassifier:
    """Classifies tips into categories using cosine similarity"""

    def __init__(self):
        self.embedding_service = get_embedding_service()
        self.categories = None
        self.confidence_threshold = CATEGORY_CONFIDENCE_THRESHOLD

    def load_categories(self, db: Session):
        """Load categories from database"""
        self.categories = db.query(Category).order_by(Category.display_order).all()
        logger.info(f"Loaded {len(self.categories)} categories")

    def classify_tip(self, tip_embedding: List[float], return_details: bool = False) -> Tuple[str, float]:
        """
        Classify tip using cosine similarity against multiple category embeddings.

        Args:
            tip_embedding: The embedding vector for the tip
            return_details: If True, returns (category_id, confidence, best_phrase_idx, all_phrase_sims)

        Returns:
            Tuple of (category_id, confidence_score) or
            Tuple of (category_id, confidence_score, best_phrase_idx, phrase_similarities) if return_details=True
        """
        if not self.categories:
            raise ValueError("Categories not loaded. Call load_categories() first.")

        if not tip_embedding:
            raise ValueError("Tip embedding cannot be empty")

        # Calculate similarity with each category (taking max across all phrase embeddings)
        similarities = {}
        best_phrase_indices = {}
        all_phrase_similarities = {}

        for category in self.categories:
            try:
                # category.embedding is now a list of embedding vectors
                max_similarity = 0.0
                best_phrase_idx = 0
                phrase_sims = []

                for idx, phrase_embedding in enumerate(category.embedding):
                    similarity = self.embedding_service.similarity(
                        tip_embedding,
                        phrase_embedding
                    )
                    phrase_sims.append(similarity)

                    if similarity > max_similarity:
                        max_similarity = similarity
                        best_phrase_idx = idx

                similarities[category.id] = max_similarity
                best_phrase_indices[category.id] = best_phrase_idx
                all_phrase_similarities[category.id] = phrase_sims
            except Exception as e:
                logger.error(f"Error calculating similarity for category {category.id}: {e}")
                similarities[category.id] = 0.0
                best_phrase_indices[category.id] = 0
                all_phrase_similarities[category.id] = []

        # Find category with highest similarity
        if not similarities:
            raise ValueError("No similarities calculated")

        best_category_id, best_score = max(similarities.items(), key=lambda x: x[1])

        if return_details:
            return (
                best_category_id,
                best_score,
                best_phrase_indices[best_category_id],
                all_phrase_similarities[best_category_id]
            )

        return best_category_id, best_score

    def classify_batch(self, tips_with_embeddings: List[Tuple[int, List[float]]], return_details: bool = False) -> List[Tuple]:
        """
        Batch classification for efficiency.

        Args:
            tips_with_embeddings: List of (tip_id, embedding) tuples
            return_details: If True, returns detailed classification info

        Returns:
            List of (tip_id, category_id, confidence_score) tuples or
            List of (tip_id, category_id, confidence_score, phrase_idx, phrase_sims) if return_details=True
        """
        if not self.categories:
            raise ValueError("Categories not loaded. Call load_categories() first.")

        results = []
        for tip_id, embedding in tips_with_embeddings:
            try:
                classification = self.classify_tip(embedding, return_details=return_details)
                if return_details:
                    category_id, confidence, phrase_idx, phrase_sims = classification
                    results.append((tip_id, category_id, confidence, phrase_idx, phrase_sims))
                else:
                    category_id, confidence = classification
                    results.append((tip_id, category_id, confidence))
            except Exception as e:
                logger.error(f"Error classifying tip {tip_id}: {e}")
                # Skip tips that fail classification
                continue

        return results

    def should_assign_category(self, confidence: float) -> bool:
        """Check if confidence meets threshold for auto-assignment"""
        return confidence >= self.confidence_threshold


# Global instance
_category_classifier = None


def get_category_classifier() -> CategoryClassifier:
    """Get or create category classifier instance"""
    global _category_classifier
    if _category_classifier is None:
        _category_classifier = CategoryClassifier()
    return _category_classifier
