# TravelBuddy Backend

Backend API server for TravelBuddy, running on Raspberry Pi.

## Features

- REST API for tip submission and querying
- PostgreSQL database for data storage
- NLLB translation service for multilingual tips
- Vector embeddings using sentence-transformers (miniLM-v6)
- Wake-on-LAN integration for PC-based processing
- Nightly batch processing job
- Tip promotion based on frequency and similarity

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL with pgvector extension
- Raspberry Pi (or compatible Linux system)

### Installation

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up PostgreSQL:
```bash
# Create database
createdb travelbuddy

# Install pgvector extension (if available)
psql -d travelbuddy -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Or use the schema file
psql -d travelbuddy -f database/schema.sql
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

### Configuration

Edit `.env` file with your settings:
- `DATABASE_URL`: PostgreSQL connection string
- `PC_MAC_ADDRESS`: MAC address of PC for wake-on-lan
- `PC_IP_ADDRESS`: IP address of PC
- `NLLB_MODEL_NAME`: NLLB model to use (default: facebook/nllb-200-3.3B)
- `EMBEDDING_MODEL_NAME`: Embedding model (default: sentence-transformers/all-MiniLM-L6-v2)

## Running

### Development

```bash
python -m backend.main
```

Or with uvicorn:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Production

Use a process manager like systemd or supervisor to run the API server.

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /api/tips` - Submit new tip
- `GET /api/tips` - Query tips (with filters)
- `GET /api/tips/{id}` - Get specific tip
- `GET /api/locations` - Get all locations
- `GET /api/locations/{id}` - Get specific location
- `GET /api/locations/{id}/tips` - Get tips for location
- `POST /api/jobs/process` - Manually trigger processing
- `POST /api/jobs/promote` - Manually trigger promotion

## Nightly Processing

The nightly job processes pending tips:
1. Wakes PC via wake-on-lan
2. Translates tips using NLLB
3. Generates embeddings using miniLM-v6
4. Stores results in database
5. Optionally puts PC back to sleep

### Running Manually

```bash
python -m backend.jobs.nightly_processor
```

### Scheduling with Cron

Add to crontab:
```bash
0 2 * * * /path/to/venv/bin/python -m backend.jobs.nightly_processor
```

## Architecture

- **FastAPI**: Web framework
- **SQLAlchemy**: ORM for database
- **PostgreSQL**: Database with pgvector for vector storage
- **NLLB**: Facebook's No Language Left Behind translation model
- **sentence-transformers**: Embedding generation
- **wakeonlan**: Wake-on-LAN magic packet sending

## Network Setup

The system supports multi-hop network routing:
- Pi (ethernet) -> Router -> WiFi -> Node -> PC

Wake-on-LAN packets are sent through the network to wake the PC for processing.

