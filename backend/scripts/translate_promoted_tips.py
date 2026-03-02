"""
Translate promoted tips to all supported languages without re-running the full
nightly processor.

Use this when promoted tips are missing multi-language translations — for
example after running reset_tips_for_reprocessing and then the nightly job,
or any time tips appear in English when another language is requested.

Only promoted tips (those with a TipPromotion record) receive multi-language
translations. Regular tips fall back to their English translated_text on the
frontend; this script does not change that behaviour.

Usage:
    # Dry run — show how many promoted tips are missing translations
    python -m backend.scripts.translate_promoted_tips

    # Translate all promoted tips that are missing any language
    python -m backend.scripts.translate_promoted_tips --confirm

    # Limit to a specific location
    python -m backend.scripts.translate_promoted_tips --location-id 5 --confirm

    # Force re-translation even for tips that already have translations
    python -m backend.scripts.translate_promoted_tips --force --confirm
"""
import sys
import os
import argparse
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import SessionLocal
from backend.database.models import Tip, TipPromotion, TipTranslation
from backend.services.processing_client import get_processing_client
from backend.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def translate_promoted_tips(
    confirm: bool = False,
    location_id: int = None,
    force: bool = False,
) -> None:
    db = SessionLocal()
    try:
        # Find all promotions that have a source tip
        query = db.query(TipPromotion).filter(TipPromotion.source_tip_id.isnot(None))
        if location_id:
            query = query.filter(TipPromotion.location_id == location_id)
        promotions = query.all()

        # Collect unique source tip IDs
        source_tip_ids = list({p.source_tip_id for p in promotions})
        logger.info(f"Found {len(promotions)} promotions with {len(source_tip_ids)} unique source tips")

        all_languages = set(settings.supported_languages)

        # Determine which tips need translation
        to_translate: list[Tip] = []
        missing_by_tip: dict[int, set] = {}

        for tip_id in source_tip_ids:
            tip = db.query(Tip).filter(Tip.id == tip_id).first()
            if not tip:
                logger.warning(f"Source tip {tip_id} not found in database")
                continue
            if not tip.translated_text and not tip.tip_text:
                logger.warning(f"Tip {tip_id} has no text — skipping")
                continue

            if force:
                missing = all_languages
            else:
                existing_langs = {
                    t.language_code
                    for t in db.query(TipTranslation).filter(
                        TipTranslation.tip_id == tip_id
                    ).all()
                }
                missing = all_languages - existing_langs

            if missing:
                to_translate.append(tip)
                missing_by_tip[tip_id] = missing

        print(f"Promoted tips missing translations: {len(to_translate)}")

        if not confirm:
            print("Dry run — pass --confirm to actually translate")
            if to_translate:
                print("\nSample of tips that would be translated:")
                for tip in to_translate[:5]:
                    preview = (tip.translated_text or tip.tip_text or "")[:70]
                    missing = sorted(missing_by_tip[tip.id])
                    print(f"  tip_id={tip.id}: missing {missing}")
                    print(f"    text: {preview}")
            return

        if not to_translate:
            print("Nothing to do.")
            return

        client = get_processing_client()
        if not client.health_check():
            print("Error: PC processing service is not available")
            sys.exit(1)

        other_languages = [lang for lang in settings.supported_languages if lang != "en"]
        english_texts = [t.translated_text or t.tip_text for t in to_translate]

        logger.info(
            f"Translating {len(to_translate)} tips into {len(other_languages)} languages "
            f"via translate-multi-batch..."
        )
        batch_translations = client.translate_multi_batch(
            texts=english_texts,
            source_language="en",
            target_languages=other_languages,
        )

        for tip_idx, tip in enumerate(to_translate):
            missing_langs = missing_by_tip[tip.id]

            # English
            if "en" in missing_langs:
                if force:
                    db.query(TipTranslation).filter(
                        TipTranslation.tip_id == tip.id,
                        TipTranslation.language_code == "en",
                    ).delete(synchronize_session=False)
                db.add(TipTranslation(
                    tip_id=tip.id,
                    language_code="en",
                    translated_text=english_texts[tip_idx],
                ))

            # Original language (store the raw source text)
            orig = tip.original_language
            if orig and orig != "en" and orig in missing_langs:
                if force:
                    db.query(TipTranslation).filter(
                        TipTranslation.tip_id == tip.id,
                        TipTranslation.language_code == orig,
                    ).delete(synchronize_session=False)
                db.add(TipTranslation(
                    tip_id=tip.id,
                    language_code=orig,
                    translated_text=tip.tip_text,
                ))

            # All other target languages from the batch response
            for lang_code, translated_list in batch_translations.items():
                if lang_code not in missing_langs:
                    continue
                if tip_idx < len(translated_list) and translated_list[tip_idx]:
                    if force:
                        db.query(TipTranslation).filter(
                            TipTranslation.tip_id == tip.id,
                            TipTranslation.language_code == lang_code,
                        ).delete(synchronize_session=False)
                    db.add(TipTranslation(
                        tip_id=tip.id,
                        language_code=lang_code,
                        translated_text=translated_list[tip_idx],
                    ))

        db.commit()
        print(f"Successfully translated {len(to_translate)} promoted tips")

    except Exception as e:
        logger.error(f"Translation failed: {e}", exc_info=True)
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description="Translate promoted tips to all supported languages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run — see what's missing
  python -m backend.scripts.translate_promoted_tips

  # Translate everything missing
  python -m backend.scripts.translate_promoted_tips --confirm

  # Translate for one location only
  python -m backend.scripts.translate_promoted_tips --location-id 5 --confirm

  # Re-translate everything even if translations already exist
  python -m backend.scripts.translate_promoted_tips --force --confirm
        """,
    )
    parser.add_argument("--confirm", action="store_true", help="Actually write translations (default: dry run)")
    parser.add_argument("--location-id", type=int, help="Limit to a specific location ID")
    parser.add_argument("--force", action="store_true", help="Re-translate even if translations already exist")
    args = parser.parse_args()

    translate_promoted_tips(
        confirm=args.confirm,
        location_id=args.location_id,
        force=args.force,
    )


if __name__ == "__main__":
    main()
