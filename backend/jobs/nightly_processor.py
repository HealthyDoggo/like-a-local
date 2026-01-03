"""
Nightly processing job for tips.

This job runs on the Raspberry Pi and coordinates the processing pipeline:
1. Wakes PC via Wake-on-LAN (if PC is sleeping)
2. Processes pending tips on PC (translation + embedding)
3. Stores results back to Pi's PostgreSQL database
4. Optionally puts PC back to sleep

Data flow:
- Input: Tips stored in PostgreSQL on Pi (status='pending')
- Processing: Translation (NLLB) and embedding (miniLM-v6) run on PC
- Output: Translated text and embeddings stored back in Pi's database

Network path: Pi (ethernet) -> Router -> WiFi -> Node -> PC
"""
import logging
import sys
from datetime import datetime
from sqlalchemy.orm import Session
from backend.database.connection import SessionLocal
from backend.database.models import Tip, Embedding
from backend.services.processing_client import get_processing_client
from backend.services.promotion import get_promotion_service
from backend.utils.wol import get_wol
from backend.config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def process_pending_tips(db: Session, wake_pc: bool = True) -> dict:
    """
    Process all pending tips: translate and generate embeddings.
    
    This function:
    1. Fetches tips with status='pending' from Pi's PostgreSQL database
    2. Wakes PC if needed (checks if already awake first)
    3. For each tip:
       - Detects language
       - Translates to English using NLLB (if not already English)
       - Generates vector embedding using miniLM-v6
       - Stores results back to Pi's database
    4. Updates tip status to 'processed'
    
    Note: Translation and embedding models run on PC, but results are stored
    back on Pi's database. The PC is used for computation only.
    
    Args:
        db: Database session (connected to Pi's PostgreSQL)
        wake_pc: Whether to wake PC if sleeping (if False, assumes PC is already on)
        
    Returns:
        Dictionary with processing statistics
    """
    stats = {
        "processed": 0,
        "translated": 0,
        "embedded": 0,
        "errors": 0
    }
    
    # Fetch pending tips from Pi's PostgreSQL database
    # These are tips submitted via API and stored with status='pending'
    pending_tips = db.query(Tip).filter(Tip.status == "pending").all()
    
    if not pending_tips:
        logger.info("No pending tips to process")
        return stats
    
    logger.info(f"Processing {len(pending_tips)} pending tips")
    
    # Wake PC if needed (only if PC is sleeping - checks first)
    # If PC is already on, wake() returns True immediately without sending packet
    if wake_pc:
        wol = get_wol()
        if not wol.wake():
            logger.error("Failed to wake PC, but continuing with processing")
            # Continue anyway - PC might already be on or processing can happen later
    
    # Initialize processing client (connects to PC's processing API)
    # The PC must have a processing service running (see processing_service.py)
    processing_client = get_processing_client()
    
    # Check if PC processing service is available
    if not processing_client.health_check():
        logger.error("PC processing service is not available. Make sure it's running on the PC.")
        logger.error(f"Expected service at: {processing_client.api_url}")
        return stats
    
    # Process each tip
    for tip in pending_tips:
        try:
            # Step 1: Detect language and translate if needed
            # This sends HTTP request to PC's processing API
            # PC runs NLLB model and returns translated text
            if not tip.translated_text:
                detected_lang = processing_client.detect_language(tip.tip_text)
                tip.original_language = detected_lang
                
                # Translate if not English (PC processes this using NLLB)
                if detected_lang != "en":
                    tip.translated_text = processing_client.translate(
                        tip.tip_text,
                        source_language=detected_lang
                    )
                    stats["translated"] += 1
                else:
                    # Already English, use original text
                    tip.translated_text = tip.tip_text
            
            # Step 2: Generate vector embedding (PC processes this using miniLM-v6)
            # This sends HTTP request to PC's processing API
            # PC generates embedding and returns vector
            text_to_embed = tip.translated_text or tip.tip_text
            embedding_vector = processing_client.embed(text_to_embed)
            
            # Step 3: Store embedding back to Pi's PostgreSQL database
            # Check if embedding already exists (in case of re-processing)
            existing_embedding = db.query(Embedding).filter(
                Embedding.tip_id == tip.id
            ).first()
            
            if existing_embedding:
                # Update existing embedding
                existing_embedding.embedding = embedding_vector
            else:
                # Create new embedding record
                embedding = Embedding(
                    tip_id=tip.id,
                    embedding=embedding_vector  # Stored as REAL[] array in PostgreSQL
                )
                db.add(embedding)
            
            # Step 4: Update tip status to 'processed' in Pi's database
            tip.status = "processed"
            tip.processed_at = datetime.utcnow()
            
            stats["processed"] += 1
            stats["embedded"] += 1
            
            logger.info(f"Processed tip {tip.id}")
        
        except Exception as e:
            logger.error(f"Error processing tip {tip.id}: {e}")
            tip.status = "error"
            stats["errors"] += 1
    
    # Commit all changes to Pi's PostgreSQL database
    # This saves: translated_text, original_language, embedding, status, processed_at
    db.commit()
    
    logger.info(f"Processing complete: {stats}")
    return stats


def run_promotion(db: Session) -> int:
    """
    Run tip promotion logic to identify frequently mentioned tips.
    
    This analyzes processed tips in Pi's database to find:
    - Tips mentioned multiple times for the same location
    - Similar tips (using vector similarity)
    - Promotes tips that meet threshold criteria
    
    All processing happens on Pi using embeddings already stored in database.
    
    Args:
        db: Database session (connected to Pi's PostgreSQL)
        
    Returns:
        Number of tips promoted
    """
    logger.info("Running tip promotion")
    
    promotion_service = get_promotion_service()
    promoted = promotion_service.promote_tips(db)
    
    logger.info(f"Promoted {len(promoted)} tips")
    return len(promoted)


def nightly_job(wake_pc: bool = True, run_promotion: bool = True, sleep_pc: bool = False):
    """
    Main nightly processing job entry point.
    
    This is the main function called by cron or manually. It:
    1. Connects to Pi's PostgreSQL database
    2. Wakes PC if needed (only if sleeping - checks first)
    3. Processes pending tips (translation + embedding on PC, results stored on Pi)
    4. Runs promotion logic (on Pi using stored embeddings)
    5. Optionally puts PC back to sleep
    
    Data flow summary:
    - Tips read from: Pi PostgreSQL (status='pending')
    - Processing happens: On PC (translation/embedding models)
    - Results written to: Pi PostgreSQL (translated_text, embeddings, status='processed')
    - Promotion runs: On Pi (using stored embeddings)
    
    Args:
        wake_pc: Whether to wake PC if sleeping (if False, assumes PC is already on)
        run_promotion: Whether to run tip promotion after processing
        sleep_pc: Whether to put PC to sleep after processing (optional)
    """
    logger.info("Starting nightly processing job")
    
    # Connect to Pi's PostgreSQL database
    db = SessionLocal()
    try:
        # Process pending tips
        # This wakes PC if needed, processes tips, stores results back to Pi's DB
        stats = process_pending_tips(db, wake_pc=wake_pc)
        
        # Run promotion if requested
        # This runs entirely on Pi using embeddings already in database
        if run_promotion:
            promoted_count = run_promotion(db)
            stats["promoted"] = promoted_count
        
        logger.info(f"Nightly job completed: {stats}")
        
        # Optionally put PC to sleep to save power
        # Only works if SSH is configured and PC supports it
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

