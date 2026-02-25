"""
Reset processed tips back to 'pending' so they are re-embedded and re-translated.

Use this after fixing the embedding ordering bug in process_batch_concurrent,
which could cause tips to receive each other's embeddings and translated_text
when batches completed out of order.

Usage:
    python -m backend.scripts.reset_tips_for_reprocessing           # dry run
    python -m backend.scripts.reset_tips_for_reprocessing --confirm # actually reset
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import SessionLocal
from backend.database.models import Tip, Embedding, TipTranslation, TipPromotion


def reset_for_reprocessing(confirm: bool = False):
    db = SessionLocal()
    try:
        tips = db.query(Tip).filter(Tip.status == "processed").all()
        print(f"Found {len(tips)} processed tips to reset")

        if not confirm:
            print("Dry run — pass --confirm to actually reset")
            return

        tip_ids = [t.id for t in tips]

        # Delete embeddings (will be regenerated)
        deleted_embeddings = db.query(Embedding).filter(
            Embedding.tip_id.in_(tip_ids)
        ).delete(synchronize_session=False)

        # Delete translations (will be regenerated)
        deleted_translations = db.query(TipTranslation).filter(
            TipTranslation.tip_id.in_(tip_ids)
        ).delete(synchronize_session=False)

        # Reset tip fields and status
        for tip in tips:
            tip.status = "pending"
            tip.translated_text = None
            tip.original_language = None
            tip.processed_at = None
            tip.category_id = None
            tip.category_confidence = None
            tip.category_assigned_at = None

        db.commit()
        print(f"Reset {len(tips)} tips to 'pending'")
        print(f"Deleted {deleted_embeddings} embeddings")
        print(f"Deleted {deleted_translations} translations")
        print("Run the nightly processor to reprocess.")

        # Reset promotions
        deleted_promotions = db.query(TipPromotion).filter(
            TipPromotion.tip_id.in_(tip_ids)
        ).delete(synchronize_session=False)

        print(f"Deleted {deleted_promotions} promotions")

    finally:
        db.close()


if __name__ == "__main__":
    confirm = "--confirm" in sys.argv
    reset_for_reprocessing(confirm=confirm)
