import sys
import os
import tempfile
import subprocess

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import SessionLocal
from backend.database.models import Category
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def remove_category_descriptions():
    """Remove category descriptions from the database"""
    print("Removing category descriptions from the database...")
    
    with SessionLocal() as db:
        db.query(Category).delete()
        db.commit()
        print("✓ Removed all categories from the database")
    
if __name__ == "__main__":
    remove_category_descriptions()