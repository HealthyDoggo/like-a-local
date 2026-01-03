# Processing Architecture

## Current Issue

The original implementation had a confusion: the `TranslationService` and `EmbeddingService` were designed to run on the Pi, but the architecture called for processing on the PC. 

**The problem:** The services load models directly where they run, so if they run on the Pi, the models run on the Pi (which doesn't have enough power).

## Solution: Client-Server Architecture

The system now uses a **client-server architecture**:

### On Raspberry Pi (Client):
- `ProcessingClient` - Makes HTTP requests to PC
- `nightly_processor.py` - Orchestrates processing, uses client to send requests
- Reads/writes to Pi's PostgreSQL database

### On PC (Server):
- Processing service API (needs to be created) - Receives requests, runs models
- NLLB translation model
- miniLM-v6 embedding model
- Returns results to Pi

## Data Flow

```
┌─────────────────┐
│  Raspberry Pi   │
│                 │
│ 1. Read tips    │──┐
│    from DB      │  │
│                 │  │
│ 2. Send HTTP    │──┼──► ┌──────────────┐
│    request      │  │    │      PC      │
│    to PC        │  │    │              │
│                 │  │    │ 3. Translate │
│ 5. Store        │◄─┼──┐ │    (NLLB)    │
│    results      │  │  │ │              │
│    in DB        │  │  │ │ 4. Embed     │
└─────────────────┘  │  │ │    (miniLM)  │
                     │  │ │              │
                     │  │ │ 5. Return    │
                     │  │ │    results   │
                     │  │ └──────────────┘
                     │  │
                     └──┘
```

### Step-by-Step:

1. **Pi reads tips** from PostgreSQL (status='pending')
2. **Pi wakes PC** via Wake-on-LAN (if sleeping)
3. **Pi sends HTTP POST** to PC's processing API with tip text
4. **PC processes**:
   - Detects language
   - Translates using NLLB (if needed)
   - Generates embedding using miniLM-v6
5. **PC returns** translated text and embedding vector
6. **Pi stores** results back to PostgreSQL
7. **Pi updates** tip status to 'processed'

## Implementation Status

✅ **Completed:**
- `ProcessingClient` - Client on Pi that makes HTTP requests
- Updated `nightly_processor.py` to use client
- Configuration for PC API URL

❌ **Still Needed:**
- PC processing service API (FastAPI service on PC)
- This service should:
  - Expose `/translate`, `/embed`, `/detect-language` endpoints
  - Load NLLB and miniLM-v6 models
  - Run on PC's port 8001 (or configurable)

## Next Steps

1. Create `pc_processing_service.py` - FastAPI service for PC
2. Install dependencies on PC (transformers, sentence-transformers, torch)
3. Run service on PC: `python pc_processing_service.py`
4. Configure Pi's `.env` with PC API URL
5. Test end-to-end processing

## Alternative: Direct Model Access

If you want models to run directly on Pi (not recommended for large models):
- Keep `TranslationService` and `EmbeddingService` as-is
- They will run on Pi (slow, may run out of memory)
- No PC needed for processing (only for WOL if you want to wake it)

## Alternative: SSH-Based Processing

Instead of HTTP API, could use SSH to run commands on PC:
- Pi SSHs into PC
- Executes Python script with tip text
- Gets results back via stdout
- More complex but no API needed

