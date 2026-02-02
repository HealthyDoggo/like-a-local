"""Initialize categories table with predefined categories and embeddings"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import SessionLocal
from backend.database.models import Category
from backend.services.embedding import get_embedding_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Category definitions with descriptions optimized for semantic similarity
CATEGORIES = [
    {
        "id": "everyday-etiquette",
        "title": "Everyday Etiquette",
        "description": "Social norms, proper greetings, acceptable gestures, dress codes, polite behavior in public, body language, personal space, eye contact, handshakes, bowing, removing shoes, appropriate clothing for different settings",
        "icon_name": "handshake",
        "color": "#4A90E2",
        "display_order": 1
    },
    {
        "id": "food-dining",
        "title": "Food & Dining",
        "description": "Restaurant etiquette, tipping customs, meal timing, table manners, dining protocols, chopstick usage, how to order food, eating with hands, food sharing, paying the bill, breakfast lunch dinner times, cafe culture, street food",
        "icon_name": "utensils",
        "color": "#E94B3C",
        "display_order": 2
    },
    {
        "id": "getting-around",
        "title": "Getting Around",
        "description": "Transportation options, public transit, taxis, ride-sharing, buses, trains, subways, metro, driving, parking, walking, cycling, navigation, maps, getting from place to place, commuting, traffic, road rules",
        "icon_name": "bus",
        "color": "#F39C12",
        "display_order": 3
    },
    {
        "id": "public-spaces",
        "title": "Public Spaces",
        "description": "Behavior in parks, museums, galleries, religious sites, temples, churches, mosques, libraries, theaters, cinemas, shared spaces, quiet zones, photography rules, entry requirements, respect in sacred places",
        "icon_name": "landmark",
        "color": "#9B59B6",
        "display_order": 4
    },
    {
        "id": "social-interactions",
        "title": "Social Interactions",
        "description": "Making friends, conversation topics, small talk, meeting locals, dating culture, friendships, social gatherings, parties, networking, interpersonal relationships, talking to strangers, building connections",
        "icon_name": "users",
        "color": "#1ABC9C",
        "display_order": 5
    },
    {
        "id": "cultural-customs",
        "title": "Cultural Customs",
        "description": "Holidays, festivals, celebrations, traditional ceremonies, religious practices, cultural events, national traditions, rituals, customs specific to the culture, special occasions, observances, cultural heritage",
        "icon_name": "calendar-star",
        "color": "#E67E22",
        "display_order": 6
    },
    {
        "id": "locals-appreciate",
        "title": "Locals Appreciate",
        "description": "Respectful behaviors, cultural appreciation, learning local language, attempting to speak the language, respecting traditions, being mindful, showing interest in culture, polite gestures locals love, what makes you a good visitor",
        "icon_name": "heart",
        "color": "#E91E63",
        "display_order": 7
    },
    {
        "id": "misunderstandings",
        "title": "Common Misunderstandings",
        "description": "Tourist mistakes, cultural misinterpretations, things travelers get wrong, common misconceptions, faux pas, embarrassing errors, what not to do, offensive behaviors to avoid, cultural blunders, awkward situations",
        "icon_name": "alert-triangle",
        "color": "#FF6B6B",
        "display_order": 8
    },
    {
        "id": "helpful-tips",
        "title": "Helpful Tips",
        "description": "Practical advice, safety tips, money matters, currency, ATMs, local secrets, insider knowledge, useful information, things to know, life hacks, smart strategies, bargaining, shopping, SIM cards, WiFi",
        "icon_name": "lightbulb",
        "color": "#FFC107",
        "display_order": 9
    }
]


def init_categories():
    """Initialize categories with embeddings"""
    db = SessionLocal()
    embedding_service = get_embedding_service()

    try:
        # Check if categories already exist
        existing_count = db.query(Category).count()
        if existing_count > 0:
            logger.info(f"Categories already exist ({existing_count} found). Skipping initialization.")
            logger.info("If you want to reinitialize, delete existing categories first.")
            return

        logger.info("Initializing categories...")

        # Generate embeddings for all category descriptions
        descriptions = [cat["description"] for cat in CATEGORIES]
        logger.info(f"Generating embeddings for {len(descriptions)} categories...")
        embeddings = embedding_service.embed_batch(descriptions)

        # Create category records
        for i, category_data in enumerate(CATEGORIES):
            category = Category(
                id=category_data["id"],
                title=category_data["title"],
                description=category_data["description"],
                embedding=embeddings[i],
                icon_name=category_data["icon_name"],
                color=category_data["color"],
                display_order=category_data["display_order"]
            )
            db.add(category)
            logger.info(f"✓ Added category: {category_data['title']}")

        db.commit()
        logger.info(f"\n✓ Successfully initialized {len(CATEGORIES)} categories")

        # Verify
        count = db.query(Category).count()
        logger.info(f"✓ Verified: {count} categories in database")

    except Exception as e:
        logger.error(f"Error initializing categories: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_categories()
