"""
Seed the database with LLM-generated travel tips using Gemini 2.5 Flash.

For each location in the DB, asks Gemini to produce realistic, specific tips
that a local would actually share with a visitor. Tips are inserted as
status='pending' so they flow through the normal nightly processing pipeline
(translation, embedding, classification, promotion).

Locations are processed in batches so multiple cities are sent in a single
Gemini call, reducing API round-trips and latency.

Usage:
    python -m backend.scripts.seed_llm_tips --confirm
    python -m backend.scripts.seed_llm_tips --confirm --locations "Tokyo,Paris"
    python -m backend.scripts.seed_llm_tips --confirm --tips-per-location 15
    python -m backend.scripts.seed_llm_tips --confirm --max-locations 5
    python -m backend.scripts.seed_llm_tips --confirm --batch-size 3
"""
import argparse
import json
import logging
import time
from typing import List

from sqlalchemy.orm import Session
from backend.database.connection import SessionLocal
from backend.database.models import Location, Tip, Category
from backend.services.gemini_client import gemini_generate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-2.5-flash"
DEFAULT_BATCH_SIZE = 5

SUPPORTED_LANGUAGES = [
    ("en", "English"),
    ("es", "Spanish"),
    ("fr", "French"),
    ("de", "German"),
    ("it", "Italian"),
    ("pt", "Portuguese"),
    ("ja", "Japanese"),
    ("ko", "Korean"),
    ("zh", "Chinese"),
    ("ar", "Arabic"),
    ("hi", "Hindi"),
    ("th", "Thai"),
    ("vi", "Vietnamese"),
    ("id", "Indonesian"),
    ("ru", "Russian"),
]


def _build_batch_prompt(
    locations: List[Location],
    categories: List[Category],
    tips_per_location: int,
    languages: List[tuple],
) -> str:
    cat_lines = [f"- {cat.title}" for cat in categories]
    categories_block = "\n".join(cat_lines)

    lang_examples = ", ".join(
        f"{name} ({code})" for code, name in languages[:6]
    )

    location_lines = []
    for loc in locations:
        location_lines.append(f'  {{"id": {loc.id}, "city": "{loc.name}", "country": "{loc.country}"}}')
    locations_block = ",\n".join(location_lines)

    return f"""You are a knowledgeable local travel guide.

For EACH location below, generate exactly {tips_per_location} realistic travel tips that a local resident would share with a first-time visitor. Each tip must be specific to that city — mention real place names, neighbourhoods, customs, or practical details whenever possible.

Vary the tips across these categories (you don't need to cover every one):
{categories_block}

Write most tips in English, but write some tips in other languages that would be natural for that city. For example, tips for Tokyo could be in Japanese, tips for Paris in French, etc. Available languages: {lang_examples}, and others.

For each tip, pick a language that feels authentic — a local giving advice in their own tongue.

Locations:
[
{locations_block}
]

Respond with ONLY a JSON array (one entry per location, same order), no markdown fences:
[
  {{
    "id": <location_id>,
    "tips": [
      {{"tip_text": "...", "language": "en"}},
      {{"tip_text": "...", "language": "ja"}},
      ...
    ]
  }},
  ...
]

Rules:
- Generate exactly {tips_per_location} tips per location
- Each tip should be 1-2 sentences, practical, and specific to that city
- Avoid generic advice that applies to any city
- Include a mix of well-known and insider/lesser-known tips
- For non-English tips, write them naturally in that language (not a translation of English)
"""


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def seed_llm_tips(
    locations_filter: List[str] | None = None,
    tips_per_location: int = 10,
    max_locations: int | None = None,
    batch_size: int = DEFAULT_BATCH_SIZE,
):
    db: Session = SessionLocal()
    try:
        categories = db.query(Category).order_by(Category.display_order).all()
        if not categories:
            logger.warning("No categories in DB — tips will still be generated but uncategorised")

        query = db.query(Location)
        if locations_filter:
            query = query.filter(Location.name.in_(locations_filter))
        locations = query.all()

        if max_locations:
            locations = locations[:max_locations]

        if not locations:
            print("No locations found in the database.")
            return

        batches = [locations[i:i + batch_size] for i in range(0, len(locations), batch_size)]
        print(f"Generating tips for {len(locations)} location(s) in {len(batches)} batch(es), "
              f"{tips_per_location} tips each...\n")

        total_created = 0

        for batch_idx, batch in enumerate(batches, start=1):
            batch_names = ", ".join(loc.name for loc in batch)
            print(f"  Batch {batch_idx}/{len(batches)}: {batch_names}")

            prompt = _build_batch_prompt(
                locations=batch,
                categories=categories,
                tips_per_location=tips_per_location,
                languages=SUPPORTED_LANGUAGES,
            )

            try:
                response = gemini_generate(model=GEMINI_MODEL, contents=prompt)
                items = json.loads(_strip_fences(response.text))
            except Exception as e:
                logger.error(f"Failed to generate tips for batch {batch_idx}: {e}")
                continue

            loc_map = {loc.id: loc for loc in batch}
            batch_created = 0

            for entry in items:
                try:
                    loc_id = int(entry["id"])
                    tips_data = entry.get("tips", [])
                except (KeyError, ValueError, TypeError) as e:
                    logger.warning(f"Skipping malformed batch entry: {entry} ({e})")
                    continue

                if loc_id not in loc_map:
                    logger.warning(f"Response contained unexpected location id {loc_id}, skipping")
                    continue

                loc = loc_map[loc_id]
                loc_count = 0
                for item in tips_data:
                    tip_text = item.get("tip_text", "").strip()
                    language = item.get("language", "en").strip()
                    if not tip_text:
                        continue

                    db.add(Tip(
                        tip_text=tip_text,
                        location_id=loc.id,
                        original_language=language,
                        status="pending",
                    ))
                    loc_count += 1

                batch_created += loc_count
                print(f"    {loc.name}, {loc.country}: {loc_count} tips")

            db.commit()
            total_created += batch_created

            if batch_idx < len(batches):
                time.sleep(1)

        print(f"\nDone — {total_created} tips created as 'pending'.")
        print("Run the nightly processor to translate, embed, and classify them.")

    except Exception as e:
        db.rollback()
        logger.error(f"Seeding error: {e}", exc_info=True)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Seed database with LLM-generated travel tips"
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        required=True,
        help="Confirm you want to seed tips (required)",
    )
    parser.add_argument(
        "--locations",
        type=str,
        default=None,
        help='Comma-separated list of city names to seed (default: all)',
    )
    parser.add_argument(
        "--tips-per-location",
        type=int,
        default=10,
        help="Number of tips to generate per location (default: 10)",
    )
    parser.add_argument(
        "--max-locations",
        type=int,
        default=None,
        help="Maximum number of locations to process (default: all)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help=f"Number of locations per Gemini call (default: {DEFAULT_BATCH_SIZE})",
    )

    args = parser.parse_args()

    locations_filter = None
    if args.locations:
        locations_filter = [s.strip() for s in args.locations.split(",")]

    seed_llm_tips(
        locations_filter=locations_filter,
        tips_per_location=args.tips_per_location,
        max_locations=args.max_locations,
        batch_size=args.batch_size,
    )
