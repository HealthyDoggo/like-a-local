"""
Script to display tip clusters in JSON format.

Shows all promoted tips grouped by location with cluster information including
mention counts, similarity scores, and all tips in each cluster.

Usage:
    # Show all clusters
    python scripts/show_clusters.py

    # Show clusters for specific location
    python scripts/show_clusters.py --location "Tokyo"

    # Show only clusters with minimum mention count
    python scripts/show_clusters.py --min-mentions 5

    # Include all tips in each cluster (requires embeddings)
    python scripts/show_clusters.py --show-all-tips

    # Pretty print JSON
    python scripts/show_clusters.py --pretty
"""
import sys
import os
import json
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from backend.database.connection import SessionLocal
from backend.database.models import TipPromotion, Location, Tip, Embedding
from backend.services.embedding import get_embedding_service
from backend.config import settings


def find_cluster_members(
    promotion: TipPromotion,
    db: Session,
    embedding_service
) -> list:
    """
    Find all tips that belong to a cluster (similar to the promoted tip).

    Args:
        promotion: The promoted tip
        db: Database session
        embedding_service: Embedding service for similarity calculations

    Returns:
        List of tip dictionaries with similarity scores
    """
    try:
        # Get embedding for promoted tip
        promoted_embedding = embedding_service.embed(promotion.tip_text)

        # Get all processed tips for this location
        tips = db.query(Tip).join(Embedding).filter(
            Tip.location_id == promotion.location_id,
            Tip.status == "processed"
        ).all()

        cluster_members = []
        for tip in tips:
            # Get embedding for this tip
            tip_embedding = db.query(Embedding).filter(
                Embedding.tip_id == tip.id
            ).first()

            if not tip_embedding:
                continue

            # Calculate similarity
            similarity = embedding_service.similarity(
                promoted_embedding,
                tip_embedding.embedding
            )

            # Include if similar enough
            if similarity >= settings.similarity_threshold:
                cluster_members.append({
                    "id": tip.id,
                    "tip_text": tip.tip_text,
                    "translated_text": tip.translated_text,
                    "original_language": tip.original_language,
                    "similarity_to_promoted": round(float(similarity), 4),
                    "submitted_at": tip.submitted_at.isoformat() if tip.submitted_at else None
                })

        # Sort by similarity (highest first)
        cluster_members.sort(key=lambda x: x["similarity_to_promoted"], reverse=True)
        return cluster_members

    except Exception as e:
        # If embedding service fails, return empty list
        return []


def get_clusters(
    db: Session,
    location_name: str = None,
    min_mentions: int = None,
    show_all_tips: bool = False
) -> dict:
    """
    Get all tip clusters from the database.

    Args:
        db: Database session
        location_name: Optional filter by location name
        min_mentions: Optional minimum mention count filter
        show_all_tips: If True, include all tips in each cluster

    Returns:
        Dictionary with cluster data
    """
    # Initialize embedding service if needed
    embedding_service = None
    if show_all_tips:
        try:
            embedding_service = get_embedding_service()
        except Exception as e:
            print(f"Warning: Could not initialize embedding service: {e}", file=sys.stderr)
            print("Continuing without showing cluster members...", file=sys.stderr)
            show_all_tips = False

    # Base query
    query = db.query(TipPromotion, Location).join(
        Location, TipPromotion.location_id == Location.id
    )

    # Apply filters
    if location_name:
        query = query.filter(Location.name.ilike(f"%{location_name}%"))

    if min_mentions is not None:
        query = query.filter(TipPromotion.mention_count >= min_mentions)

    # Order by location, then by mention count
    query = query.order_by(
        Location.country,
        Location.name,
        TipPromotion.mention_count.desc()
    )

    results = query.all()

    # Group by location
    clusters_by_location = {}
    for promotion, location in results:
        location_key = f"{location.name}, {location.country}"

        if location_key not in clusters_by_location:
            clusters_by_location[location_key] = {
                "location": {
                    "id": location.id,
                    "name": location.name,
                    "country": location.country,
                    "latitude": float(location.latitude) if location.latitude else None,
                    "longitude": float(location.longitude) if location.longitude else None
                },
                "clusters": []
            }

        cluster_data = {
            "promotion_id": promotion.id,
            "promoted_tip_text": promotion.tip_text,
            "mention_count": promotion.mention_count,
            "similarity_score": float(promotion.similarity_score) if promotion.similarity_score else None,
            "promoted_at": promotion.promoted_at.isoformat() if promotion.promoted_at else None
        }

        # Optionally include all tips in cluster
        if show_all_tips and embedding_service:
            cluster_members = find_cluster_members(promotion, db, embedding_service)
            cluster_data["cluster_members"] = cluster_members
            cluster_data["actual_member_count"] = len(cluster_members)

        clusters_by_location[location_key]["clusters"].append(cluster_data)

    # Convert to list and add statistics
    clusters = []
    total_promotions = 0
    total_mentions = 0

    for location_key, data in clusters_by_location.items():
        cluster_mentions = sum(tip["mention_count"] for tip in data["clusters"])
        total_promotions += len(data["clusters"])
        total_mentions += cluster_mentions

        clusters.append({
            **data,
            "total_promoted_tips": len(data["clusters"]),
            "total_mentions": cluster_mentions
        })

    return {
        "summary": {
            "total_locations": len(clusters),
            "total_promoted_tips": total_promotions,
            "total_mentions": total_mentions,
            "similarity_threshold": settings.similarity_threshold,
            "filters": {
                "location": location_name,
                "min_mentions": min_mentions,
                "show_all_tips": show_all_tips
            }
        },
        "clusters": clusters
    }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Display tip clusters in JSON format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show all clusters (promoted tips only)
  python scripts/show_clusters.py

  # Show all tips in each cluster
  python scripts/show_clusters.py --show-all-tips

  # Show clusters for Tokyo with all member tips
  python scripts/show_clusters.py --location Tokyo --show-all-tips

  # Show only high-mention clusters
  python scripts/show_clusters.py --min-mentions 5

  # Pretty print
  python scripts/show_clusters.py --pretty

  # Combine filters
  python scripts/show_clusters.py --location Paris --min-mentions 3 --show-all-tips --pretty
        """
    )
    parser.add_argument(
        "--location",
        type=str,
        help="Filter by location name (case-insensitive partial match)"
    )
    parser.add_argument(
        "--min-mentions",
        type=int,
        help="Minimum mention count to include"
    )
    parser.add_argument(
        "--show-all-tips",
        action="store_true",
        help="Include all tips in each cluster (recalculates similarity)"
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty print JSON output"
    )

    args = parser.parse_args()

    db = SessionLocal()
    try:
        clusters = get_clusters(
            db,
            location_name=args.location,
            min_mentions=args.min_mentions,
            show_all_tips=args.show_all_tips
        )

        # Output as JSON
        if args.pretty:
            print(json.dumps(clusters, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(clusters, ensure_ascii=False))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
