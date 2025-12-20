# TravelBuddy Architecture

## Overview

TravelBuddy is a Kivy-based mobile-style application that helps travelers discover local insights about destinations they want to visit.

## Application Flow

```
┌─────────────────┐
│  SignupScreen   │ ← User enters profile information
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│DestinationsScreen│ ← Browse available destinations
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  DetailsScreen  │ ← View local tips for selected destination
└─────────────────┘
```

## Screen Descriptions

### 1. SignupScreen (`main.py`)

**Purpose**: Collect user information during initial setup

**Data Collected**:
- User's name
- Hometown (where they're from)
- Current location (where they live now)

**Data Storage**: Saves to `user_data.json`

**Navigation**: 
- On submit → DestinationsScreen
- Can return here via "Edit Profile" button

### 2. DestinationsScreen (`main.py`)

**Purpose**: Display all available travel destinations

**Features**:
- Scrollable list of destination buttons
- Edit Profile button to update user info
- Dynamically loads from `data/destinations.json`
- Creates default data if file doesn't exist

**Navigation**:
- Click destination → DetailsScreen
- Edit Profile → SignupScreen

### 3. DetailsScreen (`main.py`)

**Purpose**: Show detailed local tips for selected destination

**Features**:
- Displays destination name and country
- Lists local tips with emoji bullets
- Back button to return to destinations

**Navigation**:
- Back button → DestinationsScreen

## Data Structure

### User Data (`user_data.json`)

```json
{
  "name": "John Doe",
  "hometown": "San Francisco, USA",
  "current_location": "New York, USA"
}
```

### Destinations Data (`data/destinations.json`)

```json
{
  "destination_id": {
    "name": "City Name",
    "country": "Country Name",
    "tips": [
      "Tip 1",
      "Tip 2",
      "Tip 3"
    ]
  }
}
```

## Key Technologies

- **Kivy**: Cross-platform Python framework for GUI applications
- **ScreenManager**: Handles navigation between different screens
- **JSON**: Simple data persistence

## Future Enhancements

### Phase 2 - Enhanced Features
- [ ] Add destination images
- [ ] Search/filter destinations
- [ ] Categories (by continent, climate, etc.)
- [ ] User ratings for tips
- [ ] Save favorite destinations

### Phase 3 - Social Features
- [ ] User-generated tips
- [ ] Connect with other travelers
- [ ] Trip planning features
- [ ] Budget estimator

### Phase 4 - Advanced Features
- [ ] Interactive map view
- [ ] Integration with travel APIs
- [ ] Weather information
- [ ] Currency converter
- [ ] Language phrase guide

## Development Guidelines

### Adding New Destinations

1. Edit `data/destinations.json`
2. Follow the existing JSON structure
3. Add 3-5 actionable tips per destination
4. Focus on insights locals would share, not generic tourist info

### Code Style

- Follow PEP 8 for Python code
- Add docstrings to all classes and methods
- Keep screen logic self-contained
- Use meaningful variable names

### Testing

Run the app in development mode:
```bash
python main.py
```

Window size is set to 400x650 for mobile-like experience during development.

## File Organization

```
TravelBuddy/
├── main.py                 # Main application and all screens
├── data/
│   └── destinations.json   # Destination data (auto-generated)
├── user_data.json         # User profile (created on signup)
├── requirements.txt       # Python dependencies
├── setup.sh              # Setup script
├── README.md             # User-facing documentation
├── ARCHITECTURE.md       # This file
└── .gitignore           # Git ignore rules
```

## Contributing

When adding features:
1. Create a new branch
2. Test thoroughly
3. Update documentation
4. Submit clear commit messages




