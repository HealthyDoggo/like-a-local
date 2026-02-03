"""Edit category descriptions and regenerate embeddings"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import SessionLocal
from backend.database.models import Category
from backend.services.embedding import get_embedding_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def list_categories():
    """List all categories with their descriptions"""
    db = SessionLocal()
    try:
        categories = db.query(Category).order_by(Category.display_order).all()

        if not categories:
            print("No categories found in database.")
            return

        print("\n=== CATEGORIES ===\n")
        for cat in categories:
            print(f"ID: {cat.id}")
            print(f"Title: {cat.title}")
            print(f"Description: {cat.description}")
            print(f"Order: {cat.display_order}")
            print("-" * 80)

        print(f"\nTotal: {len(categories)} categories")

    finally:
        db.close()


def view_category(category_id: str):
    """View a specific category's details"""
    db = SessionLocal()
    try:
        category = db.query(Category).filter(Category.id == category_id).first()

        if not category:
            print(f"Category '{category_id}' not found.")
            return

        print(f"\nCategory: {category.title}")
        print(f"ID: {category.id}")
        print(f"Display Order: {category.display_order}")
        print(f"Icon: {category.icon_name}")
        print(f"Color: {category.color}")
        print(f"\nDescription:")
        print(category.description)
        print()

    finally:
        db.close()


def update_category_description(category_id: str, new_description: str):
    """Update a category's description and regenerate its embedding"""
    db = SessionLocal()
    embedding_service = get_embedding_service()

    try:
        category = db.query(Category).filter(Category.id == category_id).first()

        if not category:
            print(f"Category '{category_id}' not found.")
            return

        print(f"\nUpdating category: {category.title}")
        print(f"\nOld description:")
        print(category.description)
        print(f"\nNew description:")
        print(new_description)

        # Generate new embedding
        logger.info("Generating new embedding...")
        new_embedding = embedding_service.embed(new_description)

        # Update category
        category.description = new_description
        category.embedding = new_embedding

        db.commit()
        print(f"\n✓ Successfully updated category '{category.title}'")
        print("✓ Embedding regenerated")

        # Suggest reclassification
        print("\nNote: You may want to reclassify tips to reflect this change:")
        print("  python backend/scripts/reset_categories.py")
        print("  python backend/scripts/classify_existing_tips.py")

    except Exception as e:
        logger.error(f"Error updating category: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def interactive_edit(category_id: str):
    """Interactively edit a category description"""
    db = SessionLocal()

    try:
        category = db.query(Category).filter(Category.id == category_id).first()

        if not category:
            print(f"Category '{category_id}' not found.")
            return

        print(f"\nEditing category: {category.title}")
        print(f"\nCurrent description:")
        print(category.description)
        print("\nEnter new description (or press Ctrl+C to cancel):")
        print("(Tip: Include keywords and phrases that tips in this category typically mention)")
        print()

        # Read multiline input
        lines = []
        try:
            while True:
                line = input()
                if line.strip() == "":
                    break
                lines.append(line)
        except EOFError:
            pass

        new_description = " ".join(lines).strip()

        if not new_description:
            print("No description entered. Cancelled.")
            return

        # Confirm
        print(f"\nNew description will be:")
        print(new_description)
        confirm = input("\nProceed with update? (y/n): ")

        if confirm.lower() != 'y':
            print("Cancelled.")
            return

        db.close()  # Close before calling update function
        update_category_description(category_id, new_description)

    except KeyboardInterrupt:
        print("\n\nCancelled.")
    finally:
        if not db.is_active:
            db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python edit_category.py <command> [args]")
        print("\nCommands:")
        print("  list                           List all categories")
        print("  view <category-id>             View a specific category")
        print("  edit <category-id>             Interactively edit a category")
        print("  update <category-id> <desc>    Update category description directly")
        print("\nExamples:")
        print("  python edit_category.py list")
        print("  python edit_category.py view food-dining")
        print("  python edit_category.py edit food-dining")
        print('  python edit_category.py update food-dining "New description here"')
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        list_categories()

    elif command == "view":
        if len(sys.argv) < 3:
            print("Error: category-id required")
            print("Usage: python edit_category.py view <category-id>")
            sys.exit(1)
        view_category(sys.argv[2])

    elif command == "edit":
        if len(sys.argv) < 3:
            print("Error: category-id required")
            print("Usage: python edit_category.py edit <category-id>")
            sys.exit(1)
        interactive_edit(sys.argv[2])

    elif command == "update":
        if len(sys.argv) < 4:
            print("Error: category-id and description required")
            print('Usage: python edit_category.py update <category-id> "description"')
            sys.exit(1)
        category_id = sys.argv[2]
        new_description = " ".join(sys.argv[3:])
        update_category_description(category_id, new_description)

    else:
        print(f"Unknown command: {command}")
        print("Use -h or --help for usage information")
        sys.exit(1)
