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
        base_query = db.query(TipPromotion)
        if location_id:
            base_query = base_query.filter(TipPromotion.location_id == location_id)
        all_promotions = base_query.all()

        if not all_promotions:
            print("No promoted tips found.")
            return

        # Always report NULL source_tip_id promotions upfront — these can never
        # be translated regardless of what else is done.
        null_source = [p for p in all_promotions if p.source_tip_id is None]
        if null_source:
            print(f"\n{'!'*70}")
            print(f"WARNING: {len(null_source)} promotion(s) have source_tip_id = NULL")
            print("These were created before the source_tip_id column was added and")
            print("will ALWAYS show in English. Fix: delete and recluster, or backfill.")
            print(f"{'!'*70}")
            for p in null_source[:5]:
                loc = db.query(Location).filter(Location.id == p.location_id).first()
                loc_label = f"{loc.name}, {loc.country}" if loc else f"location_id={p.location_id}"
                preview = p.tip_text[:70] + ("..." if len(p.tip_text) > 70 else "")
                print(f"  promotion_id={p.id}  [{loc_label}]  \"{preview}\"")
            if len(null_source) > 5:
                print(f"  ... and {len(null_source) - 5} more")

        promotions = [p for p in all_promotions if p.source_tip_id is not None]

        if not promotions:
            print("\nNo promotions with source_tip_id to inspect.")
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
            print(f"\nPromotions (with source_tip_id) missing '{missing_lang}' translation: {len(promotions)}")
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
        with_source = len([p for p in all_promotions if p.source_tip_id is not None])
        print(f"Sampled {len(sample)} of {with_source} promotions with source_tip_id "
              f"({len(null_source)} without source_tip_id skipped)")

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
