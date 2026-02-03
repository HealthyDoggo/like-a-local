"""Analyze classification quality and show similarity details"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import SessionLocal
from backend.database.models import Tip, Embedding, Category
from backend.services.category_classifier import get_category_classifier
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def analyze_classifications(limit=50, min_confidence=None, max_confidence=None):
    """Analyze classified tips and show similarity details"""
    db = SessionLocal()

    try:
        # Initialize classifier
        classifier = get_category_classifier()
        classifier.load_categories(db)

        # Build query
        query = db.query(Tip).join(Embedding).filter(
            Tip.status == "processed",
            Tip.category_id.isnot(None)
        )

        if min_confidence is not None:
            query = query.filter(Tip.category_confidence >= min_confidence)

        if max_confidence is not None:
            query = query.filter(Tip.category_confidence <= max_confidence)

        tips = query.order_by(Tip.category_confidence.desc()).limit(limit).all()

        if not tips:
            print("No classified tips found.")
            return

        print(f"\n=== CLASSIFICATION ANALYSIS ({len(tips)} tips) ===\n")

        for tip in tips:
            embedding_obj = db.query(Embedding).filter(Embedding.tip_id == tip.id).first()

            if not embedding_obj:
                continue

            # Reclassify to get detailed info
            category_id, confidence, phrase_idx, phrase_sims = classifier.classify_tip(
                embedding_obj.embedding,
                return_details=True
            )

            # Get category info
            category = next((c for c in classifier.categories if c.id == category_id), None)

            if not category:
                continue

            matching_phrase = category.description[phrase_idx]

            print(f"Tip ID: {tip.id}")
            print(f"Text: {tip.text[:100]}{'...' if len(tip.text) > 100 else ''}")
            print(f"Category: {category.title} ({category_id})")
            print(f"Confidence: {confidence:.3f}")
            print(f"Best matching phrase: '{matching_phrase}'")
            print(f"Phrase similarities:")
            for i, (desc, sim) in enumerate(zip(category.description, phrase_sims)):
                marker = " <-- BEST" if i == phrase_idx else ""
                print(f"  [{sim:.3f}] {desc}{marker}")

            # Show runner-up categories
            print(f"Other category scores:")
            other_scores = []
            for other_cat in classifier.categories:
                if other_cat.id == category_id:
                    continue

                max_sim = 0.0
                for emb in other_cat.embedding:
                    sim = classifier.embedding_service.similarity(
                        embedding_obj.embedding,
                        emb
                    )
                    max_sim = max(max_sim, sim)

                other_scores.append((other_cat.title, max_sim))

            other_scores.sort(key=lambda x: x[1], reverse=True)
            for cat_title, score in other_scores[:3]:
                print(f"  [{score:.3f}] {cat_title}")

            print("-" * 80)

        print(f"\nAnalyzed {len(tips)} tips")

    finally:
        db.close()


def analyze_unclassified(limit=20):
    """Analyze tips that weren't classified (low confidence)"""
    db = SessionLocal()

    try:
        # Initialize classifier
        classifier = get_category_classifier()
        classifier.load_categories(db)

        # Get unclassified tips that were processed
        tips = db.query(Tip).join(Embedding).filter(
            Tip.status == "processed",
            Tip.category_assigned_at.isnot(None),
            Tip.category_id.is_(None)
        ).limit(limit).all()

        if not tips:
            print("No unclassified tips found.")
            return

        print(f"\n=== UNCLASSIFIED TIPS ANALYSIS ({len(tips)} tips) ===\n")

        for tip in tips:
            embedding_obj = db.query(Embedding).filter(Embedding.tip_id == tip.id).first()

            if not embedding_obj:
                continue

            # Classify to see what it would have been
            category_id, confidence, phrase_idx, phrase_sims = classifier.classify_tip(
                embedding_obj.embedding,
                return_details=True
            )

            category = next((c for c in classifier.categories if c.id == category_id), None)

            if not category:
                continue

            matching_phrase = category.description[phrase_idx]

            print(f"Tip ID: {tip.id}")
            print(f"Text: {tip.text[:100]}{'...' if len(tip.text) > 100 else ''}")
            print(f"Best match: {category.title} ({category_id})")
            print(f"Confidence: {confidence:.3f} (below threshold)")
            print(f"Would match phrase: '{matching_phrase}'")
            print("-" * 80)

        print(f"\nAnalyzed {len(tips)} unclassified tips")

    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_classification.py <command> [options]")
        print("\nCommands:")
        print("  classified [limit]              Analyze classified tips (default: 50)")
        print("  unclassified [limit]            Analyze unclassified tips (default: 20)")
        print("  low-confidence [limit]          Show tips with confidence < 0.75")
        print("  high-confidence [limit]         Show tips with confidence > 0.90")
        print("\nExamples:")
        print("  python analyze_classification.py classified 100")
        print("  python analyze_classification.py low-confidence 30")
        print("  python analyze_classification.py unclassified")
        sys.exit(1)

    command = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else None

    if command == "classified":
        analyze_classifications(limit=limit or 50)

    elif command == "unclassified":
        analyze_unclassified(limit=limit or 20)

    elif command == "low-confidence":
        analyze_classifications(limit=limit or 50, max_confidence=0.75)

    elif command == "high-confidence":
        analyze_classifications(limit=limit or 50, min_confidence=0.90)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
