# TravelBuddy API Testing Guide

Complete guide to testing the backend API, including the embedding-based tip promotion system.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Setup](#setup)
3. [Starting Services](#starting-services)
4. [Populating Test Data](#populating-test-data)
5. [Testing the Processing Pipeline](#testing-the-processing-pipeline)
6. [Testing API Endpoints](#testing-api-endpoints)
7. [Testing the Kivy App](#testing-the-kivy-app)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- Python 3.11+
- PostgreSQL
- Virtual environment activated

### Optional (for PC processing)
- PC with processing service running
- Wake-on-LAN configured (if testing WOL)

### Check Your Setup
```bash
# Verify PostgreSQL is running
sudo systemctl status postgresql

# Verify database exists
psql -U travelbuddy -d travelbuddy -c "\dt"

# Check Python environment
which python
python --version
```

---

## Setup

### 1. Environment Configuration

Check your `.env` file in the backend directory:

```bash
cat backend/.env
```

Should contain:
```env
# Database
DATABASE_URL=postgresql://travelbuddy:your_password@localhost:5432/travelbuddy

# PC Processing Service (if using remote PC)
PC_IP_ADDRESS=192.168.1.100
PC_MAC_ADDRESS=AA:BB:CC:DD:EE:FF
PC_PROCESSING_API_URL=http://192.168.1.100:8001
PC_PROCESSING_API_PORT=8001

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true

# Models (for PC processing service)
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
TRANSLATION_MODEL_NAME=facebook/nllb-200-distilled-600M
MODEL_CACHE_DIR=./models
```

### 2. Install Dependencies

```bash
# Backend dependencies
cd backend
pip install -r requirements.txt

# If testing PC processing locally
pip install transformers sentence-transformers torch langdetect
```

---

## Starting Services

### Option A: Local Testing (Everything on One Machine)

**Terminal 1: Start Backend API**
```bash
cd /path/to/TravelBuddy
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Terminal 2: Start PC Processing Service**
```bash
cd /path/to/TravelBuddy
python pc_processing_service.py --host 0.0.0.0 --port 8001
```

Expected output:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001
```

**Test Services:**
```bash
# Test backend API
curl http://localhost:8000/health

# Test PC processing service
curl http://localhost:8001/health
```

### Option B: Testing with Remote PC

**On Raspberry Pi:**
```bash
# Start backend API
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

**On PC:**
```bash
# Start processing service
cd /path/to/TravelBuddy
python pc_processing_service.py --host 0.0.0.0 --port 8001
```

**Test from Pi:**
```bash
# Test PC is reachable
curl http://YOUR_PC_IP:8001/health

# If PC is sleeping, wake it up
python -c "from backend.utils.wol import get_wol; get_wol().wake()"
```

---

## Populating Test Data

### Option 1: Promotion Test Data (Recommended)

This script creates tips specifically designed to test the promotion system with similar tips.

```bash
cd /path/to/TravelBuddy

# Clear existing data and populate
python -m backend.scripts.populate_promotion_test_data --clear

# Or just add to existing data
python -m backend.scripts.populate_promotion_test_data
```

Expected output:
```
📝 Populating database with promotion test data...
   Total tips: 50

  ✓ Created location: Paris, France
  ✓ Created location: Tokyo, Japan
  ✓ Created location: Barcelona, Spain
  ...

✅ Successfully created 50 tips
   Locations: 5

📊 Database summary:
   Pending tips: 50
   Processed tips: 0
   Total tips: 50

📍 Tips by location:
   • Paris, France: 14 tips
   • Tokyo, Japan: 7 tips
   • Barcelona, Spain: 7 tips
   • New York, United States: 7 tips
   • London, United Kingdom: 4 tips
```

### Option 2: Multi-Language Test Data

For testing translation:

```bash
python -m backend.scripts.populate_test_data -n 20
```

### Verify Data

```bash
# Check tips in database
psql -U travelbuddy -d travelbuddy -c "SELECT location_id, status, COUNT(*) FROM tips GROUP BY location_id, status;"

# Check specific location
psql -U travelbuddy -d travelbuddy -c "SELECT id, name, country FROM locations;"
```

---

## Testing the Processing Pipeline

### Step 1: Process Tips (Translation + Embeddings)

**Important:** PC processing service must be running!

```bash
cd /path/to/TravelBuddy

# Process without waking PC (assumes PC is on)
python -m backend.jobs.nightly_processor --no-wake

# Or with PC wake-up (if WOL is configured)
python -m backend.jobs.nightly_processor

# Time the processing to measure performance
time python -m backend.jobs.nightly_processor --no-wake
```

Expected output:
```
2025-01-07 10:30:00 - INFO - Starting nightly processing job
2025-01-07 10:30:01 - INFO - Processing 50 pending tips
2025-01-07 10:30:15 - INFO - Processed tip 1
2025-01-07 10:30:16 - INFO - Processed tip 2
...
2025-01-07 10:32:30 - INFO - Processing complete: {'processed': 50, 'translated': 3, 'embedded': 50, 'errors': 0}
2025-01-07 10:32:31 - INFO - Running tip promotion
2025-01-07 10:32:45 - INFO - Promoted 12 tips
2025-01-07 10:32:45 - INFO - Nightly job completed: {...}
```

**Troubleshooting:**

If you get "PC processing service is not available":
```bash
# Check PC service is running
curl http://YOUR_PC_IP:8001/health

# Check network connectivity
ping YOUR_PC_IP

# Wake PC if needed
python -c "from backend.utils.wol import get_wol; get_wol().wake()"
# Wait 30 seconds, then retry
```

### Step 2: Verify Processing

```bash
# Check processed tips
psql -U travelbuddy -d travelbuddy -c "SELECT status, COUNT(*) FROM tips GROUP BY status;"

# Check embeddings were created
psql -U travelbuddy -d travelbuddy -c "SELECT COUNT(*) FROM embeddings;"

# Check promoted tips
psql -U travelbuddy -d travelbuddy -c "SELECT location_id, mention_count, LEFT(tip_text, 50) FROM tip_promotions ORDER BY mention_count DESC;"
```

Expected:
```
 status    | count
-----------+-------
 processed |    50

 count
-------
    50

 location_id | mention_count |                    left
-------------+---------------+-------------------------------------------
           1 |             5 | Avoid the overpriced restaurants right...
           1 |             4 | Watch out for pickpockets on the metro...
           2 |             4 | Get a Suica or Pasmo card for trains...
```

### Step 3: Manual Promotion (Optional)

If tips are processed but not promoted:

```bash
# Trigger promotion manually via API
curl -X POST http://localhost:8000/api/jobs/promote

# Or via Python
python -c "from backend.database.connection import SessionLocal; from backend.jobs.nightly_processor import run_promotion; db = SessionLocal(); print(f'Promoted {run_promotion(db)} tips')"
```

---

## Testing API Endpoints

### Health Check

```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

### Submit a Tip

```bash
curl -X POST http://localhost:8000/api/tips \
  -H "Content-Type: application/json" \
  -d '{
    "tip_text": "Test tip: Visit the local bakery on Rue Cler",
    "location_name": "Paris",
    "location_country": "France"
  }'
```

Expected response:
```json
{
  "id": 51,
  "tip_text": "Test tip: Visit the local bakery on Rue Cler",
  "original_language": null,
  "translated_text": null,
  "location_id": 1,
  "location_name": "Paris",
  "location_country": "France",
  "user_id": null,
  "submitted_at": "2025-01-07T10:30:00",
  "processed_at": null,
  "status": "pending"
}
```

### Get All Tips

```bash
# All tips
curl http://localhost:8000/api/tips

# Filter by status
curl "http://localhost:8000/api/tips?status=processed&limit=10"

# Filter by location
curl "http://localhost:8000/api/tips?location_id=1&limit=10"
```

### Search for a Location

```bash
curl "http://localhost:8000/api/locations/search?name=Paris&country=France"
```

Expected:
```json
{
  "id": 1,
  "name": "Paris",
  "location_country": "France",
  "latitude": null,
  "longitude": null
}
```

### Get Promoted Tips (KEY ENDPOINT)

**Method 1: By Location Name (Easiest)**
```bash
curl "http://localhost:8000/api/promoted-tips?location_name=Paris&location_country=France"
```

**Method 2: By Location ID**
```bash
# First get location ID
LOCATION_ID=$(curl -s "http://localhost:8000/api/locations/search?name=Paris&country=France" | jq -r '.id')

# Then get promoted tips
curl "http://localhost:8000/api/locations/${LOCATION_ID}/promoted-tips"
```

Expected response:
```json
[
  {
    "id": 1,
    "tip_text": "Avoid the overpriced restaurants right next to the Eiffel Tower",
    "location_id": 1,
    "location_name": "Paris",
    "location_country": "France",
    "mention_count": 5,
    "similarity_score": 0.8823,
    "promoted_at": "2025-01-07T10:32:45"
  },
  {
    "id": 2,
    "tip_text": "Watch out for pickpockets on the metro, especially during rush hour",
    "location_id": 1,
    "location_name": "Paris",
    "location_country": "France",
    "mention_count": 4,
    "similarity_score": 0.9012,
    "promoted_at": "2025-01-07T10:32:45"
  }
]
```

### Test All Locations

```bash
# Test promoted tips for each location
for location in "Paris,France" "Tokyo,Japan" "Barcelona,Spain" "New York,United States" "London,United Kingdom"; do
  IFS=',' read -r name country <<< "$location"
  echo "=== $name, $country ==="
  curl -s "http://localhost:8000/api/promoted-tips?location_name=$name&location_country=$country" | jq -r '.[] | "  [\(.mention_count)x] \(.tip_text[:60])..."'
  echo ""
done
```

### Interactive API Testing

Use the auto-generated API docs:

```bash
# Open in browser
open http://localhost:8000/docs

# Or
open http://localhost:8000/redoc
```

This provides an interactive UI to test all endpoints.

---

## Testing the Kivy App

### 1. Start Backend API

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### 2. Configure API URL

Edit `.env` in project root (or set environment variable):
```bash
# For local testing
echo "TRAVELBUDDY_API_URL=http://localhost:8000" > .env

# For Pi testing (replace with your Pi's IP)
echo "TRAVELBUDDY_API_URL=http://192.168.1.50:8000" > .env
```

### 3. Run the App

```bash
python main.py
```

### 4. Test Search Flow

1. Click on "Travel" screen (✈️ icon)
2. Select a country: "France"
3. Select a city: "Paris"
4. Click "Search"

Expected behavior:
- Shows "Searching tips for Paris..."
- Loads promoted tips from API
- Displays tips with mention counts:
  ```
  • Avoid the overpriced restaurants right next to the Eiffel Tower
    (5 locals mentioned this)

  • Watch out for pickpockets on the metro, especially during rush hour
    (4 locals mentioned this)
  ```

### 5. Test Edge Cases

**No tips for location:**
- Search for a city without tips
- Should show: "No tips found yet for [City], [Country]. Be the first to share local insights!"

**API offline:**
- Stop backend API
- Search for a city
- Should show: "Error loading tips: Could not connect to API..."

**Empty location:**
- Try clicking "Search" without selecting a city
- Should do nothing (validation works)

---

## Troubleshooting

### Issue: "Could not connect to API"

**Check API is running:**
```bash
curl http://localhost:8000/health
```

**Check API URL in app:**
```bash
cat .env | grep TRAVELBUDDY_API_URL
```

**Check firewall:**
```bash
# On Pi/server
sudo ufw status
sudo ufw allow 8000
```

### Issue: "No tips found" (but tips exist in DB)

**Check tips are processed:**
```bash
psql -U travelbuddy -d travelbuddy -c "SELECT status, COUNT(*) FROM tips GROUP BY status;"
```

If all pending, run:
```bash
python -m backend.jobs.nightly_processor --no-wake
```

**Check promotion ran:**
```bash
psql -U travelbuddy -d travelbuddy -c "SELECT COUNT(*) FROM tip_promotions;"
```

If zero, run:
```bash
curl -X POST http://localhost:8000/api/jobs/promote
```

### Issue: "PC processing service is not available"

**Check PC is on:**
```bash
ping YOUR_PC_IP
```

**Check service is running:**
```bash
curl http://YOUR_PC_IP:8001/health
```

**Wake PC (if configured):**
```bash
python -c "from backend.utils.wol import get_wol; wol = get_wol(); print('Sending WOL packet...'); result = wol.wake(); print(f'Success: {result}')"
```

**Start service manually on PC:**
```bash
# On PC
cd /path/to/TravelBuddy
python pc_processing_service.py --host 0.0.0.0 --port 8001
```

### Issue: Processing is slow

**Check model download:**
Models download on first use. Check:
```bash
# On PC
ls -la models/  # or ~/.cache/huggingface/
```

First run downloads ~500MB of models, which can take 5-10 minutes.

**Monitor processing:**
```bash
# Watch logs in real-time
python -m backend.jobs.nightly_processor --no-wake 2>&1 | tee processing.log
```

**Optimize batch processing:**
Edit `backend/jobs/nightly_processor.py` to use batch processing:
```python
# Instead of processing one by one, use:
results = processing_client.process_batch(texts, source_languages)
```

### Issue: Database permission errors

```bash
# Grant all permissions to travelbuddy user
sudo -u postgres psql -d travelbuddy << 'EOF'
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO travelbuddy;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO travelbuddy;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO travelbuddy;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO travelbuddy;
EOF
```

### Issue: Embeddings not generating

**Check PC processing service logs:**
```bash
# Should see model loading
INFO:     Loading embedding model: sentence-transformers/all-MiniLM-L6-v2
INFO:     Embedding model loaded
```

**Test embedding endpoint directly:**
```bash
curl -X POST http://YOUR_PC_IP:8001/embed \
  -H "Content-Type: application/json" \
  -d '{"text": "test embedding generation"}'
```

Should return 384-dimensional vector.

---

## Quick Test Script

Save this as `test_api.sh`:

```bash
#!/bin/bash
set -e

API_URL="${TRAVELBUDDY_API_URL:-http://localhost:8000}"

echo "🧪 Testing TravelBuddy API at $API_URL"
echo ""

# Health check
echo "1️⃣  Health check..."
curl -s "$API_URL/health" | jq .
echo ""

# Get locations
echo "2️⃣  Get locations..."
curl -s "$API_URL/api/locations" | jq 'length'
echo " locations found"
echo ""

# Search for Paris
echo "3️⃣  Search for Paris, France..."
curl -s "$API_URL/api/locations/search?name=Paris&country=France" | jq .
echo ""

# Get promoted tips
echo "4️⃣  Get promoted tips for Paris..."
TIPS=$(curl -s "$API_URL/api/promoted-tips?location_name=Paris&location_country=France")
echo "$TIPS" | jq 'length'
echo " promoted tips found"
echo ""

# Show top 3
echo "5️⃣  Top 3 tips:"
echo "$TIPS" | jq -r '.[0:3] | .[] | "  [\(.mention_count)x] \(.tip_text[:70])..."'
echo ""

echo "✅ All tests passed!"
```

Run it:
```bash
chmod +x test_api.sh
./test_api.sh
```

---

## Complete Test Workflow

Follow this sequence for a full end-to-end test:

```bash
# 1. Start services
# Terminal 1: Backend API
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: PC Processing (if testing locally)
python pc_processing_service.py --host 0.0.0.0 --port 8001

# 2. Populate test data
python -m backend.scripts.populate_promotion_test_data --clear

# 3. Process tips
time python -m backend.jobs.nightly_processor --no-wake

# 4. Test API endpoints
./test_api.sh

# 5. Test Kivy app
python main.py

# 6. Verify results in database
psql -U travelbuddy -d travelbuddy -c "
SELECT
  l.name, l.country,
  COUNT(DISTINCT t.id) as tips,
  COUNT(DISTINCT tp.id) as promoted
FROM locations l
LEFT JOIN tips t ON t.location_id = l.id
LEFT JOIN tip_promotions tp ON tp.location_id = l.id
GROUP BY l.id, l.name, l.country
ORDER BY tips DESC;
"
```

That's it! Your API should now be fully tested and operational. 🎉
