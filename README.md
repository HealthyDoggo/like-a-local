# Like a Local

A mobile-first app that helps travelers discover authentic, locally-sourced tips about destinations around the world.

## What it does

Travellers submit tips about places they know well. Each tip goes through a processing pipeline: language detection, English translation, and semantic embedding — enabling multilingual search and similarity-based tip clustering across 15 languages.

## Architecture

```
┌─────────────────────┐        ┌──────────────────────┐
│   Mobile App        │        │   Raspberry Pi        │
│   (React/Capacitor) │◄──────►│   FastAPI + PostgreSQL│
│                     │  REST  │                       │
│  iOS / Android      │        │  Auth, Tips, Locations│
└─────────────────────┘        └──────────┬───────────┘
                                           │  HTTP (nightly)
                                           ▼
                               ┌──────────────────────┐
                               │   PC (Processing)     │
                               │                       │
                               │  NLLB Translation     │
                               │  miniLM-v6 Embedding  │
                               └──────────────────────┘
```

**Frontend**: React + TypeScript, Vite, Capacitor (iOS/Android), Tailwind CSS
**Backend API**: FastAPI on Raspberry Pi, PostgreSQL
**Processing**: ML models run on a separate PC, called nightly from the Pi via HTTP

## Processing Pipeline

Tips submitted by users are stored with `status='pending'`. Each night the Pi runs `nightly_processor.py`, which:

1. **Wakes the PC** via Wake-on-LAN (if sleeping)
2. **Detects language** of each tip
3. **Translates to English** using [facebook/nllb-200-3.3B](https://huggingface.co/facebook/nllb-200-3.3B)
4. **Generates a semantic embedding** using [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
5. **Translates the English tip into all 15 supported languages** so users see tips in their chosen language
6. **Classifies into a category** using cosine similarity against category centroid embeddings
7. **Clusters similar tips** and promotes the most-mentioned ones per location

Processing uses concurrent batch requests to fully utilise the PC's CPU across all steps.

## Supported Languages

English, Spanish, French, German, Italian, Portuguese, Russian, Japanese, Korean, Chinese, Arabic, Hindi, Thai, Vietnamese, Indonesian

## Getting Started

### Prerequisites

- Node.js + npm (frontend)
- Python 3.10+ (backend + processing service)
- PostgreSQL (on Pi or local)
- PyTorch + Transformers + sentence-transformers (PC only, for ML models)

### Backend (Raspberry Pi / local)

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # set DB URL, secret key, PC API URL
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### PC Processing Service

```bash
pip install -r requirements.txt
python pc_processing_service.py
# Listens on :8001 by default
```

### Frontend

```bash
cd FigmaMake
npm install
npm run dev            # browser dev server
npx cap run ios        # or android
```

### Run the nightly processor manually

```bash
python -m backend.jobs.nightly_processor
# Flags: --no-wake  --no-promotion  --sleep-pc
```

## Project Structure

```
TravelBuddy/
├── backend/
│   ├── api/              # FastAPI route handlers
│   ├── database/         # SQLAlchemy models + connection
│   ├── jobs/
│   │   └── nightly_processor.py   # Orchestrates batch processing
│   ├── services/
│   │   ├── translation.py         # NLLB wrapper
│   │   ├── embedding.py           # miniLM-v6 wrapper
│   │   ├── processing_client.py   # HTTP client → PC service
│   │   ├── promotion.py           # Tip clustering & promotion
│   │   └── category_classifier.py # Cosine similarity classifier
│   └── utils/
│       └── wol.py                 # Wake-on-LAN
├── pc_processing_service.py       # FastAPI service (runs on PC)
└── FigmaMake/                     # React/Capacitor mobile app
    └── src/
        ├── app/                   # Screen components
        ├── contexts/              # Auth context
        ├── hooks/                 # useTips, useSettings, etc.
        └── services/              # API client, auth, OAuth
```
