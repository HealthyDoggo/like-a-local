# Performance Optimizations for PC Processing

This document describes the performance optimizations implemented for the PC processing service to maximize CPU utilization on your Ryzen 7 7700 (8 cores/16 threads).

## Changes Implemented

### 1. PC Service: Multiple Worker Processes

The FastAPI processing service now supports multiple worker processes to handle concurrent requests in parallel.

**Start the PC service with workers:**
```bash
# Default: 4 workers (recommended for Ryzen 7 7700)
python pc_processing_service.py

# Custom number of workers (can go up to 8 for your CPU)
python pc_processing_service.py --workers 8

# Development mode with auto-reload (single worker)
python pc_processing_service.py --reload
```

**Why this helps:**
- Each worker process can handle translation/embedding independently
- CPU-bound ML operations run in parallel across cores
- Maximizes utilization of your 8-core CPU

### 2. Pi Client: Concurrent Batch Requests

The nightly processor on the Pi now sends multiple batch requests concurrently using ThreadPoolExecutor.

**Processing flow:**
1. Fetches pending tips from database
2. Splits into batches of 20 tips each
3. Sends 4 concurrent batch requests to PC
4. PC processes batches in parallel using worker processes
5. Results stored back to Pi database

**Default configuration:**
- Batch size: 20 tips per request
- Concurrent workers: 4 parallel requests
- Total batch limit: 100 tips per run

**Why this helps:**
- Network latency hidden by parallel requests
- PC CPU stays busy processing multiple batches
- Much faster than sequential processing

### 3. Batch Processing Endpoint

The `/process-batch` endpoint was already implemented and is now being used instead of individual requests.

**Endpoint:** `POST /process-batch`

**Benefits:**
- Models load once per batch (not per tip)
- More efficient GPU/CPU utilization
- Reduced network overhead

## Performance Comparison

### Before (Sequential Processing)
- 1 tip at a time
- 3 API calls per tip (detect language, translate, embed)
- ~2-3 seconds per tip
- **100 tips = ~5 minutes**

### After (Concurrent Batch Processing)
- 4 concurrent batches of 20 tips each
- 1 API call per batch (detect + translate + embed)
- ~30-40 seconds per batch of 20
- **100 tips = ~40-60 seconds**

**Estimated speedup: 5-8x faster**

## Configuration Options

### Adjusting Concurrency

Edit `backend/jobs/nightly_processor.py` if you want to tune performance:

```python
# In nightly_job() function, you can pass custom parameters:
stats = process_pending_tips(
    db,
    wake_pc=wake_pc,
    batch_size=200,      # Process more tips per run
    max_workers=6        # More concurrent requests
)
```

### Recommended Settings for Ryzen 7 7700

**PC Service:**
```bash
python pc_processing_service.py --workers 6
```

**Pi Processor:**
- `batch_size=100` (default is good)
- `max_workers=4-6` (4 is safe, 6 for max performance)

## Monitoring Performance

When the nightly job runs, you'll see logs like:

```
INFO - Processing 100 pending tips with 4 concurrent workers
INFO - Completed batch of 20 tips (12 translated)
INFO - Completed batch of 20 tips (15 translated)
INFO - Completed batch of 20 tips (8 translated)
INFO - Completed batch of 20 tips (18 translated)
INFO - Processing complete: {'processed': 100, 'translated': 53, 'embedded': 100, 'errors': 0}
```

## Notes

- The `/process-batch` endpoint processes translation and embedding in one call
- Concurrent requests work because FastAPI is async and uses multiple workers
- Your Ryzen 7 7700 can easily handle 4-8 concurrent ML inference tasks
- Network bandwidth between Pi and PC might be the bottleneck, not CPU
