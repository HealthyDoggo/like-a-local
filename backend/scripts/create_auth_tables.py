"""Create authentication tables (users and refresh_tokens)"""
import sys
from pathlib import Path

# Add parent directory to path to import backend modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.database.connection import engine
from backend.database.models import Base, User, RefreshToken


def create_auth_tables():
    """Create users and refresh_tokens tables"""
    print("Creating authentication tables...")

    # This will only create tables that don't exist yet
    # Existing tables will not be modified
    Base.metadata.create_all(bind=engine, tables=[
        User.__table__,
        RefreshToken.__table__
    ])

    print("✓ Authentication tables created successfully!")
    print("  - users")
    print("  - refresh_tokens")


if __name__ == "__main__":
    create_auth_tables()
