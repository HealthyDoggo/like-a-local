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


# Category definitions with multiple description phrases for better semantic matching
CATEGORIES = [
    {
        "id": "everyday-etiquette",
        "title": "Everyday Etiquette",
        "descriptions": [
            "Social norms and proper greetings",
            "Acceptable gestures and body language",
            "Dress codes and appropriate clothing for different settings",
            "Polite behavior in public, personal space, eye contact",
            "Handshakes, bowing, removing shoes indoors"
        ],
        "icon_name": "handshake",
        "color": "#4A90E2",
        "display_order": 1
    },
    {
        "id": "food-dining",
        "title": "Food & Dining",
        "descriptions": [
            "Restaurant etiquette and tipping customs",
            "Table manners and dining protocols",
            "Chopstick usage and eating with hands",
            "Meal timing, breakfast lunch dinner schedules",
            "How to order food, paying the bill, food sharing",
            "Cafe culture and street food"
        ],
        "icon_name": "utensils",
        "color": "#E94B3C",
        "display_order": 2
    },
    {
        "id": "getting-around",
        "title": "Getting Around",
        "descriptions": [
            "Public transit, buses, trains, subways, metro systems",
            "Taxis and ride-sharing services",
            "Driving, parking, and road rules",
            "Walking and cycling in the city",
            "Navigation, maps, and getting from place to place"
        ],
        "icon_name": "bus",
        "color": "#F39C12",
        "display_order": 3
    },
    {
        "id": "public-spaces",
        "title": "Public Spaces",
        "descriptions": [
            "Behavior in parks, museums, and galleries",
            "Religious sites, temples, churches, mosques",
            "Libraries, theaters, and cinemas",
            "Photography rules and entry requirements",
            "Respect in sacred places and quiet zones"
        ],
        "icon_name": "landmark",
        "color": "#9B59B6",
        "display_order": 4
    },
    {
        "id": "social-interactions",
        "title": "Social Interactions",
        "descriptions": [
            "Making friends and meeting locals",
            "Conversation topics and small talk",
            "Dating culture and interpersonal relationships",
            "Social gatherings, parties, and networking",
            "Talking to strangers and building connections"
        ],
        "icon_name": "users",
        "color": "#1ABC9C",
        "display_order": 5
    },
    {
        "id": "cultural-customs",
        "title": "Cultural Customs",
        "descriptions": [
            "Holidays, festivals, and celebrations",
            "Traditional ceremonies and rituals",
            "Religious practices and observances",
            "National traditions and cultural events",
            "Cultural heritage and special occasions"
        ],
        "icon_name": "calendar-star",
        "color": "#E67E22",
        "display_order": 6
    },
    {
        "id": "locals-appreciate",
        "title": "Locals Appreciate",
        "descriptions": [
            "Respectful behaviors and cultural appreciation",
            "Learning and attempting to speak the local language",
            "Respecting traditions and being mindful",
            "Showing interest in local culture",
            "Polite gestures that locals love"
        ],
        "icon_name": "heart",
        "color": "#E91E63",
        "display_order": 7
    },
    {
        "id": "misunderstandings",
        "title": "Common Misunderstandings",
        "descriptions": [
            "Tourist mistakes and common misconceptions",
            "Cultural misinterpretations and faux pas",
            "Things travelers get wrong",
            "Embarrassing errors and awkward situations",
            "Offensive behaviors to avoid and cultural blunders"
        ],
        "icon_name": "alert-triangle",
        "color": "#FF6B6B",
        "display_order": 8
    },
    {
        "id": "helpful-tips",
        "title": "Helpful Tips",
        "descriptions": [
            "Practical advice and safety tips",
            "Money matters, currency, and ATMs",
            "Local secrets and insider knowledge",
            "Bargaining, shopping, and smart strategies",
            "SIM cards, WiFi, and staying connected"
        ],
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

        # Generate embeddings for all category description phrases
        all_descriptions = []
        category_phrase_counts = []

        for cat in CATEGORIES:
            descriptions = cat["descriptions"]
            all_descriptions.extend(descriptions)
            category_phrase_counts.append(len(descriptions))

        logger.info(f"Generating embeddings for {len(all_descriptions)} description phrases across {len(CATEGORIES)} categories...")
        all_embeddings = embedding_service.embed_batch(all_descriptions)

        # Create category records with multiple embeddings
        embedding_idx = 0
        for i, category_data in enumerate(CATEGORIES):
            phrase_count = category_phrase_counts[i]
            category_embeddings = all_embeddings[embedding_idx:embedding_idx + phrase_count]
            embedding_idx += phrase_count

            category = Category(
                id=category_data["id"],
                title=category_data["title"],
                description=category_data["descriptions"],  # Now a list
                embedding=category_embeddings,  # Now a list of embeddings
                icon_name=category_data["icon_name"],
                color=category_data["color"],
                display_order=category_data["display_order"]
            )
            db.add(category)
            logger.info(f"✓ Added category: {category_data['title']} ({phrase_count} phrases)")

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
