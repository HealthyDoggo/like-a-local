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

    def classify_tip(self, tip_embedding: List[float]) -> Tuple[str, float]:
        """
        Classify tip using cosine similarity.

        Args:
            tip_embedding: The embedding vector for the tip

        Returns:
            Tuple of (category_id, confidence_score)
        """
        if not self.categories:
            raise ValueError("Categories not loaded. Call load_categories() first.")

        if not tip_embedding:
            raise ValueError("Tip embedding cannot be empty")

        # Calculate similarity with each category
        similarities = {}
        for category in self.categories:
            try:
                similarity = self.embedding_service.similarity(
                    tip_embedding,
                    category.embedding
                )
                similarities[category.id] = similarity
            except Exception as e:
                logger.error(f"Error calculating similarity for category {category.id}: {e}")
                similarities[category.id] = 0.0

        # Find category with highest similarity
        if not similarities:
            raise ValueError("No similarities calculated")

        best_category_id = max(similarities.items(), key=lambda x: x[1])
        return best_category_id

    def classify_batch(self, tips_with_embeddings: List[Tuple[int, List[float]]]) -> List[Tuple[int, str, float]]:
        """
        Batch classification for efficiency.

        Args:
            tips_with_embeddings: List of (tip_id, embedding) tuples

        Returns:
            List of (tip_id, category_id, confidence_score) tuples
        """
        if not self.categories:
            raise ValueError("Categories not loaded. Call load_categories() first.")

        results = []
        for tip_id, embedding in tips_with_embeddings:
            try:
                category_id, confidence = self.classify_tip(embedding)
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
