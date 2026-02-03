"""Migration script to convert category descriptions and embeddings to arrays"""
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import engine
from sqlalchemy import text


def migrate_categories():
    """Convert category description and embedding columns to JSON arrays"""
    print("Migrating categories to support multiple descriptions...")

    with engine.connect() as conn:
        # Check if categories table exists
        result = conn.execute(text("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = 'categories'
        """))

        if result.scalar() == 0:
            print("Categories table doesn't exist yet. No migration needed.")
            print("Run init_categories.py to create categories with the new schema.")
            return

        # Check current column types
        result = conn.execute(text("""
            SELECT data_type
            FROM information_schema.columns
            WHERE table_name = 'categories' AND column_name = 'description'
        """))

        current_type = result.scalar()

        if current_type == 'json' or current_type == 'jsonb':
            print("Categories already migrated to JSON format.")
            return

        print(f"Current description type: {current_type}")
        print("Converting to JSON format...")

        # Get existing categories
        result = conn.execute(text("SELECT id, description, embedding FROM categories"))
        existing_categories = result.fetchall()

        if not existing_categories:
            print("No existing categories found.")
            # Just alter the columns
            conn.execute(text("""
                ALTER TABLE categories
                ALTER COLUMN description TYPE JSON USING to_jsonb(ARRAY[description])
            """))
            conn.execute(text("""
                ALTER TABLE categories
                ALTER COLUMN embedding TYPE JSON USING to_jsonb(ARRAY[embedding])
            """))
            conn.commit()
            print("✓ Schema updated (no data to convert)")
            return

        print(f"Found {len(existing_categories)} categories to convert")

        # Create temporary table with new schema
        conn.execute(text("""
            CREATE TABLE categories_new (
                id VARCHAR(50) PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description JSON NOT NULL,
                embedding JSON NOT NULL,
                icon_name VARCHAR(50),
                color VARCHAR(20),
                display_order INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Copy and convert data
        for cat_id, desc, emb in existing_categories:
            # Convert single description to array
            desc_array = [desc] if isinstance(desc, str) else desc

            # Convert embedding to array of arrays (one embedding per description)
            emb_array = [emb] if isinstance(emb, list) else [[emb]]

            # Get the rest of the category data
            cat_data = conn.execute(text("""
                SELECT title, icon_name, color, display_order, created_at
                FROM categories
                WHERE id = :cat_id
            """), {"cat_id": cat_id}).fetchone()

            # Insert with proper JSON encoding
            conn.execute(text("""
                INSERT INTO categories_new (id, title, description, embedding, icon_name, color, display_order, created_at)
                VALUES (:cat_id, :title, :desc::jsonb, :emb::jsonb, :icon_name, :color, :display_order, :created_at)
            """), {
                "cat_id": cat_id,
                "title": cat_data[0],
                "desc": json.dumps(desc_array),
                "emb": json.dumps(emb_array),
                "icon_name": cat_data[1],
                "color": cat_data[2],
                "display_order": cat_data[3],
                "created_at": cat_data[4]
            })

        # Drop old table and rename new one
        conn.execute(text("DROP TABLE categories"))
        conn.execute(text("ALTER TABLE categories_new RENAME TO categories"))

        # Recreate index
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_category_order
            ON categories(display_order)
        """))

        conn.commit()
        print(f"✓ Successfully migrated {len(existing_categories)} categories")
        print("\nNote: Existing categories now have their descriptions as single-item arrays.")
        print("You may want to:")
        print("  1. View categories: python backend/scripts/edit_category.py list")
        print("  2. Edit to add more phrases: python backend/scripts/edit_category.py edit <category-id>")
        print("  3. Or reinitialize: Delete categories and run init_categories.py")


if __name__ == "__main__":
    try:
        migrate_categories()
    except Exception as e:
        print(f"Error during migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
