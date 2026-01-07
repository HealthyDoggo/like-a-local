"""
Script to populate database with test tips specifically designed to test promotion system.
This creates multiple similar tips for the same location to trigger the promotion logic.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from backend.database.connection import SessionLocal
from backend.database.models import Location, Tip
from backend.config import settings


# Tips grouped by theme to test similarity clustering
PROMOTION_TEST_TIPS = [
    # Paris - Tourist Traps (5 similar tips)
    {
        "tip_text": "Avoid the overpriced restaurants right next to the Eiffel Tower",
        "location_name": "Paris",
        "location_country": "France",
        "language": "en"
    },
    {
        "tip_text": "Skip the tourist trap restaurants near Eiffel Tower, they're expensive",
        "location_name": "Paris",
        "location_country": "France",
        "language": "en"
    },
    {
        "tip_text": "Don't eat at restaurants directly by the Eiffel Tower - total tourist traps",
        "location_name": "Paris",
        "location_country": "France",
        "language": "en"
    },
    {
        "tip_text": "Stay away from Eiffel Tower area restaurants, overpriced for tourists",
        "location_name": "Paris",
        "location_country": "France",
        "language": "en"
    },
    {
        "tip_text": "The restaurants around Eiffel Tower are tourist traps with high prices",
        "location_name": "Paris",
        "location_country": "France",
        "language": "en"
    },

    # Paris - Metro Safety (4 similar tips)
    {
        "tip_text": "Watch out for pickpockets on the metro, especially during rush hour",
        "location_name": "Paris",
        "location_country": "France",
        "language": "en"
    },
    {
        "tip_text": "Be careful of pickpockets in the Paris metro system",
        "location_name": "Paris",
        "location_country": "France",
        "language": "en"
    },
    {
        "tip_text": "Keep your belongings close on the metro - pickpockets are common",
        "location_name": "Paris",
        "location_country": "France",
        "language": "en"
    },
    {
        "tip_text": "Metro pickpockets are a real issue, stay alert with your bags",
        "location_name": "Paris",
        "location_country": "France",
        "language": "en"
    },

    # Paris - Greeting Etiquette (3 similar tips)
    {
        "tip_text": "Always say bonjour when entering shops - it's considered rude not to",
        "location_name": "Paris",
        "location_country": "France",
        "language": "en"
    },
    {
        "tip_text": "Greet shopkeepers with bonjour, locals expect this basic courtesy",
        "location_name": "Paris",
        "location_country": "France",
        "language": "en"
    },
    {
        "tip_text": "Say bonjour when you walk into any store - it's just polite in France",
        "location_name": "Paris",
        "location_country": "France",
        "language": "en"
    },

    # Tokyo - Train Cards (4 similar tips)
    {
        "tip_text": "Get a Suica or Pasmo card for trains - makes everything easier",
        "location_name": "Tokyo",
        "location_country": "Japan",
        "language": "en"
    },
    {
        "tip_text": "Buy a Suica card for easy train and subway travel",
        "location_name": "Tokyo",
        "location_country": "Japan",
        "language": "en"
    },
    {
        "tip_text": "Suica card is essential for public transportation in Tokyo",
        "location_name": "Tokyo",
        "location_country": "Japan",
        "language": "en"
    },
    {
        "tip_text": "Don't bother with paper tickets, get a Suica card immediately",
        "location_name": "Tokyo",
        "location_country": "Japan",
        "language": "en"
    },

    # Tokyo - Learn Basic Japanese (3 similar tips)
    {
        "tip_text": "Learn basic Japanese phrases - locals really appreciate the effort",
        "location_name": "Tokyo",
        "location_country": "Japan",
        "language": "en"
    },
    {
        "tip_text": "Try to speak some Japanese, even basic phrases are appreciated",
        "location_name": "Tokyo",
        "location_country": "Japan",
        "language": "en"
    },
    {
        "tip_text": "Know a few Japanese words like arigatou and sumimasen - it helps a lot",
        "location_name": "Tokyo",
        "location_country": "Japan",
        "language": "en"
    },

    # Barcelona - Late Dining (4 similar tips)
    {
        "tip_text": "Restaurants don't open for dinner until 9 PM - eat late like the locals",
        "location_name": "Barcelona",
        "location_country": "Spain",
        "language": "en"
    },
    {
        "tip_text": "Dinner starts at 9 PM or later in Barcelona, plan accordingly",
        "location_name": "Barcelona",
        "location_country": "Spain",
        "language": "en"
    },
    {
        "tip_text": "Don't expect to eat dinner before 9 PM, that's just how it is here",
        "location_name": "Barcelona",
        "location_country": "Spain",
        "language": "en"
    },
    {
        "tip_text": "Spanish dinner time is 9-10 PM, you'll look like a tourist eating at 6",
        "location_name": "Barcelona",
        "location_country": "Spain",
        "language": "en"
    },

    # Barcelona - Skip La Rambla (3 similar tips)
    {
        "tip_text": "La Rambla is overrated and full of tourists, explore other neighborhoods",
        "location_name": "Barcelona",
        "location_country": "Spain",
        "language": "en"
    },
    {
        "tip_text": "Avoid La Rambla for food - total tourist trap with bad restaurants",
        "location_name": "Barcelona",
        "location_country": "Spain",
        "language": "en"
    },
    {
        "tip_text": "Skip La Rambla, go to El Born or Gracia for authentic Barcelona",
        "location_name": "Barcelona",
        "location_country": "Spain",
        "language": "en"
    },

    # New York - Subway Card (4 similar tips)
    {
        "tip_text": "Get a MetroCard when you arrive, don't use single tickets",
        "location_name": "New York",
        "location_country": "United States",
        "language": "en"
    },
    {
        "tip_text": "Buy a weekly MetroCard if staying more than 3 days - saves money",
        "location_name": "New York",
        "location_country": "United States",
        "language": "en"
    },
    {
        "tip_text": "MetroCard is the way to go for subway travel in NYC",
        "location_name": "New York",
        "location_country": "United States",
        "language": "en"
    },
    {
        "tip_text": "Don't waste time buying single ride tickets, get a MetroCard",
        "location_name": "New York",
        "location_country": "United States",
        "language": "en"
    },

    # New York - Times Square (3 similar tips)
    {
        "tip_text": "Times Square is just for photos - don't eat or shop there",
        "location_name": "New York",
        "location_country": "United States",
        "language": "en"
    },
    {
        "tip_text": "Avoid Times Square restaurants, they're overpriced tourist traps",
        "location_name": "New York",
        "location_country": "United States",
        "language": "en"
    },
    {
        "tip_text": "Skip Times Square except for a quick photo - it's a tourist trap",
        "location_name": "New York",
        "location_country": "United States",
        "language": "en"
    },

    # London - Oyster Card (4 similar tips)
    {
        "tip_text": "Get an Oyster card for the Tube - much cheaper than buying tickets",
        "location_name": "London",
        "location_country": "United Kingdom",
        "language": "en"
    },
    {
        "tip_text": "Oyster card is essential for using London Underground efficiently",
        "location_name": "London",
        "location_country": "United Kingdom",
        "language": "en"
    },
    {
        "tip_text": "Don't buy individual tube tickets, get an Oyster card immediately",
        "location_name": "London",
        "location_country": "United Kingdom",
        "language": "en"
    },
    {
        "tip_text": "Oyster card saves time and money on all London public transport",
        "location_name": "London",
        "location_country": "United Kingdom",
        "language": "en"
    },

    # Mixed language tips for testing translation
    {
        "tip_text": "Évitez les restaurants touristiques près de la Tour Eiffel - trop chers",
        "location_name": "Paris",
        "location_country": "France",
        "language": "fr"
    },
    {
        "tip_text": "Suica カードを買って電車移動を簡単にしましょう",
        "location_name": "Tokyo",
        "location_country": "Japan",
        "language": "ja"
    },
    {
        "tip_text": "Los restaurantes no abren para cenar hasta las 9 PM",
        "location_name": "Barcelona",
        "location_country": "Spain",
        "language": "es"
    },
]


def get_or_create_location(db: Session, name: str, country: str) -> Location:
    """Get existing location or create new one"""
    location = db.query(Location).filter(
        Location.name == name,
        Location.country == country
    ).first()

    if not location:
        location = Location(name=name, country=country)
        db.add(location)
        db.commit()
        db.refresh(location)
        print(f"  ✓ Created location: {name}, {country}")

    return location


def create_tip(db: Session, tip_data: dict, location: Location) -> Tip:
    """Create a tip in the database"""
    tip = Tip(
        tip_text=tip_data["tip_text"],
        location_id=location.id,
        original_language=tip_data.get("language", "en"),
        status="pending"
    )
    db.add(tip)
    return tip


def populate_database(clear_first: bool = False):
    """Populate database with test tips designed to test promotion"""
    db = SessionLocal()

    try:
        if clear_first:
            print("⚠️  Clearing existing data...")
            from backend.database.models import TipPromotion, Embedding
            db.query(TipPromotion).delete()
            db.query(Embedding).delete()
            db.query(Tip).delete()
            db.query(Location).delete()
            db.commit()
            print("  ✓ Cleared all tips, embeddings, promotions, and locations\n")

        print(f"📝 Populating database with promotion test data...")
        print(f"   Total tips: {len(PROMOTION_TEST_TIPS)}\n")

        created_count = 0
        location_cache = {}

        for tip_data in PROMOTION_TEST_TIPS:
            # Get or create location
            loc_key = (tip_data["location_name"], tip_data["location_country"])
            if loc_key not in location_cache:
                location = get_or_create_location(
                    db,
                    tip_data["location_name"],
                    tip_data["location_country"]
                )
                location_cache[loc_key] = location
            else:
                location = location_cache[loc_key]

            # Create tip
            tip = create_tip(db, tip_data, location)
            created_count += 1

        # Commit all tips
        db.commit()

        print(f"\n✅ Successfully created {created_count} tips")
        print(f"   Locations: {len(location_cache)}")

        # Show summary
        pending_count = db.query(Tip).filter(Tip.status == "pending").count()
        processed_count = db.query(Tip).filter(Tip.status == "processed").count()

        print(f"\n📊 Database summary:")
        print(f"   Pending tips: {pending_count}")
        print(f"   Processed tips: {processed_count}")
        print(f"   Total tips: {pending_count + processed_count}")

        # Show tips by location
        print(f"\n📍 Tips by location:")
        for (name, country), location in location_cache.items():
            count = db.query(Tip).filter(Tip.location_id == location.id).count()
            print(f"   • {name}, {country}: {count} tips")

        print(f"\n💡 Next steps:")
        print(f"   1. Start PC processing service: python pc_processing_service.py")
        print(f"   2. Process tips: python -m backend.jobs.nightly_processor --no-wake")
        print(f"   3. Check promoted tips: curl 'http://localhost:8000/api/promoted-tips?location_name=Paris&location_country=France'")

    except Exception as e:
        db.rollback()
        print(f"❌ Error populating database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Populate database with promotion test data"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear all existing data before adding (WARNING: deletes everything!)"
    )

    args = parser.parse_args()

    populate_database(clear_first=args.clear)
