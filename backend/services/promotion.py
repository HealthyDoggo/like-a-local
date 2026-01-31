"""Tip promotion logic"""
import logging
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database.models import Tip, TipPromotion, Location, Embedding, TipTranslation
from backend.services.embedding import get_embedding_service
from backend.services.processing_client import get_processing_client
from backend.config import settings

logger = logging.getLogger(__name__)

# Top 10 supported languages
TOP_10_LANGUAGES = ["en", "es", "fr", "de", "pt", "it", "zh", "ja", "ar", "hi"]


class PromotionService:
    """Service for promoting tips based on frequency and similarity"""

    def __init__(self):
        self.embedding_service = get_embedding_service()
        self.processing_client = get_processing_client()

    def translate_tip_to_all_languages(self, tip: Tip, db: Session) -> bool:
        """
        Translate a tip to all supported languages.

        Only translates if:
        1. Tip has not been translated yet (no entries in TipTranslation)
        2. PC processing service is available

        Args:
            tip: The tip to translate
            db: Database session

        Returns:
            True if translation succeeded, False otherwise
        """
        # Check if translations already exist
        existing = db.query(TipTranslation).filter(
            TipTranslation.tip_id == tip.id
        ).first()

        if existing:
            logger.info(f"Tip {tip.id} already has translations, skipping")
            return True

        # Determine source language and text
        source_language = tip.original_language or "en"
        source_text = tip.tip_text

        # Determine which languages to translate to (exclude source language)
        target_languages = [lang for lang in TOP_10_LANGUAGES if lang != source_language]

        try:
            # Call PC service for multi-language translation
            logger.info(f"Translating tip {tip.id} from {source_language} to {len(target_languages)} languages")
            translations = self.processing_client.translate_multi(
                text=source_text,
                source_language=source_language,
                target_languages=target_languages
            )

            # Store original language translation
            db.add(TipTranslation(
                tip_id=tip.id,
                language_code=source_language,
                translated_text=source_text
            ))

            # Store English translation if we have it and it's different from source
            if source_language != "en" and tip.translated_text:
                db.add(TipTranslation(
                    tip_id=tip.id,
                    language_code="en",
                    translated_text=tip.translated_text
                ))

            # Store all other translations
            for lang_code, translated_text in translations.items():
                # Skip if we already added it (original or English)
                if lang_code == source_language or (lang_code == "en" and tip.translated_text):
                    continue

                db.add(TipTranslation(
                    tip_id=tip.id,
                    language_code=lang_code,
                    translated_text=translated_text
                ))

            db.commit()
            logger.info(f"Successfully translated tip {tip.id} to {len(translations)} languages")
            return True

        except Exception as e:
            logger.error(f"Failed to translate tip {tip.id}: {e}")
            db.rollback()
            return False
    
    def find_similar_tips(
        self,
        tip_text: str,
        location_id: int,
        db: Session,
        threshold: float = None
    ) -> List[Tip]:
        """Find tips similar to the given tip text at the same location"""
        # Use config threshold if not provided
        if threshold is None:
            threshold = settings.similarity_threshold

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

                if mention_count >= settings.min_mentions:
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
                        # Translate representative tip to all languages before promoting
                        # Use the first tip in the group as the representative
                        if group_tips:
                            representative_tip = group_tips[0]
                            self.translate_tip_to_all_languages(representative_tip, db)

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

