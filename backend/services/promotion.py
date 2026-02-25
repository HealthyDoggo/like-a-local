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

        threshold = settings.similarity_threshold
        locations = db.query(Location).all()

        for location in locations:
            # Load all processed tips with their embeddings in one JOIN query.
            # This avoids re-embedding text that is already stored and eliminates
            # the N² per-tip embedding DB queries from the old find_similar_tips loop.
            rows = (
                db.query(Tip, Embedding)
                .join(Embedding, Embedding.tip_id == Tip.id)
                .filter(Tip.location_id == location.id, Tip.status == "processed")
                .all()
            )
            if not rows:
                continue

            tips = [tip for tip, _ in rows]
            embedding_cache: Dict[int, list] = {tip.id: emb.embedding for tip, emb in rows}

            # Group similar tips using cached embeddings (no model calls)
            processed_ids: set = set()
            tip_groups: Dict[str, List[Tip]] = {}

            for tip in tips:
                if tip.id in processed_ids:
                    continue

                tip_vec = embedding_cache[tip.id]
                canonical_text = tip.translated_text or tip.tip_text

                similar = [
                    other for other in tips
                    if other.id != tip.id
                    and other.id not in processed_ids
                    and self.embedding_service.similarity(tip_vec, embedding_cache[other.id]) >= threshold
                ]

                group_tips = [tip] + similar
                tip_groups[canonical_text] = group_tips
                for t in group_tips:
                    processed_ids.add(t.id)

            # Promote groups with enough mentions
            for canonical_text, group_tips in tip_groups.items():
                mention_count = len(group_tips)

                if mention_count >= settings.min_mentions:
                    category_counts: Dict[int, int] = {}
                    for t in group_tips:
                        if t.category_id:
                            category_counts[t.category_id] = category_counts.get(t.category_id, 0) + 1

                    most_common_category = (
                        max(category_counts.items(), key=lambda x: x[1])[0]
                        if category_counts else None
                    )

                    existing = db.query(TipPromotion).filter(
                        TipPromotion.tip_text == canonical_text,
                        TipPromotion.location_id == location.id
                    ).first()

                    if existing:
                        existing.mention_count = mention_count
                        existing.category_id = most_common_category
                        # Recalculate average similarity using cached embeddings
                        representative_vec = embedding_cache.get(group_tips[0].id)
                        if representative_vec:
                            scores = [
                                self.embedding_service.similarity(representative_vec, embedding_cache[t.id])
                                for t in group_tips if t.id in embedding_cache
                            ]
                            existing.similarity_score = sum(scores) / len(scores) if scores else 0.85
                    else:
                        representative_tip = group_tips[0] if group_tips else None
                        if not skip_translation and representative_tip:
                            new_representative_tips.append(representative_tip)

                        promotion = TipPromotion(
                            tip_text=canonical_text,
                            location_id=location.id,
                            source_tip_id=representative_tip.id if representative_tip else None,
                            mention_count=mention_count,
                            similarity_score=0.85,
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

