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
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple
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


def process_batch_concurrent(
    tips_batch: List[Tip],
    processing_client,
    max_workers: int = 4
) -> Tuple[List[dict], int, int]:
    """
    Process a batch of tips using concurrent requests to PC.

    This function sends multiple batch requests concurrently to maximize
    PC CPU utilization (Ryzen 7 7700: 8 cores/16 threads).

    Args:
        tips_batch: List of Tip objects to process
        processing_client: ProcessingClient instance
        max_workers: Number of concurrent threads (default: 4)

    Returns:
        Tuple of (results, translated_count, error_count)
    """
    # Split tips into smaller batches for concurrent processing
    # Each batch gets processed in parallel by different PC worker processes
    batch_size = 20  # 20 tips per request
    tip_batches = [tips_batch[i:i + batch_size] for i in range(0, len(tips_batch), batch_size)]

    all_results = []
    translated_count = 0
    error_count = 0

    def process_single_batch(batch: List[Tip]) -> Tuple[List[dict], int]:
        """Process a single batch via PC API"""
        texts = [tip.tip_text for tip in batch]
        try:
            results = processing_client.process_batch(texts)
            # Count translations (non-English texts that were translated)
            translations = sum(1 for r in results if r.get("language") != "en")
            return results, translations
        except Exception as e:
            logger.error(f"Batch processing error: {e}")
            return [], 0

    # Process batches concurrently using ThreadPoolExecutor
    # This sends multiple HTTP requests in parallel to the PC
    # PC's FastAPI with multiple workers can handle them concurrently
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all batch processing tasks
        future_to_batch = {
            executor.submit(process_single_batch, batch): batch
            for batch in tip_batches
        }

        # Collect results as they complete
        for future in as_completed(future_to_batch):
            batch = future_to_batch[future]
            try:
                results, translations = future.result()
                all_results.extend(results)
                translated_count += translations
                logger.info(f"Completed batch of {len(batch)} tips ({translations} translated)")
            except Exception as e:
                logger.error(f"Batch future error: {e}")
                error_count += len(batch)

    return all_results, translated_count, error_count


def process_pending_tips(
    db: Session,
    wake_pc: bool = True,
    batch_size: int = 100,
    max_workers: int = 4
) -> dict:
    """
    Process all pending tips: translate and generate embeddings.

    This function uses batch processing with concurrent requests for optimal
    performance on the PC (Ryzen 7 7700: 8 cores/16 threads).

    Processing strategy:
    1. Fetches tips with status='pending' from Pi's PostgreSQL database
    2. Wakes PC if needed (checks if already awake first)
    3. Splits tips into batches (default: 20 tips per batch)
    4. Sends multiple batches concurrently (default: 4 concurrent requests)
    5. PC processes each batch in parallel using multiple worker processes
    6. Stores results back to Pi's database

    Performance improvements over sequential processing:
    - Uses /process-batch endpoint (efficient batch processing on PC)
    - Concurrent requests maximize PC CPU utilization
    - Network latency hidden by parallel requests

    Args:
        db: Database session (connected to Pi's PostgreSQL)
        wake_pc: Whether to wake PC if sleeping (default: True)
        batch_size: Max tips to process in one run (default: 100)
        max_workers: Number of concurrent threads (default: 4)

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
    pending_tips = db.query(Tip).filter(Tip.status == "pending").limit(batch_size).all()

    if not pending_tips:
        logger.info("No pending tips to process")
        return stats

    logger.info(f"Processing {len(pending_tips)} pending tips with {max_workers} concurrent workers")

    # Wake PC if needed
    if wake_pc:
        wol = get_wol()
        if not wol.wake():
            logger.error("Failed to wake PC")
            return stats

    # Initialize processing client
    processing_client = get_processing_client()

    # Check if PC processing service is available
    if not processing_client.health_check():
        logger.error("PC processing service is not available")
        logger.error(f"Expected service at: {processing_client.api_url}")
        return stats

    # Process tips in batches with concurrent requests
    results, translated_count, error_count = process_batch_concurrent(
        pending_tips,
        processing_client,
        max_workers=max_workers
    )

    stats["translated"] = translated_count
    stats["errors"] = error_count

    # Store results back to database
    for i, tip in enumerate(pending_tips):
        if i >= len(results):
            # Error occurred for this tip
            tip.status = "error"
            continue

        try:
            result = results[i]

            # Store translated text and language
            tip.translated_text = result.get("translated_text")
            tip.original_language = result.get("language")

            # Store embedding
            embedding_vector = result.get("embedding", [])
            if embedding_vector:
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

                stats["embedded"] += 1

            # Update tip status
            tip.status = "processed"
            tip.processed_at = datetime.utcnow()
            stats["processed"] += 1

        except Exception as e:
            logger.error(f"Error storing results for tip {tip.id}: {e}")
            tip.status = "error"
            stats["errors"] += 1

    # Commit all changes
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


def nightly_job(wake_pc: bool = True, promote: bool = True, sleep_pc: bool = False):
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
        promote: Whether to run tip promotion after processing
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
        if promote:
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
    promote = "--no-promotion" not in sys.argv
    sleep_pc = "--sleep-pc" in sys.argv
    
    nightly_job(wake_pc=wake_pc, promote=promote, sleep_pc=sleep_pc)

