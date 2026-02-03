"""Reset category classifications to allow re-running classification"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import engine
from sqlalchemy import text


def reset_categories():
    """Reset all category assignments"""
    print("Resetting category classifications...")
    
    with engine.connect() as conn:
        # Reset tips
        result = conn.execute(text("""
            UPDATE tips 
            SET category_id = NULL,
                category_confidence = NULL,
                category_assigned_at = NULL
            WHERE category_assigned_at IS NOT NULL
        """))
        tips_reset = result.rowcount
        
        # Reset promotions
        result = conn.execute(text("""
            UPDATE tip_promotions 
            SET category_id = NULL
            WHERE category_id IS NOT NULL
        """))
        promotions_reset = result.rowcount
        
        conn.commit()
        print(f"✓ Reset {tips_reset} tips and {promotions_reset} promotions")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] in ["-h", "--help"]:
            print("Usage: python reset_categories.py [--unclassified-only]")
            print("\nOptions:")
            print("  (no args)              Reset all category assignments")
            print("  --unclassified-only    Reset only tips that weren't assigned a category")
            print("  -h, --help             Show this help message")
            sys.exit(0)
        elif sys.argv[1] == "--unclassified-only":
            reset_unclassified_only()
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use -h or --help for usage information")
            sys.exit(1)
    else:
        reset_categories()


def reset_unclassified_only():
    """Reset only tips that were processed but not assigned a category"""
    print("Resetting unclassified tips only...")
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            UPDATE tips 
            SET category_assigned_at = NULL
            WHERE category_assigned_at IS NOT NULL 
              AND category_id IS NULL
        """))
        
        conn.commit()
        print(f"✓ Reset {result.rowcount} unclassified tips for reprocessing")
