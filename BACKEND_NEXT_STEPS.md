# Backend System - Next Steps

## Implementation Status: ✅ COMPLETE

All core backend components have been implemented:

- ✅ Backend API structure with FastAPI
- ✅ Database models and schema (PostgreSQL)
- ✅ REST API endpoints (tips, locations, jobs)
- ✅ NLLB translation service
- ✅ Embedding service (miniLM-v6)
- ✅ Wake-on-LAN integration
- ✅ Nightly processing job
- ✅ App integration with API client
- ✅ Tip promotion logic

## Next Steps

### 1. Deployment Setup (Raspberry Pi)

#### 1.1 Database Setup
```bash
# On Raspberry Pi
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Create database and user (as postgres user)
sudo -u postgres psql
CREATE DATABASE travelbuddy;
CREATE USER travelbuddy WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE travelbuddy TO travelbuddy;
\q

# Run schema - Option 1: As postgres user (recommended)
sudo -u postgres psql -d travelbuddy -f backend/database/schema.sql

# OR Option 2: With password authentication
# First, edit pg_hba.conf to allow password auth:
# sudo nano /etc/postgresql/*/main/pg_hba.conf
# Change line: local   all             all                                     peer
# To:          local   all             all                                     md5
# Then restart: sudo systemctl restart postgresql
# Then run: PGPASSWORD='your_password' psql -U travelbuddy -d travelbuddy -h localhost -f backend/database/schema.sql

# OR Option 3: Connect as postgres and run SQL directly
sudo -u postgres psql -d travelbuddy << EOF
\i backend/database/schema.sql
EOF
```

#### 1.2 Python Environment
```bash
# On Raspberry Pi
cd /path/to/TravelBuddy
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

#### 1.3 Configuration
```bash
# Copy and edit environment file
cp backend/.env.example backend/.env
nano backend/.env

# Update with your settings:
# - DATABASE_URL (PostgreSQL connection)
# - PC_MAC_ADDRESS (your PC's MAC address)
# - PC_IP_ADDRESS (your PC's IP address)
# - Other settings as needed
```

#### 1.4 Test API Server
```bash
# Start the API server
cd backend
python -m backend.main

# Or with uvicorn
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### 2. PC Setup (for Processing)

#### 2.1 Enable Wake-on-LAN

**Find Your MAC Address:**
```bash
# Windows (PowerShell)
Get-NetAdapter | Select-Object Name, MacAddress

# Windows (Command Prompt)
ipconfig /all
# Look for "Physical Address" under your network adapter

# Linux/Mac
ip addr show
# or
ifconfig
# Look for "ether" or "HWaddr" - this is your MAC address
```

**Find Your IP Address:**
```bash
# Windows
ipconfig

# Linux/Mac
ip addr show
# or
hostname -I
```

**WOL Port Configuration:**

Wake-on-LAN uses **UDP port 9** by default (sometimes port 7). This is usually handled automatically, but here's how to check/configure:

**Windows:**
1. Open Device Manager
2. Expand "Network adapters"
3. Right-click your network adapter → Properties
4. Go to "Power Management" tab
5. Check "Allow this device to wake the computer"
6. Check "Only allow a magic packet to wake the computer" (recommended)
7. Go to "Advanced" tab
8. Look for "Wake on Magic Packet" or "Wake on LAN" → Enable it
9. Port is typically handled by the network adapter driver (default: 9)

**Linux (systemd):**
```bash
# Check if WOL is enabled
sudo ethtool eth0  # or your interface name (use ip addr to find it)
# Look for "Wake-on: g" (g = magic packet)

# Enable WOL
sudo ethtool -s eth0 wol g

# Make it persistent (create systemd service or add to /etc/network/interfaces)
# For systemd-networkd, create:
sudo nano /etc/systemd/network/50-wired.network
# Add:
[Link]
WakeOnLan=magic
```

**Mac:**
1. System Preferences → Energy Saver
2. Check "Wake for network access"
3. Port is handled automatically (default: 9)

**Testing WOL Port:**
```bash
# From Raspberry Pi, test if port is open (optional - WOL works even if port appears closed)
nc -u -v <PC_IP> 9

# Or use wakeonlan tool to test
wakeonlan <MAC_ADDRESS>
```

**Important Notes:**
- WOL port (9) is usually **not** a listening port - it's a destination port for the magic packet
- The PC doesn't need to be "listening" on port 9 - the network adapter handles it at hardware level
- Most routers/switches forward WOL packets automatically
- If WOL doesn't work, check:
  - BIOS/UEFI has WOL enabled
  - Network adapter has WOL enabled in OS
  - Router allows WOL packets (some block them)
  - PC is in sleep/hibernate, not fully shut down (unless "Wake on Power" is enabled)

#### 2.2 Install Dependencies (if processing runs on PC)
```bash
# On PC
pip install transformers sentence-transformers torch
```

#### 2.3 Network Configuration
- Ensure PC and Pi are on same network (or routable)
- Test wake-on-LAN from Pi to PC
- Configure firewall if needed

### 3. Scheduling Nightly Job

#### 3.1 Set up Cron Job
```bash
# Edit crontab
crontab -e

# Add line (runs at 2 AM daily)
0 2 * * * cd /path/to/TravelBuddy && /path/to/venv/bin/python -m backend.jobs.nightly_processor --sleep-pc

# Or without sleeping PC
0 2 * * * cd /path/to/TravelBuddy && /path/to/venv/bin/python -m backend.jobs.nightly_processor
```

#### 3.2 Populate Test Data
```bash
# Populate database with test tips in various languages
python -m backend.scripts.populate_test_data

# Add only first 10 tips (for quick testing)
python -m backend.scripts.populate_test_data -n 10

# Clear existing data and repopulate (WARNING: deletes all tips!)
python -m backend.scripts.populate_test_data --clear
```

#### 3.3 Test Manual Processing
```bash
# Test the processing job manually
python -m backend.jobs.nightly_processor

# Test without waking PC
python -m backend.jobs.nightly_processor --no-wake

# Test promotion only
python -m backend.jobs.nightly_processor --no-wake --no-promotion

# Time the processing (to measure performance)
time python -m backend.jobs.nightly_processor --no-wake
```

### 4. App Configuration

#### 4.1 Update API URL
```bash
# In main app directory, set environment variable or update api_client.py
export TRAVELBUDDY_API_URL=http://raspberry-pi-ip:8000

# Or edit api_client.py directly to set default URL
```

#### 4.2 Test App Connection
- Run the app and try submitting a tip
- Verify tip appears in database
- Check API logs for any errors

### 5. Testing Checklist

#### 5.1 Initial Setup
- [ ] API server starts successfully
- [ ] Database connection works
- [ ] Can submit tip via API
- [ ] Can query tips via API

#### 5.2 Test Data Population
- [ ] Run populate script: `python -m backend.scripts.populate_test_data`
- [ ] Verify tips are in database with "pending" status
- [ ] Check tips in various languages were added

#### 5.3 Processing Tests
- [ ] Wake-on-LAN successfully wakes PC (if testing with WOL)
- [ ] Nightly job processes tips correctly
- [ ] Translation works for non-English tips
- [ ] Embeddings are generated and stored
- [ ] Check processing times (use `time` command)
- [ ] Verify tips status changed to "processed"

#### 5.4 Promotion Tests
- [ ] Tip promotion logic works
- [ ] Similar tips are grouped correctly
- [ ] Promoted tips appear in tip_promotions table

#### 5.5 App Integration
- [ ] App can connect to API
- [ ] App can submit tips
- [ ] App can fetch processed tips

### 6. Production Considerations

#### 6.1 Security
- [ ] Change default database password
- [ ] Use environment variables for secrets
- [ ] Configure CORS properly (not `*` in production)
- [ ] Set up SSL/TLS for API (nginx reverse proxy)
- [ ] Secure wake-on-LAN (consider VPN)

#### 6.2 Monitoring
- [ ] Set up logging (file rotation, levels)
- [ ] Monitor API health endpoint
- [ ] Track processing job success/failure
- [ ] Monitor database size and performance

#### 6.3 Performance
- [ ] Tune PostgreSQL settings
- [ ] Consider connection pooling
- [ ] Monitor model loading times
- [ ] Optimize batch processing sizes

### 7. Future Enhancements (Optional)

- [ ] Add authentication/authorization
- [ ] Implement rate limiting
- [ ] Add API versioning
- [ ] Set up automated backups
- [ ] Add metrics/analytics
- [ ] Implement caching layer
- [ ] Add admin dashboard
- [ ] Group places by vector similarity (as mentioned in original plan)

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check PostgreSQL is running: `sudo systemctl status postgresql`
   - Verify connection string in `.env`
   - Check firewall rules

2. **Wake-on-LAN Not Working**
   - Verify MAC address is correct
   - Check PC has WOL enabled
   - Test network connectivity
   - Check router settings (some routers block WOL)

3. **Models Not Loading**
   - Check disk space (models are large)
   - Verify internet connection for first download
   - Check MODEL_CACHE_DIR path

4. **Processing Job Fails**
   - Check logs for specific errors
   - Verify PC is accessible
   - Check database has pending tips
   - Verify model files are downloaded

## File Locations

- Configuration: `backend/.env`
- Database Schema: `backend/database/schema.sql`
- API Server: `backend/main.py`
- Nightly Job: `backend/jobs/nightly_processor.py`
- API Client: `api_client.py` (in root)
- App Integration: `main.py` (updated)

## Development Workflow

### Option 1: Full Repo on Pi (Recommended)
Clone the entire repository on your Raspberry Pi:
```bash
# On Raspberry Pi
cd ~
git clone <your-repo-url> TravelBuddy
cd TravelBuddy
# Work in backend/ folder
```

**Pros:**
- Simple, single source of truth
- Easy to sync changes between dev machine and Pi
- Can test full integration if needed

**Cons:**
- Includes frontend code you don't need on Pi
- Slightly larger repo

### Option 2: Backend-Only Repo
Create a separate repository just for backend:
```bash
# On your dev machine
cd backend
git init
git remote add origin <backend-repo-url>
git add .
git commit -m "Initial backend commit"
git push

# On Raspberry Pi
git clone <backend-repo-url> travelbuddy-backend
cd travelbuddy-backend
```

**Pros:**
- Cleaner separation
- Smaller repo on Pi
- Can have different access controls

**Cons:**
- Need to maintain two repos
- More complex sync if frontend changes affect backend

### Option 3: Git Sparse-Checkout (Best of Both Worlds) ⭐
Clone the full repo but only checkout the `backend/` folder:
```bash
# On Raspberry Pi
cd ~
git clone --no-checkout <your-repo-url> TravelBuddy
cd TravelBuddy

# Enable sparse-checkout
git sparse-checkout init --cone
git sparse-checkout set backend/

# Now checkout only the backend folder
git checkout main  # or master, depending on your default branch

# Verify only backend is checked out
ls  # Should only show backend/ folder
```

**To add more folders later:**
```bash
git sparse-checkout set backend/ api_client.py requirements.txt
```

**To see full repo again:**
```bash
git sparse-checkout disable
git checkout .
```

**Pros:**
- Full repo access (can see all branches, history, etc.)
- Only downloads what you need (saves disk space)
- Easy to add more files/folders later
- Single source of truth
- No nested repos

**Cons:**
- Slightly more setup initially
- Need to remember sparse-checkout commands

**This is the recommended approach for Pi deployment!**

### Option 4: Git Submodule (Advanced)
Keep backend as a submodule in main repo:
```bash
# On dev machine
cd TravelBuddy
git submodule add <backend-repo-url> backend

# On Pi
git clone --recursive <your-repo-url> TravelBuddy
# Or if already cloned:
git submodule update --init --recursive
```

**Pros:**
- Single repo but modular
- Can version backend independently

**Cons:**
- More complex to manage
- Overkill for most use cases

### Recommended: Option 3 (Sparse-Checkout) or Option 1

**For Pi:** Use sparse-checkout (Option 3) - you get full repo access but only download what you need.

**For simplicity:** Use Option 1 (full repo) - easiest to understand and maintain.

### Alternative: Option 1 with Selective Sync

Use the full repo but sync only what you need:

```bash
# On Raspberry Pi - clone full repo
git clone <your-repo-url> TravelBuddy
cd TravelBuddy/backend

# Create a simple sync script (optional)
cat > sync_backend.sh << 'EOF'
#!/bin/bash
# Sync only backend changes
git pull origin main
# Restart API if using systemd
# sudo systemctl restart travelbuddy-api
EOF
chmod +x sync_backend.sh
```

**Development Workflow:**
1. Develop on your main machine
2. Test locally if possible
3. Commit and push to repo
4. On Pi: `git pull` to get latest changes
5. Restart API server if needed

### Quick Sync Alternative (rsync/scp)

If you don't want to use git on Pi, sync files directly:

```bash
# From your dev machine
rsync -avz --exclude='__pycache__' --exclude='*.pyc' \
  backend/ pi@raspberry-pi-ip:~/TravelBuddy/backend/

# Or with scp
scp -r backend/* pi@raspberry-pi-ip:~/TravelBuddy/backend/
```

**Recommendation:** Use Option 1 (full repo) - it's the simplest and most maintainable. The extra frontend files don't hurt, and you get version control on the Pi.

