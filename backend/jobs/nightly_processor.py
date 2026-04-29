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
from backend.services.category_classifier import get_category_classifier
from backend.services.llm_classifier import get_llm_classifier
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

    # Process batches concurrently using ThreadPoolExecutor.
    # IMPORTANT: index futures by batch position so results are reassembled in
    # the original tip order regardless of which batch completes first.
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_idx = {
            executor.submit(process_single_batch, batch): i
            for i, batch in enumerate(tip_batches)
        }

        # Collect into a dict keyed by batch index (as_completed is unordered)
        batch_results: dict[int, list] = {}
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            batch = tip_batches[idx]
            try:
                results, translations = future.result()
                batch_results[idx] = results
                translated_count += translations
                logger.info(f"Completed batch {idx} of {len(batch)} tips ({translations} translated)")
            except Exception as e:
                logger.error(f"Batch future error (batch {idx}): {e}")
                batch_results[idx] = []
                error_count += len(batch)

    # Reconstruct in original order so results[i] always maps to tips_batch[i]
    for idx in range(len(tip_batches)):
        all_results.extend(batch_results.get(idx, []))

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

    # Check there is anything to do before waking the PC
    first_check = db.query(Tip).filter(Tip.status == "pending").first()
    if not first_check:
        logger.info("No pending tips to process")
        return stats, []

    # Wake PC once before the loop
    if wake_pc:
        wol = get_wol()
        if not wol.wake():
            logger.error("Failed to wake PC")
            return stats, []

    processing_client = get_processing_client()
    if not processing_client.health_check():
        logger.error("PC processing service is not available")
        logger.error(f"Expected service at: {processing_client.api_url}")
        return stats, []

    # Track every tip processed across all batches for classification at the end
    all_processed_tips: list[Tip] = []

    # Drain the pending queue in chunks of batch_size
    while True:
        pending_tips = db.query(Tip).filter(Tip.status == "pending").limit(batch_size).all()
        if not pending_tips:
            break

        logger.info(f"Processing batch of {len(pending_tips)} pending tips")

        # --- Translate to English + generate embeddings ---
        results, translated_count, error_count = process_batch_concurrent(
            pending_tips,
            processing_client,
            max_workers=max_workers
        )

        stats["translated"] += translated_count
        stats["errors"] += error_count

        for i, tip in enumerate(pending_tips):
            if i >= len(results):
                tip.status = "error"
                continue
            try:
                result = results[i]
                tip.translated_text = result.get("translated_text")
                tip.original_language = result.get("language")

                embedding_vector = result.get("embedding", [])
                if embedding_vector:
                    existing_embedding = db.query(Embedding).filter(
                        Embedding.tip_id == tip.id
                    ).first()
                    if existing_embedding:
                        existing_embedding.embedding = embedding_vector
                    else:
                        db.add(Embedding(tip_id=tip.id, embedding=embedding_vector))
                    stats["embedded"] += 1

                tip.status = "processed"
                tip.processed_at = datetime.utcnow()
                stats["processed"] += 1

            except Exception as e:
                logger.error(f"Error storing results for tip {tip.id}: {e}")
                tip.status = "error"
                stats["errors"] += 1

        db.commit()

        all_processed_tips.extend(t for t in pending_tips if t.status == "processed")

    # --- Classify all tips processed in this run (runs once, after all batches) ---
    logger.info(f"Classifying tips into categories (method: {settings.classification_method})...")
    try:
        use_llm = settings.classification_method == "llm"

        if use_llm:
            classifier = get_llm_classifier()
        else:
            classifier = get_category_classifier()
        classifier.load_categories(db)

        classified_count = 0
        for tip in all_processed_tips:
            if tip.category_manual:
                continue
            try:
                if use_llm:
                    text = tip.translated_text or tip.tip_text
                    category_id, confidence = classifier.classify_tip(text)
                else:
                    embedding_obj = db.query(Embedding).filter(Embedding.tip_id == tip.id).first()
                    if not embedding_obj:
                        continue
                    category_id, confidence = classifier.classify_tip(embedding_obj.embedding)

                if category_id and classifier.should_assign_category(confidence):
                    tip.category_id = category_id
                    tip.category_confidence = confidence
                    tip.category_assigned_at = datetime.utcnow()
                    classified_count += 1
            except Exception as e:
                logger.error(f"Error classifying tip {tip.id}: {e}")

        db.commit()
        stats["classified"] = classified_count
        logger.info(f"Classified {classified_count} tips into categories")

    except Exception as e:
        logger.error(f"Category classification error: {e}")
        stats["classification_errors"] = 1

    logger.info(f"Processing complete: {stats}")
    return stats, all_processed_tips


def run_promotion(db: Session, new_tips: List[Tip] = None) -> int:
    """
    Run tip promotion logic to identify frequently mentioned tips.

    When new_tips is provided (nightly job), only those tips are compared
    against existing promotions (incremental mode). When None, all tips are
    reclustered from scratch (forced via API endpoint after e.g. a threshold
    change).

    All processing happens on Pi using embeddings already stored in database.

    Args:
        db: Database session (connected to Pi's PostgreSQL)
        new_tips: Tips processed in the current run, or None for full recluster

    Returns:
        Number of tips promoted
    """
    logger.info("Running tip promotion")

    promotion_service = get_promotion_service()
    promoted = promotion_service.promote_tips(db, new_tips=new_tips)

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
        stats, processed_tips = process_pending_tips(db, wake_pc=wake_pc)

        # Run promotion only when tips were actually processed this run.
        # Pass the newly processed tips so promotion compares them against
        # existing promotions rather than reclustering all tips from scratch.
        if promote and processed_tips:
            promoted_count = run_promotion(db, new_tips=processed_tips)
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

