# Database Scripts

## Scripts

### `seed_comprehensive_data.py`
Seeds realistic travel tips across 40+ countries, 150+ cities, and 10 categories.

```bash
# Clear data and seed everything
python scripts/seed_comprehensive_data.py --clear

# Seed subset (5 countries, 2 cities each, 2 tips/category)
python scripts/seed_comprehensive_data.py --countries 5 --cities 2 --tips-per-category 2

# Just clear data (no seeding)
python scripts/seed_comprehensive_data.py --clear --countries 0
```

### `populate_test_data.py`
Seeds multilingual tips for translation testing.

```bash
python scripts/populate_test_data.py --clear
```

### `recluster_tips.py`
Reclusters existing tips with different embedding thresholds.

```bash
# Test different thresholds
python scripts/recluster_tips.py --threshold 0.8
python scripts/recluster_tips.py --threshold 0.85
python scripts/recluster_tips.py --threshold 0.9
```

### `show_clusters.py`
Displays tip clusters in JSON format.

```bash
# Show all promoted tips
python scripts/show_clusters.py --pretty

# Show all tips in each cluster (recalculates similarity)
python scripts/show_clusters.py --show-all-tips --pretty

# Filter by location
python scripts/show_clusters.py --location Tokyo --show-all-tips --pretty

# Filter by minimum mentions
python scripts/show_clusters.py --min-mentions 5 --pretty
```

### `setup_database.sh`
Creates database schema and tables.

```bash
./scripts/setup_database.sh
```

### `populate_promotion_test_data.py`
Seeds data specifically for testing the promotion system.

```bash
python scripts/populate_promotion_test_data.py
```

### `create_translations_table.py`
Creates the translations table in the database.

```bash
python scripts/create_translations_table.py
```

### `add_category_support.py`
Migration script to add category support to the database schema.
Adds category fields to tips and tip_promotions tables, and creates the categories table.

```bash
python scripts/add_category_support.py
```

### `init_categories.py`
Initializes the categories table with 9 predefined categories and generates embeddings for their descriptions.
Run this after `add_category_support.py` to populate the categories.

```bash
python scripts/init_categories.py
```

**Categories created:**
- everyday-etiquette - Social norms, greetings, gestures, dress codes
- food-dining - Restaurant etiquette, tipping, meal timing
- getting-around - Transportation, navigation, travel
- public-spaces - Parks, museums, religious sites
- social-interactions - Making friends, conversations, relationships
- cultural-customs - Holidays, festivals, traditions
- locals-appreciate - Respectful behaviors, cultural appreciation
- misunderstandings - Tourist mistakes, cultural misinterpretations
- helpful-tips - Practical advice, safety, local secrets

### `classify_existing_tips.py`
Classifies all existing processed tips into categories using vector similarity.
Run this after initializing categories to classify your existing tip data.

```bash
# Classify all unclassified tips
python scripts/classify_existing_tips.py

# The script processes tips in batches of 100 by default
```

**Note:** Tips are classified using cosine similarity with a 0.65 confidence threshold.
Tips below the threshold remain unclassified and will be assigned a category during future processing.

## Quick Workflow

**Initial setup with category support:**
```bash
cd backend
python scripts/add_category_support.py
python scripts/init_categories.py
python scripts/seed_comprehensive_data.py --clear
python -m backend.jobs.nightly_processor
python scripts/classify_existing_tips.py
```

**Clear data, seed, and test embedding thresholds:**
```bash
cd backend
python scripts/seed_comprehensive_data.py --clear
python -m backend.jobs.nightly_processor
python scripts/recluster_tips.py --threshold 0.85
```

**Classify existing tips after enabling categories:**
```bash
cd backend
python scripts/add_category_support.py
python scripts/init_categories.py
python scripts/classify_existing_tips.py
```
