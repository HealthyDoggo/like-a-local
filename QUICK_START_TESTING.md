# Quick Start Testing Guide

Get your API up and running in 5 minutes.

## Prerequisites

- PostgreSQL running with `travelbuddy` database created
- Python virtual environment activated
- Backend dependencies installed

## 🚀 Quick Start (Local Testing)

### 1. Start Backend API (Terminal 1)

```bash
cd /path/to/TravelBuddy
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Keep this running. You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Start PC Processing Service (Terminal 2)

```bash
cd /path/to/TravelBuddy
python pc_processing_service.py --host 0.0.0.0 --port 8001
```

Keep this running. First run will download models (~500MB, takes 5-10 min).

### 3. Populate Test Data (Terminal 3)

```bash
cd /path/to/TravelBuddy

# Clear existing and add test data
python -m backend.scripts.populate_promotion_test_data --clear
```

You should see:
```
✅ Successfully created 50 tips
   Locations: 5
```

### 4. Process Tips (Generate Embeddings + Promote)

```bash
# Process all pending tips
python -m backend.jobs.nightly_processor --no-wake
```

Wait 2-5 minutes. You should see:
```
INFO - Processing complete: {'processed': 50, 'translated': 3, 'embedded': 50, 'errors': 0}
INFO - Promoted 12 tips
```

### 5. Test API

```bash
# Quick test
./test_api.sh

# Or manual test
curl "http://localhost:8000/api/promoted-tips?location_name=Paris&location_country=France" | jq
```

Expected: List of tips with mention counts.

### 6. Test Kivy App

```bash
# Make sure API URL is set
echo "TRAVELBUDDY_API_URL=http://localhost:8000" > .env

# Run app
python main.py
```

In the app:
1. Go to Travel screen (✈️)
2. Select "France" → "Paris"
3. Click "Search"
4. See promoted tips with mention counts!

---

## 🔥 Super Quick Test (One-Liner)

If everything is already set up:

```bash
# Stop any existing services first, then:
(uvicorn backend.main:app --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &) && \
(python pc_processing_service.py --host 0.0.0.0 --port 8001 > /dev/null 2>&1 &) && \
sleep 5 && \
python -m backend.scripts.populate_promotion_test_data --clear && \
python -m backend.jobs.nightly_processor --no-wake && \
./test_api.sh
```

---

## 🧪 Test Different Scenarios

### Test With Translation

```bash
# These tips are in French, Spanish, Japanese
curl -X POST http://localhost:8000/api/tips \
  -H "Content-Type: application/json" \
  -d '{
    "tip_text": "Évitez les restaurants près de la Tour Eiffel - trop chers!",
    "location_name": "Paris",
    "location_country": "France"
  }'

# Process it
python -m backend.jobs.nightly_processor --no-wake

# Check if it got grouped with similar English tips
curl "http://localhost:8000/api/promoted-tips?location_name=Paris&location_country=France" | jq
```

### Test Wake-on-LAN (If PC is Remote)

```bash
# First, configure in backend/.env:
# PC_MAC_ADDRESS=XX:XX:XX:XX:XX:XX
# PC_IP_ADDRESS=192.168.1.100

# Put PC to sleep, then:
python -c "from backend.utils.wol import get_wol; wol = get_wol(); print('Waking PC...'); wol.wake()"

# Wait 30 seconds
sleep 30

# Check if PC is awake
curl http://192.168.1.100:8001/health
```

### Test Promotion Thresholds

```bash
# Edit backend/services/promotion.py:
# Change MIN_MENTIONS = 3 to MIN_MENTIONS = 2
# Or SIMILARITY_THRESHOLD = 0.85 to 0.75

# Re-run promotion
curl -X POST http://localhost:8000/api/jobs/promote

# Check results
curl "http://localhost:8000/api/promoted-tips?location_name=Paris&location_country=France" | jq 'length'
```

---

## 📊 Verify Everything Works

### Check Database

```bash
psql -U travelbuddy -d travelbuddy << 'EOF'
-- Tips summary
SELECT status, COUNT(*) FROM tips GROUP BY status;

-- Promotions by location
SELECT
  l.name,
  l.country,
  tp.mention_count,
  LEFT(tp.tip_text, 60) as tip
FROM tip_promotions tp
JOIN locations l ON l.id = tp.location_id
ORDER BY tp.mention_count DESC
LIMIT 10;
EOF
```

Expected:
```
 status    | count
-----------+-------
 processed |    50

    name    | country | mention_count |                            tip
------------+---------+---------------+------------------------------------------------------------
 Paris      | France  |             5 | Avoid the overpriced restaurants right next to the Eiffel
 Paris      | France  |             4 | Watch out for pickpockets on the metro, especially during
 Tokyo      | Japan   |             4 | Get a Suica or Pasmo card for trains - makes everything
```

### Check API Endpoints

```bash
# All core endpoints
echo "Testing endpoints..."
curl -s http://localhost:8000/health && echo " ✓ Health"
curl -s http://localhost:8000/api/locations | jq 'length' && echo " ✓ Locations"
curl -s "http://localhost:8000/api/tips?limit=5" | jq 'length' && echo " ✓ Tips"
curl -s "http://localhost:8000/api/promoted-tips?location_name=Paris&location_country=France" | jq 'length' && echo " ✓ Promoted Tips"
```

---

## 🐛 Common Issues

### "Could not connect to API"
- Check API is running: `curl http://localhost:8000/health`
- Check port isn't blocked: `sudo lsof -i :8000`

### "PC processing service is not available"
- Check service is running: `curl http://localhost:8001/health`
- Check firewall: `sudo ufw allow 8001`

### "No promoted tips found"
- Check tips are processed: `psql -U travelbuddy -d travelbuddy -c "SELECT status, COUNT(*) FROM tips GROUP BY status;"`
- Run promotion: `curl -X POST http://localhost:8000/api/jobs/promote`

### Models downloading slowly
- First run downloads ~500MB
- Check download progress in PC processing service logs
- Models cached in `./models/` or `~/.cache/huggingface/`

---

## 🎯 Success Criteria

You know it's working when:

- ✅ Backend API responds to `/health`
- ✅ PC processing service responds to `/health`
- ✅ Test data creates 50 tips across 5 locations
- ✅ Processing job processes all 50 tips
- ✅ Promotion job creates 10+ promoted tips
- ✅ API returns promoted tips for Paris (5+ tips)
- ✅ Kivy app displays tips with mention counts

---

## 📚 Next Steps

Once everything works:

1. **Deploy to Raspberry Pi** - Follow `BACKEND_NEXT_STEPS.md`
2. **Set up cron job** - Run nightly processing automatically
3. **Add more test data** - Create tips for your favorite cities
4. **Customize thresholds** - Adjust `MIN_MENTIONS` and `SIMILARITY_THRESHOLD`
5. **Monitor performance** - Track processing times and optimize

---

## 💡 Tips

- **Development**: Use `--reload` flag for auto-restart on code changes
- **Production**: Remove `--reload` and use systemd services
- **Debugging**: Check logs in real-time with `tail -f processing.log`
- **Performance**: First run is slow (model download), subsequent runs are fast
- **Testing**: Use `--clear` flag to start fresh each time

Happy testing! 🚀
