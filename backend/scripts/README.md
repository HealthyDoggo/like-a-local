# TravelBuddy Database Seeding Scripts

This directory contains scripts for populating the database with test data.

## Scripts

### `seed_comprehensive_data.py`

**Comprehensive seeding script** that generates realistic, diverse travel tips across multiple cities and countries worldwide.

#### Features

- **40+ countries** with major cities
- **150+ cities** globally
- **10 tip categories** covering all aspects of travel:
  - Food & Dining
  - Getting Around
  - Culture & Etiquette
  - Safety & Health
  - Money & Budget
  - Sightseeing
  - Accommodation
  - Shopping
  - Language
  - Weather & Seasons
- **City-specific tips** for major destinations (Tokyo, Paris, Barcelona, London, etc.)
- **Realistic content** based on actual travel advice
- **Configurable** generation options

#### Usage

**Basic usage** (seed all countries and cities):
```bash
cd backend
python scripts/seed_comprehensive_data.py
```

**Limit to specific countries** (e.g., first 10 countries):
```bash
python scripts/seed_comprehensive_data.py --countries 10
```

**Limit cities per country** (e.g., 3 cities per country):
```bash
python scripts/seed_comprehensive_data.py --cities 3
```

**Adjust tips per category** (default is 3):
```bash
python scripts/seed_comprehensive_data.py --tips-per-category 5
```

**Clear existing data** before seeding:
```bash
python scripts/seed_comprehensive_data.py --clear
```

**Combine options** for precise control:
```bash
# Seed first 5 countries, max 2 cities each, 4 tips per category
python scripts/seed_comprehensive_data.py --countries 5 --cities 2 --tips-per-category 4
```

#### Example Output

```
🌟 TravelBuddy Comprehensive Data Seeder 🌟

📂 Loading cities data...
🌍 Processing 40 countries...

📍 Japan (7 cities)
   ✓ Tokyo: 38 tips
   ✓ Osaka: 30 tips
   ✓ Kyoto: 30 tips
   ...

============================================================
✅ Seeding complete!
   📍 Locations created: 150
   💡 Tips created: 4,500
   📊 Categories: 10
============================================================
```

#### Generated Data

For each city, the script generates:
- **3-5 tips per category** (configurable)
- **City-specific local tips** for major destinations
- **Realistic content** that mirrors actual travel advice
- **Proper categorization** for easy filtering

### `populate_test_data.py`

**Simple seeding script** with multilingual tips for testing translation features.

#### Features

- Tips in **12+ languages**
- Focused on major cities
- Good for testing translation functionality

#### Usage

```bash
# Add all test tips
python scripts/populate_test_data.py

# Add specific number of tips
python scripts/populate_test_data.py -n 10

# Clear existing data first
python scripts/populate_test_data.py --clear
```

## Countries & Cities Data

Location data is stored in `/backend/data/cities.json` and includes:

- **40+ countries** worldwide
- **150+ major cities**
- **Latitude/longitude** coordinates for each city
- **Country codes** (ISO 3166-1 alpha-2)

### Adding New Cities

Edit `backend/data/cities.json`:

```json
{
  "countries": [
    {
      "name": "Country Name",
      "code": "CC",
      "cities": [
        {
          "name": "City Name",
          "latitude": 00.0000,
          "longitude": 00.0000
        }
      ]
    }
  ]
}
```

### API Endpoint

The countries/cities data is available via the API:

```
GET /api/locations/countries-cities
```

Returns:
```json
{
  "countries": [
    {
      "name": "Japan",
      "code": "JP",
      "cities": [
        {
          "name": "Tokyo",
          "latitude": 35.6762,
          "longitude": 139.6503
        }
      ]
    }
  ]
}
```

## Database Schema

The seeding scripts create data in these tables:

### `locations`
- `id`: Primary key
- `name`: City name
- `country`: Country name
- `latitude`: City coordinates (optional)
- `longitude`: City coordinates (optional)
- `created_at`: Timestamp

### `tips`
- `id`: Primary key
- `tip_text`: The tip content
- `location_id`: Foreign key to locations
- `original_language`: Language code (e.g., "en", "es")
- `status`: "pending" or "processed"
- `submitted_at`: Timestamp
- `processed_at`: Timestamp (optional)

## Tips for Development

### Quick Start
For quick development testing with manageable data:
```bash
python scripts/seed_comprehensive_data.py --countries 5 --cities 2 --tips-per-category 2
```

This creates ~100-200 tips across 10 cities in 5 countries.

### Full Dataset
For comprehensive testing with production-like data:
```bash
python scripts/seed_comprehensive_data.py --clear
```

This creates thousands of tips across 150+ cities worldwide.

### Reset Database
To start fresh:
```bash
python scripts/seed_comprehensive_data.py --clear --countries 0
```

This clears all tips and locations without adding new data.

## Processing Tips

After seeding, tips need to be processed (embedded and clustered) for the promotion system:

```bash
# Process pending tips
python -m backend.jobs.nightly_processor
```

This will:
1. Generate embeddings for all tips
2. Cluster similar tips
3. Promote frequently mentioned tips to `tip_promotions` table

## Customization

### Adding New Tip Categories

Edit `TIP_TEMPLATES` in `seed_comprehensive_data.py`:

```python
TIP_TEMPLATES = {
    "Your New Category": [
        "Tip template 1",
        "Tip template 2 for {city}",
        "Tip template 3",
    ],
    # ... other categories
}
```

### Adding City-Specific Tips

Edit `CITY_SPECIFIC_TIPS` in `seed_comprehensive_data.py`:

```python
CITY_SPECIFIC_TIPS = {
    "New City": [
        "Specific local tip 1",
        "Specific local tip 2",
        "Specific local tip 3",
    ],
}
```

## Troubleshooting

### "No module named 'backend'"
Make sure you're running from the correct directory:
```bash
cd /path/to/TravelBuddy
python backend/scripts/seed_comprehensive_data.py
```

### Database connection errors
Check your `.env` file has correct database credentials:
```
DATABASE_URL=postgresql://user:password@localhost:5432/travelbuddy
```

### "Cities data file not found"
Ensure `backend/data/cities.json` exists in your repository.
