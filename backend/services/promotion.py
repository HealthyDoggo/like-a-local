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
    
    def promote_tips(
        self,
        db: Session,
        new_tips: List[Tip] = None,
        skip_translation: bool = False,
    ) -> List[TipPromotion]:
        """
        Promote tips that are mentioned frequently by locals.

        Args:
            db: Database session
            new_tips: Tips processed in the current nightly run. When provided,
                      only these tips are compared against existing promotions
                      (incremental mode — O(Q×P) instead of O(N²)). Pass None
                      to force a full recluster of all tips at all locations,
                      e.g. after a similarity threshold change.
            skip_translation: If True, skip translating newly promoted tips.

        Returns:
            List of newly created TipPromotion records.
        """
        if new_tips is not None:
            return self._promote_incremental(db, new_tips, skip_translation)
        return self._promote_full_recluster(db, skip_translation)

    # ------------------------------------------------------------------
    # Incremental mode — called from the nightly job
    # ------------------------------------------------------------------

    def _promote_incremental(
        self,
        db: Session,
        new_tips: List[Tip],
        skip_translation: bool,
    ) -> List[TipPromotion]:
        """
        Compare each newly processed tip against existing promotions.

        For each new tip:
        - If similar to an existing promotion → increment its mention_count.
        - Otherwise → group unmatched new tips with each other; create a
          promotion if the group meets min_mentions.

        Complexity: O(Q×P) per location, where Q = new tips and P = existing
        promotions — far cheaper than the O(N²) full recluster.
        """
        from collections import defaultdict

        promoted = []
        new_representative_tips: List[Tip] = []
        threshold = settings.similarity_threshold

        # Group new tips by location; skip tips with no location
        by_location: Dict[int, List[Tip]] = defaultdict(list)
        for tip in new_tips:
            if tip.location_id:
                by_location[tip.location_id].append(tip)
        if not by_location:
            return promoted

        # Fetch embeddings for all new tips in one query
        new_tip_ids = [t.id for t in new_tips if t.location_id]
        new_emb_rows = db.query(Embedding).filter(Embedding.tip_id.in_(new_tip_ids)).all()
        new_tip_vecs: Dict[int, list] = {e.tip_id: e.embedding for e in new_emb_rows}

        for location_id, location_new_tips in by_location.items():
            # Load existing promotions with their source embeddings in one JOIN
            promo_rows = (
                db.query(TipPromotion, Embedding)
                .outerjoin(Embedding, Embedding.tip_id == TipPromotion.source_tip_id)
                .filter(TipPromotion.location_id == location_id)
                .all()
            )
            existing_promotions = [p for p, _ in promo_rows]
            promo_vecs: Dict[int, list] = {p.id: e.embedding for p, e in promo_rows if e}

            unmatched: List[Tip] = []

            for tip in location_new_tips:
                tip_vec = new_tip_vecs.get(tip.id)
                if not tip_vec:
                    continue

                # Find the most similar existing promotion
                best_promo, best_sim = None, -1.0
                for promo in existing_promotions:
                    promo_vec = promo_vecs.get(promo.id)
                    if not promo_vec:
                        continue
                    sim = self.embedding_service.similarity(tip_vec, promo_vec)
                    if sim >= threshold and sim > best_sim:
                        best_sim, best_promo = sim, promo

                if best_promo:
                    best_promo.mention_count += 1
                    if tip.category_id and not best_promo.category_id:
                        best_promo.category_id = tip.category_id
                else:
                    unmatched.append(tip)

            # Group unmatched new tips with each other to catch brand-new clusters
            unmatched_seen: set = set()
            for tip in unmatched:
                if tip.id in unmatched_seen:
                    continue
                tip_vec = new_tip_vecs.get(tip.id)
                if not tip_vec:
                    continue

                similar = [
                    other for other in unmatched
                    if other.id != tip.id
                    and other.id not in unmatched_seen
                    and new_tip_vecs.get(other.id)
                    and self.embedding_service.similarity(tip_vec, new_tip_vecs[other.id]) >= threshold
                ]
                group = [tip] + similar
                for t in group:
                    unmatched_seen.add(t.id)

                if len(group) >= settings.min_mentions:
                    representative = group[0]
                    if not skip_translation:
                        new_representative_tips.append(representative)
                    category_counts: Dict[int, int] = {}
                    for t in group:
                        if t.category_id:
                            category_counts[t.category_id] = category_counts.get(t.category_id, 0) + 1
                    promotion = TipPromotion(
                        tip_text=representative.translated_text or representative.tip_text,
                        location_id=location_id,
                        source_tip_id=representative.id,
                        mention_count=len(group),
                        similarity_score=0.85,
                        category_id=max(category_counts, key=category_counts.get) if category_counts else None,
                    )
                    db.add(promotion)
                    promoted.append(promotion)

        db.commit()
        if new_representative_tips:
            self._batch_translate_promoted_tips(new_representative_tips, db)
        return promoted

    # ------------------------------------------------------------------
    # Full recluster — called from /api/jobs/promote
    # ------------------------------------------------------------------

    def _promote_full_recluster(
        self,
        db: Session,
        skip_translation: bool,
    ) -> List[TipPromotion]:
        """
        Re-cluster all processed tips at every location from scratch.

        Use this after changing the similarity threshold or to repair state.
        Complexity: O(N²) per location.
        """
        promoted = []
        new_representative_tips: List[Tip] = []
        threshold = settings.similarity_threshold

        for location in db.query(Location).all():
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

            for canonical_text, group_tips in tip_groups.items():
                mention_count = len(group_tips)
                if mention_count < settings.min_mentions:
                    continue

                category_counts: Dict[int, int] = {}
                for t in group_tips:
                    if t.category_id:
                        category_counts[t.category_id] = category_counts.get(t.category_id, 0) + 1
                most_common_category = max(category_counts, key=category_counts.get) if category_counts else None

                existing = db.query(TipPromotion).filter(
                    TipPromotion.tip_text == canonical_text,
                    TipPromotion.location_id == location.id
                ).first()

                if existing:
                    existing.mention_count = mention_count
                    existing.category_id = most_common_category
                    rep_vec = embedding_cache.get(group_tips[0].id)
                    if rep_vec:
                        scores = [
                            self.embedding_service.similarity(rep_vec, embedding_cache[t.id])
                            for t in group_tips if t.id in embedding_cache
                        ]
                        existing.similarity_score = sum(scores) / len(scores) if scores else 0.85
                else:
                    representative_tip = group_tips[0]
                    if not skip_translation:
                        new_representative_tips.append(representative_tip)
                    promotion = TipPromotion(
                        tip_text=canonical_text,
                        location_id=location.id,
                        source_tip_id=representative_tip.id,
                        mention_count=mention_count,
                        similarity_score=0.85,
                        category_id=most_common_category,
                    )
                    db.add(promotion)
                    promoted.append(promotion)

        db.commit()
        if new_representative_tips:
            self._batch_translate_promoted_tips(new_representative_tips, db)
        return promoted


def get_promotion_service() -> PromotionService:
    """Get promotion service instance"""
    return PromotionService()

