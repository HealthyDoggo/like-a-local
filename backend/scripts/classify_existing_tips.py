"""Script to classify existing tips into categories using embedding or LLM method"""
import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import SessionLocal
from backend.database.models import Tip, Embedding, TipPromotion
from backend.services.category_classifier import get_category_classifier
from backend.services.llm_classifier import get_llm_classifier
from backend.config import settings
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def classify_existing_tips(batch_size=100, method=None, force=False):
    """Classify processed tips. With --force, reclassifies all tips (keeps embeddings/translations)."""
    db = SessionLocal()
    use_llm = (method or settings.classification_method) == "llm"

    try:
        if use_llm:
            classifier = get_llm_classifier()
        else:
            classifier = get_category_classifier()
        classifier.load_categories(db)

        logger.info(f"Classification method: {'llm' if use_llm else 'embedding'}")

        if force:
            reset_count = db.query(Tip).filter(
                Tip.status == "processed",
                Tip.category_assigned_at.isnot(None)
            ).update({
                Tip.category_id: None,
                Tip.category_confidence: None,
                Tip.category_assigned_at: None,
                Tip.category_manual: False,
            }, synchronize_session="fetch")

            promo_reset = db.query(TipPromotion).filter(
                TipPromotion.category_id.isnot(None)
            ).update({TipPromotion.category_id: None}, synchronize_session="fetch")

            db.commit()
            logger.info(f"Force mode: reset categories on {reset_count} tips and {promo_reset} promotions")

        base_query = db.query(Tip).filter(
            Tip.status == "processed",
            Tip.category_assigned_at.is_(None)
        )
        if not use_llm:
            base_query = base_query.join(Embedding)

        unclassified_count = base_query.count()
        logger.info(f"Found {unclassified_count} tips to classify")

        if unclassified_count == 0:
            logger.info("No tips to classify")
            return

        processed = 0
        classified = 0

        while True:
            query = db.query(Tip).filter(
                Tip.status == "processed",
                Tip.category_assigned_at.is_(None)
            )
            if not use_llm:
                query = query.join(Embedding)
            batch = query.limit(batch_size).all()

            if not batch:
                break

            for tip in batch:
                try:
                    if use_llm:
                        text = tip.translated_text or tip.tip_text
                        category_id, confidence = classifier.classify_tip(text)
                    else:
                        embedding_obj = db.query(Embedding).filter(
                            Embedding.tip_id == tip.id
                        ).first()
                        if not embedding_obj:
                            processed += 1
                            continue
                        category_id, confidence, phrase_idx, phrase_sims = classifier.classify_tip(
                            embedding_obj.embedding,
                            return_details=True
                        )

                    tip.category_assigned_at = datetime.utcnow()

                    if category_id and classifier.should_assign_category(confidence):
                        tip.category_id = category_id
                        tip.category_confidence = confidence
                        classified += 1

                        if use_llm:
                            logger.info(
                                f"Tip {tip.id}: '{tip.tip_text[:60]}...' -> "
                                f"{category_id} (confidence: {confidence:.3f})"
                            )
                        else:
                            category = next((c for c in classifier.categories if c.id == category_id), None)
                            matching_phrase = category.description[phrase_idx] if category else "unknown"
                            logger.info(
                                f"Tip {tip.id}: '{tip.tip_text[:60]}...' -> "
                                f"{category_id} (confidence: {confidence:.3f}, "
                                f"matched phrase: '{matching_phrase}')"
                            )
                    else:
                        if use_llm:
                            logger.info(
                                f"Tip {tip.id}: '{tip.tip_text[:60]}...' -> "
                                f"{category_id} (confidence: {confidence:.3f} too low, not assigned)"
                            )
                        else:
                            category = next((c for c in classifier.categories if c.id == category_id), None)
                            matching_phrase = category.description[phrase_idx] if category else "unknown"
                            logger.info(
                                f"Tip {tip.id}: '{tip.tip_text[:60]}...' -> "
                                f"{category_id} (confidence: {confidence:.3f} too low, "
                                f"matched phrase: '{matching_phrase}', not assigned)"
                            )
                except Exception as e:
                    logger.error(f"Error classifying tip {tip.id}: {e}")

                processed += 1

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
    parser = argparse.ArgumentParser(description="Classify existing tips into categories")
    parser.add_argument(
        "--method",
        choices=["embedding", "llm"],
        default=None,
        help=f"Classification method (default: from CLASSIFICATION_METHOD env, currently '{settings.classification_method}')"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Number of tips per batch (default: 100)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Reclassify all tips, not just unclassified ones (keeps embeddings and translations)"
    )
    args = parser.parse_args()
    classify_existing_tips(batch_size=args.batch_size, method=args.method, force=args.force)
