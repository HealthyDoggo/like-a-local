# PC Processing Service Setup

This document explains how to set up and run the PC processing service that handles ML model processing for TravelBuddy.

## Overview

The PC processing service is a FastAPI application that runs on your PC and provides:
- Language detection (using langdetect)
- Translation (NLLB model)
- Embedding generation (miniLM-v6)

The Raspberry Pi sends HTTP requests to this service for processing tips.

## Installation

### 1. Install Dependencies

On your PC, install the required packages:

```bash
# Navigate to TravelBuddy directory
cd /path/to/TravelBuddy

# Install backend dependencies (includes ML models)
pip install -r backend/requirements.txt

# Install FastAPI and uvicorn if not already installed
pip install fastapi uvicorn
```

### 2. Configure Environment

Create a `.env` file in the TravelBuddy root directory (or use backend/.env):

```bash
# Model configuration
NLLB_MODEL_NAME=facebook/nllb-200-3.3B
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
MODEL_CACHE_DIR=./models
TARGET_LANGUAGE=eng_Latn
```

## Running the Service

### Manual Start

```bash
# From TravelBuddy root directory
python pc_processing_service.py

# Or with custom host/port
python pc_processing_service.py --host 0.0.0.0 --port 8001

# With auto-reload (for development)
python pc_processing_service.py --reload
```

The service will start on `http://0.0.0.0:8001` and be accessible from your network.

### Verify It's Running

```bash
# Test health endpoint
curl http://localhost:8001/health

# Should return: {"status":"healthy","service":"pc_processing"}
```

## Auto-Start on Boot/Wake

### Option 1: Systemd Service (Linux)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/travelbuddy-pc-processing.service
```

Add this content (adjust paths as needed):

```ini
[Unit]
Description=TravelBuddy PC Processing Service
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/TravelBuddy
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python /path/to/TravelBuddy/pc_processing_service.py --host 0.0.0.0 --port 8001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable travelbuddy-pc-processing.service
sudo systemctl start travelbuddy-pc-processing.service

# Check status
sudo systemctl status travelbuddy-pc-processing.service
```

### Option 2: Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Name: "TravelBuddy PC Processing Service"
4. Trigger: "When the computer starts" and "On workstation unlock"
5. Action: Start a program
   - Program: `C:\path\to\venv\Scripts\python.exe`
   - Arguments: `C:\path\to\TravelBuddy\pc_processing_service.py --host 0.0.0.0 --port 8001`
   - Start in: `C:\path\to\TravelBuddy`

### Option 3: Startup Script (Cross-platform)

Create a startup script that checks if service is running and starts it if not:

**Linux/Mac (`start_pc_service.sh`):**
```bash
#!/bin/bash
cd /path/to/TravelBuddy
source venv/bin/activate

# Check if service is already running
if ! curl -s http://localhost:8001/health > /dev/null; then
    echo "Starting PC processing service..."
    python pc_processing_service.py --host 0.0.0.0 --port 8001 &
    echo $! > /tmp/travelbuddy_pc_service.pid
else
    echo "PC processing service already running"
fi
```

**Windows (`start_pc_service.bat`):**
```batch
@echo off
cd C:\path\to\TravelBuddy
C:\path\to\venv\Scripts\activate.bat

REM Check if service is running
curl -s http://localhost:8001/health >nul 2>&1
if errorlevel 1 (
    echo Starting PC processing service...
    start /B python pc_processing_service.py --host 0.0.0.0 --port 8001
) else (
    echo PC processing service already running
)
```

Add this script to your startup:
- **Linux**: Add to `~/.bashrc` or `~/.profile`
- **Mac**: Add to Login Items in System Preferences
- **Windows**: Add to Startup folder or Task Scheduler

### Option 4: Wake-on-LAN Hook (Advanced)

If you want the service to start automatically when PC is woken via WOL:

**Linux:**
Create a systemd service that starts after network is up:

```ini
[Unit]
Description=TravelBuddy PC Processing Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/path/to/venv/bin/python /path/to/TravelBuddy/pc_processing_service.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Or use a network hook script:**
```bash
# /etc/network/if-up.d/travelbuddy-pc-service
#!/bin/bash
if [ "$IFACE" = "eth0" ] || [ "$IFACE" = "wlan0" ]; then
    systemctl start travelbuddy-pc-processing.service
fi
```

## Configuration on Pi

Update your Pi's `.env` file to point to the PC service:

```bash
# In backend/.env on Pi
PC_IP_ADDRESS=192.168.1.100  # Your PC's IP address
PC_PROCESSING_API_PORT=8001
# Or specify full URL:
PC_PROCESSING_API_URL=http://192.168.1.100:8001
```

## Testing

### Test from Pi

```bash
# From Pi, test the PC service
curl http://192.168.1.100:8001/health

# Test language detection
curl -X POST http://192.168.1.100:8001/detect-language \
  -H "Content-Type: application/json" \
  -d '{"text": "Hola, cómo estás?"}'

# Test translation
curl -X POST http://192.168.1.100:8001/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hola, cómo estás?", "source_language": "es"}'

# Test embedding
curl -X POST http://192.168.1.100:8001/embed \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, how are you?"}'
```

### Test Full Pipeline

```bash
# On Pi, run the nightly processor
python -m backend.jobs.nightly_processor --no-wake
```

## Troubleshooting

### Service Won't Start

1. Check if port 8001 is already in use:
   ```bash
   # Linux/Mac
   lsof -i :8001
   # Windows
   netstat -ano | findstr :8001
   ```

2. Check firewall settings - ensure port 8001 is open

3. Check logs for errors:
   ```bash
   python pc_processing_service.py
   ```

### Models Not Loading

1. Check disk space (models are large, ~3GB+ for NLLB)
2. Check internet connection (first run downloads models)
3. Verify MODEL_CACHE_DIR path is writable

### Pi Can't Connect

1. Verify PC service is running: `curl http://localhost:8001/health`
2. Check PC firewall allows port 8001
3. Verify PC_IP_ADDRESS in Pi's .env is correct
4. Test network connectivity: `ping <PC_IP_ADDRESS>`

### Performance Issues

- First request is slow (models loading)
- Consider using batch endpoint for multiple tips
- GPU acceleration helps (if available)

## API Endpoints

- `GET /` - Service info
- `GET /health` - Health check
- `POST /detect-language` - Detect language of text
- `POST /translate` - Translate text
- `POST /embed` - Generate embedding vector
- `POST /process-batch` - Process multiple texts at once

See `pc_processing_service.py` for detailed endpoint documentation.

