"""Migration script to add category support to the database"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import engine
from sqlalchemy import text

def run_migration():
    """Add category support: categories table, category fields to tips and tip_promotions"""
    print("Adding category support to database...")

    with engine.connect() as conn:
        # Create categories table
        print("1. Creating categories table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS categories (
                id VARCHAR(50) PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                embedding REAL[] NOT NULL,
                icon_name VARCHAR(50),
                color VARCHAR(20),
                display_order INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))

        # Create index on display_order
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_category_order
            ON categories(display_order);
        """))

        # Add category fields to tips table
        print("2. Adding category fields to tips table...")
        conn.execute(text("""
            ALTER TABLE tips
            ADD COLUMN IF NOT EXISTS category_id VARCHAR(50),
            ADD COLUMN IF NOT EXISTS category_confidence DECIMAL(4, 3),
            ADD COLUMN IF NOT EXISTS category_assigned_at TIMESTAMP,
            ADD COLUMN IF NOT EXISTS category_manual BOOLEAN DEFAULT FALSE;
        """))

        # Create indexes for tips category fields
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_tip_category
            ON tips(category_id);
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_tip_location_category
            ON tips(location_id, category_id);
        """))

        # Add category_id to tip_promotions table
        print("3. Adding category_id to tip_promotions table...")
        conn.execute(text("""
            ALTER TABLE tip_promotions
            ADD COLUMN IF NOT EXISTS category_id VARCHAR(50);
        """))

        # Create index for tip_promotions category
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_promotion_category
            ON tip_promotions(category_id);
        """))

        conn.commit()
        print("✓ Category support added successfully")


if __name__ == "__main__":
    run_migration()
