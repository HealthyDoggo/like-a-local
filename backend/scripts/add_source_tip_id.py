"""Migration: add source_tip_id column to tip_promotions."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import engine
from sqlalchemy import text


def run():
    with engine.connect() as conn:
        conn.execute(text("""
            ALTER TABLE tip_promotions
            ADD COLUMN IF NOT EXISTS source_tip_id INTEGER REFERENCES tips(id);
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_promotion_source_tip
            ON tip_promotions(source_tip_id);
        """))
        conn.commit()
    print("Added source_tip_id to tip_promotions")


if __name__ == "__main__":
    run()
