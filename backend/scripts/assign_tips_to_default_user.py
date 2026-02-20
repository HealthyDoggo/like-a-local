"""Migration: assign tips without a user_id to user id 1."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import SessionLocal
from backend.database.models import Tip


def run():
    db = SessionLocal()
    try:
        updated = db.query(Tip).filter(Tip.user_id == None).update({"user_id": 1})
        db.commit()
        print(f"Updated {updated} tips to user_id=1")
    finally:
        db.close()


if __name__ == "__main__":
    run()
