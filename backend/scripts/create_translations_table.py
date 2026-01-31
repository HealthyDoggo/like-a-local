"""Migration script to create tip_translations table"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import engine
from sqlalchemy import text


def run_migration():
    """Create tip_translations table and indexes"""
    print("Creating tip_translations table...")

    with engine.connect() as conn:
        # Create table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS tip_translations (
                id SERIAL PRIMARY KEY,
                tip_id INTEGER NOT NULL REFERENCES tips(id) ON DELETE CASCADE,
                language_code VARCHAR(10) NOT NULL,
                translated_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                UNIQUE(tip_id, language_code)
            );
        """))

        # Create indexes
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_translation_tip_lang
            ON tip_translations(tip_id, language_code);
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_translation_language
            ON tip_translations(language_code);
        """))

        conn.commit()
        print("✓ tip_translations table created successfully")


if __name__ == "__main__":
    run_migration()
