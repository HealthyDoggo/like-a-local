# TravelBuddy

A Kivy-based travel companion app that helps users discover local insights about their dream destinations.

## Features

- **Personalized Signup**: Users share where they're from and where they currently live
- **Destination Browser**: Browse and select places you want to travel
- **Local Insights**: See tips and advice from locals about each destination

## Setup

### Prerequisites

- Python 3.8 or higher
- pip

### Installation

1. Create and activate a virtual environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

### Running the App

```bash
python main.py
```

## Project Structure

```
TravelBuddy/
├── main.py              # Main application entry point
├── screens/             # Screen definitions
│   ├── signup.py        # Signup/survey screen
│   ├── destinations.py  # Destination browser
│   └── details.py       # Destination details screen
├── data/                # Data storage
│   └── destinations.json
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Development

### Adding New Destinations

Edit `data/destinations.json` to add new destinations with local tips.

### Adding New Features

The app uses Kivy's ScreenManager for navigation between screens. Add new screens in the `screens/` directory.

## License

MIT




