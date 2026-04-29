"""Analyze classification quality and show similarity details"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import SessionLocal
from backend.database.models import Tip, Embedding, Category
from backend.services.category_classifier import get_category_classifier
from backend.services.llm_classifier import get_llm_classifier
from backend.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _get_classifier(db, method=None):
    """Return (classifier, use_llm) based on method or config."""
    use_llm = (method or settings.classification_method) == "llm"
    if use_llm:
        classifier = get_llm_classifier()
    else:
        classifier = get_category_classifier()
    classifier.load_categories(db)
    return classifier, use_llm


def analyze_classifications(limit=50, min_confidence=None, max_confidence=None, method=None):
    """Analyze classified tips and show similarity details"""
    db = SessionLocal()

    try:
        classifier, use_llm = _get_classifier(db, method)

        print(f"Classification method: {'llm' if use_llm else 'embedding'}")

        query = db.query(Tip).filter(
            Tip.status == "processed",
            Tip.category_id.isnot(None)
        )
        if not use_llm:
            query = query.join(Embedding)

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
            if use_llm:
                text = tip.translated_text or tip.tip_text
                category_id, confidence = classifier.classify_tip(text)
                category = next((c for c in classifier.categories if c.id == category_id), None)

                print(f"Tip ID: {tip.id}")
                print(f"Text: {tip.tip_text[:100]}{'...' if len(tip.tip_text) > 100 else ''}")
                print(f"Stored category: {tip.category_id} (confidence: {tip.category_confidence:.3f})")
                print(f"Re-classified: {category_id} (confidence: {confidence:.3f})")
                if category:
                    print(f"Category title: {category.title}")
                if tip.category_id != category_id:
                    print(f"  ⚠ MISMATCH: stored={tip.category_id}, reclassified={category_id}")
                print("-" * 80)
            else:
                embedding_obj = db.query(Embedding).filter(Embedding.tip_id == tip.id).first()
                if not embedding_obj:
                    continue

                category_id, confidence, phrase_idx, phrase_sims = classifier.classify_tip(
                    embedding_obj.embedding,
                    return_details=True
                )

                category = next((c for c in classifier.categories if c.id == category_id), None)
                if not category:
                    continue

                matching_phrase = category.description[phrase_idx]

                print(f"Tip ID: {tip.id}")
                print(f"Text: {tip.tip_text[:100]}{'...' if len(tip.tip_text) > 100 else ''}")
                print(f"Category: {category.title} ({category_id})")
                print(f"Confidence: {confidence:.3f}")
                print(f"Best matching phrase: '{matching_phrase}'")
                print(f"Phrase similarities:")
                for i, (desc, sim) in enumerate(zip(category.description, phrase_sims)):
                    marker = " <-- BEST" if i == phrase_idx else ""
                    print(f"  [{sim:.3f}] {desc}{marker}")

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


def analyze_unclassified(limit=20, method=None):
    """Analyze tips that weren't classified (low confidence)"""
    db = SessionLocal()

    try:
        classifier, use_llm = _get_classifier(db, method)

        query = db.query(Tip).filter(
            Tip.status == "processed",
            Tip.category_assigned_at.isnot(None),
            Tip.category_id.is_(None)
        )
        if not use_llm:
            query = query.join(Embedding)
        tips = query.limit(limit).all()

        if not tips:
            print("No unclassified tips found.")
            return

        print(f"\n=== UNCLASSIFIED TIPS ANALYSIS ({len(tips)} tips) ===\n")

        for tip in tips:
            if use_llm:
                text = tip.translated_text or tip.tip_text
                category_id, confidence = classifier.classify_tip(text)
                category = next((c for c in classifier.categories if c.id == category_id), None)

                print(f"Tip ID: {tip.id}")
                print(f"Text: {tip.tip_text[:100]}{'...' if len(tip.tip_text) > 100 else ''}")
                if category:
                    print(f"LLM would assign: {category.title} ({category_id})")
                else:
                    print(f"LLM returned: none")
                print(f"Confidence: {confidence:.3f} (below threshold)")
                print("-" * 80)
            else:
                embedding_obj = db.query(Embedding).filter(Embedding.tip_id == tip.id).first()
                if not embedding_obj:
                    continue

                category_id, confidence, phrase_idx, phrase_sims = classifier.classify_tip(
                    embedding_obj.embedding,
                    return_details=True
                )

                category = next((c for c in classifier.categories if c.id == category_id), None)
                if not category:
                    continue

                matching_phrase = category.description[phrase_idx]

                print(f"Tip ID: {tip.id}")
                print(f"Text: {tip.tip_text[:100]}{'...' if len(tip.tip_text) > 100 else ''}")
                print(f"Best match: {category.title} ({category_id})")
                print(f"Confidence: {confidence:.3f} (below threshold)")
                print(f"Would match phrase: '{matching_phrase}'")
                print("-" * 80)

        print(f"\nAnalyzed {len(tips)} unclassified tips")

    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze classification quality",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  classified [limit]              Analyze classified tips (default: 50)
  unclassified [limit]            Analyze unclassified tips (default: 20)
  low-confidence [limit]          Show tips with confidence < 0.75
  high-confidence [limit]         Show tips with confidence > 0.90

Examples:
  python -m backend.scripts.analyze_classification classified 100
  python -m backend.scripts.analyze_classification low-confidence 30 --method llm
  python -m backend.scripts.analyze_classification unclassified
        """
    )
    parser.add_argument("command", choices=["classified", "unclassified", "low-confidence", "high-confidence"])
    parser.add_argument("limit", nargs="?", type=int, default=None)
    parser.add_argument(
        "--method",
        choices=["embedding", "llm"],
        default=None,
        help=f"Classification method (default: from CLASSIFICATION_METHOD env, currently '{settings.classification_method}')"
    )

    args = parser.parse_args()

    if args.command == "classified":
        analyze_classifications(limit=args.limit or 50, method=args.method)
    elif args.command == "unclassified":
        analyze_unclassified(limit=args.limit or 20, method=args.method)
    elif args.command == "low-confidence":
        analyze_classifications(limit=args.limit or 50, max_confidence=0.75, method=args.method)
    elif args.command == "high-confidence":
        analyze_classifications(limit=args.limit or 50, min_confidence=0.90, method=args.method)
