"""
Script to re-cluster all tips in the database.

This script clears all existing tip promotions and re-runs the clustering
logic with the current configuration settings. You can optionally override
the similarity threshold and minimum mentions.

Usage:
    # Re-cluster with config settings (default: threshold=0.85, min_mentions=3)
    python -m backend.scripts.recluster_tips

    # Re-cluster with custom similarity threshold
    python -m backend.scripts.recluster_tips --threshold 0.90

    # Re-cluster with custom minimum mentions
    python -m backend.scripts.recluster_tips --min-mentions 2

    # Re-cluster with both custom settings
    python -m backend.scripts.recluster_tips --threshold 0.90 --min-mentions 2

    # Dry run (show what would be done without making changes)
    python -m backend.scripts.recluster_tips --dry-run
"""
import sys
import os
import logging
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from backend.database.connection import SessionLocal
from backend.database.models import TipPromotion, Tip, Location
from backend.services.promotion import get_promotion_service
from backend.config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def show_current_stats(db: Session):
    """Show current database statistics"""
    total_tips = db.query(Tip).count()
    processed_tips = db.query(Tip).filter(Tip.status == "processed").count()
    pending_tips = db.query(Tip).filter(Tip.status == "pending").count()
    total_promotions = db.query(TipPromotion).count()
    total_locations = db.query(Location).count()

    print("\n📊 Current Database Statistics:")
    print(f"   Total tips: {total_tips}")
    print(f"   Processed tips: {processed_tips}")
    print(f"   Pending tips: {pending_tips}")
    print(f"   Current promotions: {total_promotions}")
    print(f"   Locations: {total_locations}")

    # Show promotions by location
    if total_promotions > 0:
        print(f"\n📍 Current Promotions by Location:")
        locations = db.query(Location).all()
        for location in locations:
            count = db.query(TipPromotion).filter(
                TipPromotion.location_id == location.id
            ).count()
            if count > 0:
                print(f"   • {location.name}, {location.country}: {count} promoted tips")


def recluster_tips(
    db: Session,
    threshold: float = None,
    min_mentions: int = None,
    dry_run: bool = False
) -> dict:
    """
    Re-cluster all tips in the database.

    Args:
        db: Database session
        threshold: Optional custom similarity threshold (uses config if None)
        min_mentions: Optional custom minimum mentions (uses config if None)
        dry_run: If True, show what would be done without making changes

    Returns:
        Dictionary with statistics
    """
    # Use config values if not provided
    actual_threshold = threshold if threshold is not None else settings.similarity_threshold
    actual_min_mentions = min_mentions if min_mentions is not None else settings.min_mentions

    print("\n⚙️  Re-clustering Configuration:")
    print(f"   Similarity threshold: {actual_threshold}")
    print(f"   Minimum mentions: {actual_min_mentions}")

    if dry_run:
        print("\n🔍 DRY RUN MODE - No changes will be made")

    # Show current stats
    show_current_stats(db)

    if dry_run:
        print("\n✅ Dry run complete - no changes were made")
        return {"dry_run": True}

    # Clear existing promotions
    existing_count = db.query(TipPromotion).count()
    print(f"\n🧹 Clearing {existing_count} existing promotions...")
    db.query(TipPromotion).delete()
    db.commit()
    print("   ✓ Cleared all promotions")

    # Temporarily override config if custom values provided
    original_threshold = settings.similarity_threshold
    original_min_mentions = settings.min_mentions

    if threshold is not None:
        settings.similarity_threshold = threshold
    if min_mentions is not None:
        settings.min_mentions = min_mentions

    try:
        # Run promotion logic
        print(f"\n🔄 Running clustering with threshold={settings.similarity_threshold}, min_mentions={settings.min_mentions}...")
        promotion_service = get_promotion_service()
        promoted = promotion_service.promote_tips(db)

        print(f"\n✅ Clustering complete!")
        print(f"   New promotions created: {len(promoted)}")

        # Show new stats
        print("\n📊 New Promotion Statistics:")
        locations = db.query(Location).all()
        total_promoted = 0
        for location in locations:
            count = db.query(TipPromotion).filter(
                TipPromotion.location_id == location.id
            ).count()
            if count > 0:
                total_promoted += count
                print(f"   • {location.name}, {location.country}: {count} promoted tips")

        # Show some sample promotions
        sample_promotions = db.query(TipPromotion).order_by(
            TipPromotion.mention_count.desc()
        ).limit(5).all()

        if sample_promotions:
            print(f"\n🏆 Top 5 Promoted Tips (by mention count):")
            for promo in sample_promotions:
                location = db.query(Location).filter(Location.id == promo.location_id).first()
                tip_preview = promo.tip_text[:60] + "..." if len(promo.tip_text) > 60 else promo.tip_text
                print(f"   • [{promo.mention_count} mentions] {location.name}: {tip_preview}")

        return {
            "cleared": existing_count,
            "created": len(promoted),
            "total_promoted": total_promoted,
            "threshold": settings.similarity_threshold,
            "min_mentions": settings.min_mentions
        }

    finally:
        # Restore original config
        settings.similarity_threshold = original_threshold
        settings.min_mentions = original_min_mentions


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Re-cluster all tips in the database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Re-cluster with config settings
  python -m backend.scripts.recluster_tips

  # Use a stricter threshold (higher = more similar required)
  python -m backend.scripts.recluster_tips --threshold 0.90

  # Use a looser threshold (lower = more tips grouped together)
  python -m backend.scripts.recluster_tips --threshold 0.75

  # Require fewer mentions to promote
  python -m backend.scripts.recluster_tips --min-mentions 2

  # Dry run to preview changes
  python -m backend.scripts.recluster_tips --dry-run --threshold 0.90
        """
    )
    parser.add_argument(
        "--threshold",
        type=float,
        help=f"Cosine similarity threshold for clustering (default: {settings.similarity_threshold})"
    )
    parser.add_argument(
        "--min-mentions",
        type=int,
        help=f"Minimum mentions required to promote a tip (default: {settings.min_mentions})"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )

    args = parser.parse_args()

    # Validate threshold
    if args.threshold is not None and (args.threshold < 0 or args.threshold > 1):
        print("❌ Error: Threshold must be between 0 and 1")
        sys.exit(1)

    # Validate min_mentions
    if args.min_mentions is not None and args.min_mentions < 1:
        print("❌ Error: Minimum mentions must be at least 1")
        sys.exit(1)

    print("🔧 TravelBuddy Tip Re-clustering Tool")
    print("=" * 50)

    db = SessionLocal()
    try:
        stats = recluster_tips(
            db,
            threshold=args.threshold,
            min_mentions=args.min_mentions,
            dry_run=args.dry_run
        )

        if not args.dry_run:
            print(f"\n💡 Tip: To make these settings permanent, update your .env file:")
            if args.threshold is not None:
                print(f"   SIMILARITY_THRESHOLD={args.threshold}")
            if args.min_mentions is not None:
                print(f"   MIN_MENTIONS={args.min_mentions}")

    except Exception as e:
        logger.error(f"Re-clustering failed: {e}", exc_info=True)
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
