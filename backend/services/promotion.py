"""Tip promotion logic"""
import logging
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database.models import Tip, TipPromotion, Location, Embedding
from backend.services.embedding import get_embedding_service

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 0.85  # Threshold for considering tips similar
MIN_MENTIONS = 3  # Minimum mentions to promote a tip


class PromotionService:
    """Service for promoting tips based on frequency and similarity"""
    
    def __init__(self):
        self.embedding_service = get_embedding_service()
    
    def find_similar_tips(
        self,
        tip_text: str,
        location_id: int,
        db: Session,
        threshold: float = SIMILARITY_THRESHOLD
    ) -> List[Tip]:
        """Find tips similar to the given tip text at the same location"""
        # Get embedding for the tip text
        try:
            embedding = self.embedding_service.embed(tip_text)
        except Exception as e:
            logger.error(f"Failed to generate embedding for promotion: {e}")
            return []
        
        # Get all processed tips for this location
        tips = db.query(Tip).join(Embedding).filter(
            Tip.location_id == location_id,
            Tip.status == "processed"
        ).all()
        
        similar_tips = []
        for tip in tips:
            # Get embedding for this tip
            tip_embedding = db.query(Embedding).filter(
                Embedding.tip_id == tip.id
            ).first()
            
            if not tip_embedding:
                continue
            
            # Calculate similarity
            similarity = self.embedding_service.similarity(
                embedding,
                tip_embedding.embedding
            )
            
            if similarity >= threshold:
                similar_tips.append(tip)
        
        return similar_tips
    
    def promote_tips(self, db: Session) -> List[TipPromotion]:
        """Promote tips that are mentioned frequently by locals"""
        promoted = []
        
        # Get all locations
        locations = db.query(Location).all()
        
        for location in locations:
            # Get all processed tips for this location
            tips = db.query(Tip).filter(
                Tip.location_id == location.id,
                Tip.status == "processed"
            ).all()
            
            # Group similar tips
            processed_tips = set()
            tip_groups: Dict[str, List[Tip]] = {}
            
            for tip in tips:
                if tip.id in processed_tips:
                    continue
                
                # Find similar tips
                similar = self.find_similar_tips(
                    tip.translated_text or tip.tip_text,
                    location.id,
                    db
                )
                
                # Create a canonical representation (use the most common text)
                canonical_text = tip.translated_text or tip.tip_text
                
                # Add all similar tips to the group
                group_tips = [tip] + [t for t in similar if t.id not in processed_tips]
                tip_groups[canonical_text] = group_tips
                
                # Mark as processed
                for t in group_tips:
                    processed_tips.add(t.id)
            
            # Promote groups with enough mentions
            for canonical_text, group_tips in tip_groups.items():
                mention_count = len(group_tips)
                
                if mention_count >= MIN_MENTIONS:
                    # Check if already promoted
                    existing = db.query(TipPromotion).filter(
                        TipPromotion.tip_text == canonical_text,
                        TipPromotion.location_id == location.id
                    ).first()
                    
                    if existing:
                        # Update mention count
                        existing.mention_count = mention_count
                        # Calculate average similarity score
                        if group_tips:
                            try:
                                canonical_embedding = self.embedding_service.embed(canonical_text)
                                similarities = []
                                for t in group_tips:
                                    tip_embedding_obj = db.query(Embedding).filter(
                                        Embedding.tip_id == t.id
                                    ).first()
                                    if tip_embedding_obj:
                                        similarity = self.embedding_service.similarity(
                                            canonical_embedding,
                                            tip_embedding_obj.embedding
                                        )
                                        similarities.append(similarity)
                                if similarities:
                                    existing.similarity_score = sum(similarities) / len(similarities)
                            except Exception as e:
                                logger.error(f"Error calculating similarity: {e}")
                                existing.similarity_score = 0.85
                    else:
                        # Create new promotion
                        promotion = TipPromotion(
                            tip_text=canonical_text,
                            location_id=location.id,
                            mention_count=mention_count,
                            similarity_score=0.85  # Default similarity
                        )
                        db.add(promotion)
                        promoted.append(promotion)
        
        db.commit()
        return promoted


def get_promotion_service() -> PromotionService:
    """Get promotion service instance"""
    return PromotionService()

