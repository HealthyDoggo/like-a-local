# TravelBuddy Backend Completion Plan

## Current Architecture

```
┌──────────────┐         ┌──────────────────┐         ┌─────────────┐
│              │  HTTP   │  Raspberry Pi    │   WOL   │     PC      │
│  Kivy App    │◄───────►│                  │◄───────►│             │
│  (Mobile)    │         │  FastAPI Backend │  HTTP   │  ML Service │
│              │         │  PostgreSQL DB   │         │  (Port 8001)│
└──────────────┘         └──────────────────┘         └─────────────┘
                                  │
                                  │ 2am daily
                                  ↓
                         ┌─────────────────┐
                         │ Nightly Batch   │
                         │ Processing:     │
                         │ 1. Wake PC      │
                         │ 2. Translate    │
                         │ 3. Embed        │
                         │ 4. Promote tips │
                         └─────────────────┘
```

## Current Status: ✅ 85% Complete

### What's Working
- ✅ FastAPI REST API with all endpoints
- ✅ PostgreSQL database with complete schema
- ✅ PC processing service (translation + embeddings)
- ✅ Wake-on-LAN integration
- ✅ Nightly batch processor
- ✅ Tip promotion logic (similarity clustering)
- ✅ API client for Kivy app
- ✅ Test data generation
- ✅ Comprehensive documentation

### What's Missing
- ❌ Production deployment setup
- ❌ Authentication/security
- ❌ Testing infrastructure
- ❌ Monitoring/logging
- ❌ Search functionality
- ❌ User management

---

## Phase 1: Essential Production Readiness (Week 1-2)

### 1.1 Deployment Automation
**Priority: CRITICAL**

#### Raspberry Pi Service Setup
```bash
# Create systemd service
sudo nano /etc/systemd/system/travelbuddy-backend.service
```

```ini
[Unit]
Description=TravelBuddy FastAPI Backend
After=network.target postgresql.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/TravelBuddy/backend
Environment="PATH=/home/pi/.local/bin:/usr/bin"
ExecStart=/home/pi/.local/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable travelbuddy-backend
sudo systemctl start travelbuddy-backend
```

#### Nightly Job Scheduler
```bash
# Add to crontab
crontab -e

# Run at 2 AM daily
0 2 * * * /usr/bin/python3 /home/pi/TravelBuddy/backend/jobs/nightly_processor.py >> /var/log/travelbuddy-nightly.log 2>&1
```

#### PC Service Setup (Windows Task Scheduler)
1. Create `start_processing_service.bat`:
```batch
@echo off
cd C:\TravelBuddy\backend
python pc_processing_service.py --host 0.0.0.0 --port 8001
```

2. Task Scheduler:
   - Trigger: At startup
   - Action: Run batch file
   - Run whether user is logged on or not

**Tasks:**
- [ ] Create systemd service file
- [ ] Set up automatic startup
- [ ] Configure nightly cron job
- [ ] Set up PC service auto-start
- [ ] Test service restart on failure
- [ ] Document startup procedures

### 1.2 Reverse Proxy & SSL
**Priority: HIGH**

#### Nginx Configuration
```nginx
server {
    listen 80;
    server_name travelbuddy.local;  # or your domain

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Increase timeout for long processing
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}

# Optional: SSL with Let's Encrypt
# server {
#     listen 443 ssl;
#     server_name travelbuddy.local;
#     ssl_certificate /etc/letsencrypt/live/travelbuddy.local/fullchain.pem;
#     ssl_certificate_key /etc/letsencrypt/live/travelbuddy.local/privkey.pem;
#     ...
# }
```

**Tasks:**
- [ ] Install nginx on Raspberry Pi
- [ ] Create nginx config
- [ ] Set up SSL (if public)
- [ ] Configure firewall rules
- [ ] Test HTTPS connections

### 1.3 Logging & Monitoring
**Priority: HIGH**

#### Structured Logging
Update `backend/main.py`:
```python
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
log_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# File handler with rotation
file_handler = RotatingFileHandler(
    '/var/log/travelbuddy/backend.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
file_handler.setFormatter(log_formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

# Root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
```

#### Health Check Endpoint Enhancement
```python
from database.connection import get_db
from utils.network import check_pc_awake

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    status = {
        "api": "healthy",
        "database": "unknown",
        "pc_service": "unknown"
    }

    # Check database
    try:
        db = next(get_db())
        db.execute("SELECT 1")
        status["database"] = "healthy"
    except Exception as e:
        status["database"] = f"unhealthy: {str(e)}"

    # Check PC (optional, don't wake it)
    if check_pc_awake(config.PC_IP):
        status["pc_service"] = "awake"
    else:
        status["pc_service"] = "sleeping (normal)"

    return status
```

**Tasks:**
- [ ] Add rotating file logging
- [ ] Create log directory with permissions
- [ ] Enhance health check endpoint
- [ ] Add error tracking (Sentry optional)
- [ ] Set up log monitoring/alerts

### 1.4 Database Backups
**Priority: HIGH**

#### Automated Backup Script
Create `backend/scripts/backup_database.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/home/pi/backups/travelbuddy"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/travelbuddy_$DATE.sql"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U travelbuddy -h localhost travelbuddy > $BACKUP_FILE

# Compress
gzip $BACKUP_FILE

# Keep only last 14 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +14 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

```bash
# Add to crontab - daily at 3 AM
0 3 * * * /home/pi/TravelBuddy/backend/scripts/backup_database.sh
```

**Tasks:**
- [ ] Create backup script
- [ ] Schedule daily backups
- [ ] Test restore procedure
- [ ] Document backup/restore process

---

## Phase 2: Security & Authentication (Week 3-4)

### 2.1 API Key Authentication
**Priority: MEDIUM** (depends on if app is public)

#### Simple API Key System
```python
# backend/api/security.py
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    return api_key
```

Update routes:
```python
from api.security import verify_api_key

@router.post("/tips", dependencies=[Depends(verify_api_key)])
async def create_tip(...):
    ...
```

**Tasks:**
- [ ] Implement API key verification
- [ ] Add API key to .env
- [ ] Update API client to send key
- [ ] Document API key usage

### 2.2 Rate Limiting
**Priority: MEDIUM**

```bash
pip install slowapi
```

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/tips")
@limiter.limit("10/minute")  # 10 tips per minute max
async def create_tip(request: Request, ...):
    ...
```

**Tasks:**
- [ ] Add slowapi dependency
- [ ] Configure rate limits per endpoint
- [ ] Test rate limiting
- [ ] Document rate limits in API docs

### 2.3 CORS Configuration
**Priority: LOW** (since it's a mobile app)

Update `main.py`:
```python
# Instead of allow_origins=["*"]
origins = [
    "http://localhost",
    "http://localhost:8000",
    # Add your actual domains if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

**Tasks:**
- [ ] Configure specific origins
- [ ] Test CORS from app
- [ ] Update documentation

---

## Phase 3: Testing Infrastructure (Week 5)

### 3.1 Unit Tests
**Priority: MEDIUM**

Create `backend/tests/`:
```
tests/
├── __init__.py
├── conftest.py          # Pytest fixtures
├── test_services/
│   ├── test_embedding.py
│   ├── test_translation.py
│   └── test_promotion.py
└── test_api/
    ├── test_tips.py
    ├── test_locations.py
    └── test_jobs.py
```

Example test:
```python
# tests/test_services/test_embedding.py
import pytest
from services.embedding import EmbeddingService

def test_generate_embedding():
    service = EmbeddingService()
    text = "This is a test"
    embedding = service.generate_embedding(text)

    assert len(embedding) == 384
    assert all(isinstance(x, float) for x in embedding)

def test_similarity():
    service = EmbeddingService()
    sim = service.calculate_similarity(
        [0.1] * 384,
        [0.1] * 384
    )
    assert sim == pytest.approx(1.0, rel=0.01)
```

**Tasks:**
- [ ] Set up pytest configuration
- [ ] Write service unit tests
- [ ] Write API endpoint tests
- [ ] Add test database setup
- [ ] Run tests in CI (optional)

---

## Phase 4: Search & Discovery (Week 6-7)

### 4.1 Full-Text Search on Tips
**Priority: HIGH**

```python
# Add PostgreSQL full-text search
@router.get("/api/tips/search")
async def search_tips(
    q: str,
    location_id: Optional[int] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Search tips using full-text search"""
    query = db.query(Tip).filter(Tip.status == "processed")

    # PostgreSQL full-text search
    if q:
        search_vector = func.to_tsvector('english', Tip.translated_text)
        search_query = func.plainto_tsquery('english', q)
        query = query.filter(search_vector.op('@@')(search_query))

    if location_id:
        query = query.filter(Tip.location_id == location_id)

    return query.limit(limit).all()
```

**Tasks:**
- [ ] Add full-text search index
- [ ] Create search endpoint
- [ ] Update API client
- [ ] Test search functionality

### 4.2 Vector Similarity Search
**Priority: HIGH**

```python
@router.get("/api/tips/{tip_id}/similar")
async def find_similar_tips(
    tip_id: int,
    limit: int = 10,
    threshold: float = 0.7,
    db: Session = Depends(get_db)
):
    """Find similar tips using embeddings"""
    # Get source tip embedding
    tip = db.query(Tip).filter(Tip.id == tip_id).first()
    if not tip or not tip.embedding:
        raise HTTPException(404, "Tip or embedding not found")

    source_embedding = tip.embedding.embedding

    # Get all embeddings for same location
    all_tips = db.query(Tip).join(Embedding).filter(
        Tip.location_id == tip.location_id,
        Tip.id != tip_id
    ).all()

    # Calculate similarities
    embedding_service = EmbeddingService()
    similar = []

    for other_tip in all_tips:
        similarity = embedding_service.calculate_similarity(
            source_embedding,
            other_tip.embedding.embedding
        )
        if similarity >= threshold:
            similar.append({
                "tip": other_tip,
                "similarity": similarity
            })

    # Sort by similarity
    similar.sort(key=lambda x: x["similarity"], reverse=True)
    return similar[:limit]
```

**Tasks:**
- [ ] Create similarity search endpoint
- [ ] Add to API client
- [ ] Update app UI to show similar tips
- [ ] Test similarity threshold tuning

---

## Phase 5: User Management (Optional - Week 8+)

### 5.1 User Registration & Authentication
**Priority: LOW** (only if needed)

This would require:
- User table with password hashing
- JWT token generation
- Login/register endpoints
- Protected endpoints
- User profile management

**Decision:** Skip for MVP unless you want users to have accounts

---

## Phase 6: Performance Optimization (Ongoing)

### 6.1 Database Indexes
**Priority: MEDIUM**

Already have most indexes, but add:
```sql
-- Add GIN index for full-text search
CREATE INDEX idx_tip_translated_text_fts
ON tips USING gin(to_tsvector('english', translated_text));

-- Add index for embedding similarity (if using pgvector in future)
-- CREATE INDEX idx_embedding_vector ON embeddings USING ivfflat (embedding);
```

### 6.2 Caching (Optional)
**Priority: LOW**

Add Redis for frequently accessed data:
```python
import redis
from functools import lru_cache

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

@lru_cache(maxsize=100)
def get_location_tips(location_id: int):
    # Cache location tips for 5 minutes
    cache_key = f"location:{location_id}:tips"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # Fetch from DB
    tips = db.query(Tip).filter(Tip.location_id == location_id).all()
    redis_client.setex(cache_key, 300, json.dumps(tips))
    return tips
```

**Tasks:**
- [ ] Install Redis (optional)
- [ ] Add caching layer
- [ ] Cache frequently accessed data
- [ ] Set appropriate TTLs

---

## Quick Start Checklist (Next Steps)

### This Weekend
- [ ] Set up systemd service on Raspberry Pi
- [ ] Configure nightly cron job (2 AM processing)
- [ ] Set up PC service auto-start
- [ ] Create database backup script
- [ ] Test full end-to-end flow

### Next Week
- [ ] Add structured logging
- [ ] Enhance health check endpoint
- [ ] Install nginx (optional)
- [ ] Test WOL + processing pipeline
- [ ] Document deployment

### Later
- [ ] Add API key authentication
- [ ] Implement rate limiting
- [ ] Create search endpoints
- [ ] Write tests
- [ ] Add monitoring

---

## Testing the Full Pipeline

### 1. Submit a tip from the app
```python
# The app will POST to Pi backend
POST http://raspberrypi.local:8000/api/tips
{
  "tip_text": "Ne bloquez pas le trottoir pour des photos",
  "location_name": "Paris",
  "location_country": "France"
}
```

### 2. Check it's stored as 'pending'
```sql
SELECT * FROM tips WHERE status = 'pending';
```

### 3. Wait for 2 AM (or manually trigger)
```bash
# Manual trigger
curl -X POST http://raspberrypi.local:8000/api/jobs/process
```

### 4. Backend will:
- Wake PC via WOL
- Wait for PC to boot
- POST tip text to `http://PC_IP:8001/process-batch`
- PC translates to English: "Don't block the sidewalk for photos"
- PC generates 384-dim embedding
- Pi stores results in database
- Tip status changes to 'processed'

### 5. Check promotion (after multiple similar tips)
```bash
curl -X POST http://raspberrypi.local:8000/api/jobs/promote
```

### 6. Query tips from app
```python
GET http://raspberrypi.local:8000/api/locations/1/tips
# Returns translated tips ranked by promotion
```

---

## Current Architecture is Excellent ✅

Your system design is actually quite sophisticated:
- **Distributed processing**: Offloading heavy ML to PC is smart
- **Wake-on-LAN**: Saves energy, PC only wakes when needed
- **Batch processing**: Efficient 2 AM processing window
- **Embedding-based promotion**: Clever use of similarity clustering
- **Multi-language support**: NLLB handles 200 languages

## What You Need to Finish

**Must Have (This Week):**
1. Systemd service for automatic startup
2. Nightly cron job (2 AM processing)
3. Database backups
4. Test full pipeline end-to-end

**Should Have (Next Week):**
5. Structured logging
6. Search endpoints
7. Enhanced health checks

**Nice to Have (Later):**
8. API authentication
9. Rate limiting
10. Monitoring/metrics
11. Tests

The backend is 85% done - you're very close to production-ready!
