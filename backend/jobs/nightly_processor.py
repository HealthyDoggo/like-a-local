"""Nightly processing job for tips"""
import logging
import sys
from datetime import datetime
from sqlalchemy.orm import Session
from backend.database.connection import SessionLocal
from backend.database.models import Tip, Embedding
from backend.services.translation import get_translation_service
from backend.services.embedding import get_embedding_service
from backend.services.promotion import get_promotion_service
from backend.utils.wol import get_wol
from backend.config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def process_pending_tips(db: Session, wake_pc: bool = True) -> dict:
    """Process all pending tips"""
    stats = {
        "processed": 0,
        "translated": 0,
        "embedded": 0,
        "errors": 0
    }
    
    # Get pending tips
    pending_tips = db.query(Tip).filter(Tip.status == "pending").all()
    
    if not pending_tips:
        logger.info("No pending tips to process")
        return stats
    
    logger.info(f"Processing {len(pending_tips)} pending tips")
    
    # Wake PC if needed
    if wake_pc:
        wol = get_wol()
        if not wol.wake():
            logger.error("Failed to wake PC, but continuing with processing")
    
    # Initialize services
    translation_service = get_translation_service()
    embedding_service = get_embedding_service()
    
    # Process each tip
    for tip in pending_tips:
        try:
            # Detect and translate if needed
            if not tip.translated_text:
                detected_lang = translation_service.detect_language(tip.tip_text)
                tip.original_language = detected_lang
                
                # Translate if not English
                if detected_lang != "en":
                    tip.translated_text = translation_service.translate(
                        tip.tip_text,
                        source_language=detected_lang
                    )
                    stats["translated"] += 1
                else:
                    tip.translated_text = tip.tip_text
            
            # Generate embedding
            text_to_embed = tip.translated_text or tip.tip_text
            embedding_vector = embedding_service.embed(text_to_embed)
            
            # Store embedding
            existing_embedding = db.query(Embedding).filter(
                Embedding.tip_id == tip.id
            ).first()
            
            if existing_embedding:
                existing_embedding.embedding = embedding_vector
            else:
                embedding = Embedding(
                    tip_id=tip.id,
                    embedding=embedding_vector
                )
                db.add(embedding)
            
            # Update tip status
            tip.status = "processed"
            tip.processed_at = datetime.utcnow()
            
            stats["processed"] += 1
            stats["embedded"] += 1
            
            logger.info(f"Processed tip {tip.id}")
        
        except Exception as e:
            logger.error(f"Error processing tip {tip.id}: {e}")
            tip.status = "error"
            stats["errors"] += 1
    
    # Commit all changes
    db.commit()
    
    logger.info(f"Processing complete: {stats}")
    return stats


def run_promotion(db: Session) -> int:
    """Run tip promotion logic"""
    logger.info("Running tip promotion")
    
    promotion_service = get_promotion_service()
    promoted = promotion_service.promote_tips(db)
    
    logger.info(f"Promoted {len(promoted)} tips")
    return len(promoted)


def nightly_job(wake_pc: bool = True, run_promotion: bool = True, sleep_pc: bool = False):
    """Main nightly processing job"""
    logger.info("Starting nightly processing job")
    
    db = SessionLocal()
    try:
        # Process pending tips
        stats = process_pending_tips(db, wake_pc=wake_pc)
        
        # Run promotion if requested
        if run_promotion:
            promoted_count = run_promotion(db)
            stats["promoted"] = promoted_count
        
        logger.info(f"Nightly job completed: {stats}")
        
        # Optionally put PC to sleep
        if sleep_pc:
            wol = get_wol()
            wol.sleep_pc()
            logger.info("PC put to sleep")
    
    except Exception as e:
        logger.error(f"Nightly job error: {e}", exc_info=True)
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    # Run as standalone script
    wake_pc = "--no-wake" not in sys.argv
    run_promotion = "--no-promotion" not in sys.argv
    sleep_pc = "--sleep-pc" in sys.argv
    
    nightly_job(wake_pc=wake_pc, run_promotion=run_promotion, sleep_pc=sleep_pc)

