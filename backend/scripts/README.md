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

## Quick Workflow

**Clear data, seed, and test embedding thresholds:**
```bash
cd backend
python scripts/seed_comprehensive_data.py --clear
python -m backend.jobs.nightly_processor
python scripts/recluster_tips.py --threshold 0.85
```
