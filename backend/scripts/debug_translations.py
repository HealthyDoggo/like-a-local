"""
Show a random sample of promoted tips and their translations for debugging.

Usage:
    # Random 10 promoted tips
    python -m backend.scripts.debug_translations

    # Custom sample size
    python -m backend.scripts.debug_translations --count 20

    # Filter by location
    python -m backend.scripts.debug_translations --location-id 5

    # Show only tips missing translations for a specific language
    python -m backend.scripts.debug_translations --missing-lang es
"""
import sys
import os
import argparse
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import SessionLocal
from backend.database.models import Tip, TipPromotion, TipTranslation, Location
from backend.config import settings


def debug_translations(count: int = 10, location_id: int = None, missing_lang: str = None):
    db = SessionLocal()
    try:
        query = db.query(TipPromotion).filter(TipPromotion.source_tip_id.isnot(None))
        if location_id:
            query = query.filter(TipPromotion.location_id == location_id)
        promotions = query.all()

        if not promotions:
            print("No promoted tips found.")
            return

        if missing_lang:
            # Filter to only promotions whose source tip is missing this language
            filtered = []
            for promo in promotions:
                has_lang = db.query(TipTranslation).filter(
                    TipTranslation.tip_id == promo.source_tip_id,
                    TipTranslation.language_code == missing_lang,
                ).first()
                if not has_lang:
                    filtered.append(promo)
            promotions = filtered
            print(f"Promotions missing '{missing_lang}' translation: {len(promotions)}")
            if not promotions:
                return

        sample = random.sample(promotions, min(count, len(promotions)))

        all_langs = settings.supported_languages

        for i, promo in enumerate(sample, 1):
            tip = db.query(Tip).filter(Tip.id == promo.source_tip_id).first()
            location = db.query(Location).filter(Location.id == promo.location_id).first()
            loc_label = f"{location.name}, {location.country}" if location else f"location_id={promo.location_id}"

            translations = {
                t.language_code: t.translated_text
                for t in db.query(TipTranslation).filter(
                    TipTranslation.tip_id == promo.source_tip_id
                ).all()
            }

            print(f"\n{'='*70}")
            print(f"[{i}/{len(sample)}] promotion_id={promo.id}  source_tip_id={promo.source_tip_id}")
            print(f"  Location : {loc_label}")
            print(f"  Mentions : {promo.mention_count}")
            if tip:
                print(f"  Original : [{tip.original_language or '?'}] {tip.tip_text}")
                print(f"  English  : {tip.translated_text or '(none)'}")
            else:
                print(f"  Source tip NOT FOUND in database")

            print(f"  TipTranslation rows ({len(translations)}/{len(all_langs)} languages):")
            for lang in all_langs:
                text = translations.get(lang)
                if text:
                    preview = text[:80] + ("..." if len(text) > 80 else "")
                    print(f"    [{lang}] {preview}")
                else:
                    print(f"    [{lang}] MISSING")

        print(f"\n{'='*70}")
        print(f"Sampled {len(sample)} of {len(promotions)} promoted tips")

    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Debug promoted tip translations")
    parser.add_argument("--count", type=int, default=10, help="Number of tips to sample (default: 10)")
    parser.add_argument("--location-id", type=int, help="Filter by location ID")
    parser.add_argument("--missing-lang", help="Only show tips missing this language code (e.g. es)")
    args = parser.parse_args()

    debug_translations(
        count=args.count,
        location_id=args.location_id,
        missing_lang=args.missing_lang,
    )


if __name__ == "__main__":
    main()
