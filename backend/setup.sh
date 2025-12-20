#!/bin/bash
# Setup script for TravelBuddy backend

set -e

echo "Setting up TravelBuddy backend..."

# Check if virtual environment exists
if [ ! -d "../venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv ../venv
fi

# Activate virtual environment
source ../venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env with your configuration"
fi

# Create models directory
mkdir -p models

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your database and PC configuration"
echo "2. Set up PostgreSQL database:"
echo "   createdb travelbuddy"
echo "   psql -d travelbuddy -f database/schema.sql"
echo "3. Run the API server:"
echo "   python -m backend.main"
echo "   or"
echo "   uvicorn backend.main:app --host 0.0.0.0 --port 8000"

