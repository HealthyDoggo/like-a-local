"""Migration script to classify existing tips into categories"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import SessionLocal
from backend.database.models import Tip, Embedding, TipPromotion
from backend.services.category_classifier import get_category_classifier
from datetime import datetime
from sqlalchemy import func
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def classify_existing_tips(batch_size=100):
    """Classify all processed tips without categories"""
    db = SessionLocal()

    try:
        # Initialize classifier
        classifier = get_category_classifier()
        classifier.load_categories(db)

        # Get count of unclassified tips
        unclassified_count = db.query(Tip).join(Embedding).filter(
            Tip.status == "processed",
            Tip.category_id.is_(None)
        ).count()

        logger.info(f"Found {unclassified_count} unclassified tips")

        if unclassified_count == 0:
            logger.info("No tips to classify")
            return

        # Process in batches
        processed = 0
        classified = 0

        while True:
            # Get batch of unclassified tips with embeddings
            batch = db.query(Tip).join(Embedding).filter(
                Tip.status == "processed",
                Tip.category_id.is_(None)
            ).limit(batch_size).all()

            if not batch:
                break

            for tip in batch:
                embedding_obj = db.query(Embedding).filter(
                    Embedding.tip_id == tip.id
                ).first()

                if embedding_obj:
                    try:
                        category_id, confidence = classifier.classify_tip(
                            embedding_obj.embedding
                        )

                        if classifier.should_assign_category(confidence):
                            tip.category_id = category_id
                            tip.category_confidence = confidence
                            tip.category_assigned_at = datetime.utcnow()
                            classified += 1
                    except Exception as e:
                        logger.error(f"Error classifying tip {tip.id}: {e}")

                processed += 1

            # Commit batch
            db.commit()
            logger.info(f"Progress: {processed}/{unclassified_count} processed, {classified} classified")

        logger.info(f"\n✓ Classification complete: {classified}/{processed} tips classified")

        # Now classify promoted tips based on most common category
        classify_promoted_tips(db)

    except Exception as e:
        logger.error(f"Error classifying tips: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def classify_promoted_tips(db):
    """Classify promoted tips based on most common category in their source tips"""
    logger.info("\nClassifying promoted tips...")

    # Get all promotions without categories
    promotions = db.query(TipPromotion).filter(
        TipPromotion.category_id.is_(None)
    ).all()

    logger.info(f"Found {len(promotions)} unclassified promotions")

    classified = 0
    for promotion in promotions:
        # Find tips similar to this promotion (by location and text similarity)
        # For simplicity, we'll use tips at the same location that match closely
        similar_tips = db.query(Tip).filter(
            Tip.location_id == promotion.location_id,
            Tip.status == "processed",
            Tip.category_id.isnot(None)
        ).all()

        if not similar_tips:
            continue

        # Count categories
        category_counts = {}
        for tip in similar_tips:
            if tip.category_id:
                category_counts[tip.category_id] = category_counts.get(tip.category_id, 0) + 1

        # Assign most common category
        if category_counts:
            most_common = max(category_counts.items(), key=lambda x: x[1])[0]
            promotion.category_id = most_common
            classified += 1

    db.commit()
    logger.info(f"✓ Classified {classified}/{len(promotions)} promotions")


if __name__ == "__main__":
    classify_existing_tips()
