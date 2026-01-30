# Tip Clustering Configuration

This document explains how to configure and re-cluster tips in the TravelBuddy database.

## Overview

TravelBuddy clusters similar tips together using cosine similarity of their embeddings. Tips that are similar enough (above the similarity threshold) and mentioned frequently enough (above the minimum mentions) are promoted and displayed to users.

## Configuration

Two main parameters control the clustering behavior:

### 1. Similarity Threshold (`SIMILARITY_THRESHOLD`)

- **Range**: 0.0 to 1.0
- **Default**: 0.85
- **Description**: Cosine similarity threshold for considering two tips as part of the same cluster
- **Higher values** (e.g., 0.90-0.95): More strict clustering, tips must be very similar
  - Results in more clusters with fewer tips each
  - Fewer promoted tips overall
  - Good for ensuring only nearly-identical tips are grouped
- **Lower values** (e.g., 0.75-0.80): More lenient clustering, somewhat related tips will cluster
  - Results in fewer, larger clusters
  - More promoted tips overall
  - Good for finding broader themes in tips

### 2. Minimum Mentions (`MIN_MENTIONS`)

- **Range**: 1 or higher (integer)
- **Default**: 3
- **Description**: Minimum number of tips in a cluster required for it to be promoted
- **Higher values** (e.g., 4-5): Only show the most commonly mentioned tips
  - Fewer promoted tips
  - Higher confidence that these are genuine patterns
- **Lower values** (e.g., 2): Show tips even if only mentioned a few times
  - More promoted tips
  - May show less validated patterns

## Setting Configuration

### Option 1: Environment Variables (Permanent)

Add to your `.env` file:

```bash
# Stricter clustering (only very similar tips)
SIMILARITY_THRESHOLD=0.90
MIN_MENTIONS=3

# Or more lenient clustering (broader themes)
SIMILARITY_THRESHOLD=0.75
MIN_MENTIONS=2
```

Then restart your API server for changes to take effect.

### Option 2: Command Line (Temporary)

Use the re-clustering script with custom parameters (doesn't modify `.env`):

```bash
# Re-cluster with custom threshold
python3.11 -m backend.scripts.recluster_tips --threshold 0.90

# Re-cluster with custom minimum mentions
python3.11 -m backend.scripts.recluster_tips --min-mentions 2

# Both custom settings
python3.11 -m backend.scripts.recluster_tips --threshold 0.90 --min-mentions 2
```

## Re-clustering Tips

When you change the configuration, existing promotions won't automatically update. You need to re-cluster.

### Basic Usage

Re-cluster using current config settings:

```bash
python3.11 -m backend.scripts.recluster_tips
```

### Preview Changes (Dry Run)

See what would happen without making changes:

```bash
python3.11 -m backend.scripts.recluster_tips --dry-run
```

With custom settings:

```bash
python3.11 -m backend.scripts.recluster_tips --dry-run --threshold 0.90 --min-mentions 2
```

### Common Scenarios

**Finding the right threshold:**

```bash
# Try different thresholds and compare results
python3.11 -m backend.scripts.recluster_tips --dry-run --threshold 0.95
python3.11 -m backend.scripts.recluster_tips --dry-run --threshold 0.85
python3.11 -m backend.scripts.recluster_tips --dry-run --threshold 0.75
```

**You have too few promoted tips:**

```bash
# Lower threshold or minimum mentions
python3.11 -m backend.scripts.recluster_tips --threshold 0.75 --min-mentions 2
```

**You have too many promoted tips or they seem unrelated:**

```bash
# Raise threshold or minimum mentions
python3.11 -m backend.scripts.recluster_tips --threshold 0.90 --min-mentions 4
```

## What the Re-clustering Script Does

1. **Shows current statistics**: Tips, promotions, locations
2. **Clears existing promotions**: Removes all entries from `tip_promotions` table
3. **Re-runs clustering**: Analyzes all processed tips using the specified threshold
4. **Creates new promotions**: Saves clusters that meet the minimum mentions requirement
5. **Shows results**: Displays new promotion statistics and top promoted tips

## Understanding the Output

After re-clustering, you'll see:

```
📊 Current Database Statistics:
   Total tips: 150
   Processed tips: 150
   Pending tips: 0
   Current promotions: 12
   Locations: 5

🧹 Clearing 12 existing promotions...
   ✓ Cleared all promotions

🔄 Running clustering with threshold=0.85, min_mentions=3...

✅ Clustering complete!
   New promotions created: 15

📊 New Promotion Statistics:
   • Paris, France: 5 promoted tips
   • Tokyo, Japan: 4 promoted tips
   • Barcelona, Spain: 3 promoted tips
   • New York, United States: 2 promoted tips
   • London, United Kingdom: 1 promoted tips

🏆 Top 5 Promoted Tips (by mention count):
   • [5 mentions] Paris: Avoid the overpriced restaurants right next to the Eiffel...
   • [4 mentions] Tokyo: Get a Suica or Pasmo card for trains - makes everything...
   • [4 mentions] Paris: Watch out for pickpockets on the metro, especially dur...
   • [3 mentions] Barcelona: Restaurants don't open for dinner until 9 PM - eat...
   • [3 mentions] Paris: Always say bonjour when entering shops - it's conside...
```

## Integration with Nightly Processor

The nightly processor (`backend/jobs/nightly_processor.py`) automatically:

1. Processes pending tips (translation + embeddings)
2. Runs promotion logic to update clusters

The nightly processor uses the config settings from `.env`, so make sure to set them there for automatic processing.

## Technical Details

- **Clustering Algorithm**: Greedy clustering based on cosine similarity
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)
- **Similarity Metric**: Cosine similarity (dot product of normalized vectors)
- **Cluster Representative**: The first tip encountered in each cluster
- **Database Tables**:
  - `tips`: Raw tips submitted by users
  - `embeddings`: Vector embeddings for each tip
  - `tip_promotions`: Clustered tips promoted to users

## Tips for Tuning

1. **Start with dry runs** to see the impact of different settings
2. **Look at actual tip text** to judge if clusters make sense
3. **Consider your data volume**:
   - Small dataset (< 100 tips): Lower threshold (0.75-0.80), lower min_mentions (2)
   - Large dataset (> 500 tips): Higher threshold (0.85-0.90), higher min_mentions (3-4)
4. **Balance quality vs quantity**:
   - Quality-focused: Higher threshold, higher min_mentions
   - Coverage-focused: Lower threshold, lower min_mentions
5. **Monitor promoted tips** in the app to ensure they make sense to users
