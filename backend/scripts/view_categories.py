"""View tips or promotions grouped by category"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import SessionLocal
from backend.database.models import Tip, TipPromotion, Category
from sqlalchemy import func


def view_tips_by_category():
    """Show tips grouped by category"""
    db = SessionLocal()
    try:
        print("\n=== TIPS BY CATEGORY ===\n")

        # Get categories with tip counts
        categories = db.query(Category).order_by(Category.display_order).all()

        total_tips = 0
        for category in categories:
            count = db.query(Tip).filter(Tip.category_id == category.id).count()
            total_tips += count
            print(f"{category.title} ({category.id}): {count} tips")

            # Show sample tips
            samples = db.query(Tip).filter(
                Tip.category_id == category.id
            ).limit(3).all()

            for tip in samples:
                confidence = f" [{tip.category_confidence:.3f}]" if tip.category_confidence else ""
                print(f"  - {tip.text[:80]}...{confidence}")
            if samples:
                print()

        # Show unclassified tips
        unclassified = db.query(Tip).filter(Tip.category_id.is_(None)).count()
        print(f"Unclassified: {unclassified} tips")

        # Show some unclassified samples
        samples = db.query(Tip).filter(Tip.category_id.is_(None)).limit(5).all()
        for tip in samples:
            processed = " [processed]" if tip.category_assigned_at else " [not processed]"
            print(f"  - {tip.text[:80]}...{processed}")

        print(f"\nTotal: {total_tips + unclassified} tips")

    finally:
        db.close()


def view_promotions_by_category():
    """Show promotions grouped by category"""
    db = SessionLocal()
    try:
        print("\n=== PROMOTIONS BY CATEGORY ===\n")

        # Get categories with promotion counts
        categories = db.query(Category).order_by(Category.display_order).all()

        total_promotions = 0
        for category in categories:
            count = db.query(TipPromotion).filter(
                TipPromotion.category_id == category.id
            ).count()
            total_promotions += count
            print(f"{category.title} ({category.id}): {count} promotions")

            # Show sample promotions
            samples = db.query(TipPromotion).filter(
                TipPromotion.category_id == category.id
            ).limit(3).all()

            for promo in samples:
                print(f"  - {promo.tip_text[:80]}... (mentions: {promo.mention_count})")
            if samples:
                print()

        # Show unclassified promotions
        unclassified = db.query(TipPromotion).filter(
            TipPromotion.category_id.is_(None)
        ).count()
        print(f"Unclassified: {unclassified} promotions")

        # Show some unclassified samples
        samples = db.query(TipPromotion).filter(
            TipPromotion.category_id.is_(None)
        ).limit(5).all()
        for promo in samples:
            print(f"  - {promo.tip_text[:80]}... (mentions: {promo.mention_count})")

        print(f"\nTotal: {total_promotions + unclassified} promotions")

    finally:
        db.close()


def view_summary():
    """Show summary of both tips and promotions"""
    db = SessionLocal()
    try:
        print("\n=== CATEGORY SUMMARY ===\n")

        categories = db.query(Category).order_by(Category.display_order).all()

        print(f"{'Category':<30} {'Tips':<10} {'Promotions':<10}")
        print("-" * 50)

        total_tips = 0
        total_promotions = 0

        for category in categories:
            tip_count = db.query(Tip).filter(Tip.category_id == category.id).count()
            promo_count = db.query(TipPromotion).filter(
                TipPromotion.category_id == category.id
            ).count()
            total_tips += tip_count
            total_promotions += promo_count
            print(f"{category.title:<30} {tip_count:<10} {promo_count:<10}")

        # Unclassified
        unclassified_tips = db.query(Tip).filter(Tip.category_id.is_(None)).count()
        unclassified_promos = db.query(TipPromotion).filter(
            TipPromotion.category_id.is_(None)
        ).count()

        print(f"{'Unclassified':<30} {unclassified_tips:<10} {unclassified_promos:<10}")
        print("-" * 50)
        print(f"{'TOTAL':<30} {total_tips + unclassified_tips:<10} {total_promotions + unclassified_promos:<10}")

    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] in ["-h", "--help"]:
            print("Usage: python view_categories.py [tips|promotions|summary]")
            print("\nOptions:")
            print("  tips         View tips grouped by category")
            print("  promotions   View promotions grouped by category")
            print("  summary      View summary counts for both (default)")
            print("  -h, --help   Show this help message")
            sys.exit(0)
        elif sys.argv[1] == "tips":
            view_tips_by_category()
        elif sys.argv[1] == "promotions":
            view_promotions_by_category()
        elif sys.argv[1] == "summary":
            view_summary()
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use -h or --help for usage information")
            sys.exit(1)
    else:
        view_summary()
