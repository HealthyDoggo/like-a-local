"""Tip promotion logic"""
import logging
from typing import List, Dict
from sqlalchemy.orm import Session
from backend.database.models import Tip, TipPromotion, Location, Embedding, TipTranslation
from backend.services.embedding import get_embedding_service
from backend.services.processing_client import get_processing_client
from backend.config import settings

logger = logging.getLogger(__name__)



class PromotionService:
    """Service for promoting tips based on frequency and similarity"""

    def __init__(self):
        self.embedding_service = get_embedding_service()
        self.processing_client = get_processing_client()

    def _batch_translate_promoted_tips(
        self,
        representative_tips: List[Tip],
        db: Session,
    ) -> None:
        """
        Translate a batch of newly promoted tips to all supported languages.

        Uses a single translate_multi_batch() call so the PC runs one
        model.generate() per language instead of one per (tip × language).

        All tips are expected to have translated_text (English) from processing.
        English is used as the source language for all translations since it
        is already available and gives the best NLLB translation quality.
        """
        if not representative_tips:
            return

        # Skip tips that already have translations (safety guard for reruns)
        to_translate = [
            t for t in representative_tips
            if not db.query(TipTranslation).filter(TipTranslation.tip_id == t.id).first()
        ]
        if not to_translate:
            return

        other_languages = [lang for lang in settings.supported_languages if lang != "en"]
        english_texts = [t.translated_text or t.tip_text for t in to_translate]

        try:
            logger.info(
                f"Batch translating {len(to_translate)} promoted tips "
                f"into {len(other_languages)} languages"
            )
            # One HTTP request; PC runs one model.generate() per target language
            # with all texts batched together
            batch_translations = self.processing_client.translate_multi_batch(
                texts=english_texts,
                source_language="en",
                target_languages=other_languages,
            )

            for tip_idx, tip in enumerate(to_translate):
                # English
                db.add(TipTranslation(
                    tip_id=tip.id,
                    language_code="en",
                    translated_text=english_texts[tip_idx],
                ))
                # Original language text (if not English)
                original_lang = tip.original_language
                if original_lang and original_lang != "en":
                    db.add(TipTranslation(
                        tip_id=tip.id,
                        language_code=original_lang,
                        translated_text=tip.tip_text,
                    ))
                # All other target languages from the batch
                for lang_code, translated_list in batch_translations.items():
                    if lang_code == "en" or lang_code == original_lang:
                        continue
                    if tip_idx < len(translated_list) and translated_list[tip_idx]:
                        db.add(TipTranslation(
                            tip_id=tip.id,
                            language_code=lang_code,
                            translated_text=translated_list[tip_idx],
                        ))

            db.commit()
            logger.info(f"Successfully batch translated {len(to_translate)} promoted tips")

        except Exception as e:
            logger.error(f"Batch translation of promoted tips failed: {e}")
            db.rollback()
    
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
    
    def promote_tips(self, db: Session, skip_translation: bool = False) -> List[TipPromotion]:
        """
        Promote tips that are mentioned frequently by locals.

        Args:
            db: Database session
            skip_translation: If True, skip translating tips (useful for reclustering)

        Returns:
            List of promoted tips
        """
        promoted = []
        new_representative_tips: List[Tip] = []

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
                    # Determine most common category in the group
                    category_counts = {}
                    for t in group_tips:
                        if t.category_id:
                            category_counts[t.category_id] = category_counts.get(t.category_id, 0) + 1

                    most_common_category = None
                    if category_counts:
                        most_common_category = max(category_counts.items(), key=lambda x: x[1])[0]

                    # Check if already promoted
                    existing = db.query(TipPromotion).filter(
                        TipPromotion.tip_text == canonical_text,
                        TipPromotion.location_id == location.id
                    ).first()

                    if existing:
                        # Update mention count and category
                        existing.mention_count = mention_count
                        existing.category_id = most_common_category
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
                        representative_tip = group_tips[0] if group_tips else None
                        if not skip_translation and representative_tip:
                            new_representative_tips.append(representative_tip)

                        # Create new promotion
                        promotion = TipPromotion(
                            tip_text=canonical_text,
                            location_id=location.id,
                            source_tip_id=representative_tip.id if representative_tip else None,
                            mention_count=mention_count,
                            similarity_score=0.85,  # Default similarity
                            category_id=most_common_category
                        )
                        db.add(promotion)
                        promoted.append(promotion)

        db.commit()

        # Batch translate all new promotions in one shot — M generate() calls
        # (one per target language) instead of N×M calls (one per tip per language)
        if new_representative_tips:
            self._batch_translate_promoted_tips(new_representative_tips, db)

        return promoted


def get_promotion_service() -> PromotionService:
    """Get promotion service instance"""
    return PromotionService()

