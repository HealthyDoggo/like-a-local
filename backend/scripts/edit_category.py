"""Edit category descriptions and regenerate embeddings"""
import sys
import os
import tempfile
import subprocess

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
            print(f"Descriptions ({len(cat.description)} phrases):")
            for i, desc in enumerate(cat.description, 1):
                print(f"  {i}. {desc}")
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
        print(f"\nDescriptions ({len(category.description)} phrases):")
        for i, desc in enumerate(category.description, 1):
            print(f"  {i}. {desc}")
        print()

    finally:
        db.close()


def update_category_descriptions(category_id: str, new_descriptions: list):
    """Update a category's descriptions and regenerate embeddings"""
    db = SessionLocal()
    embedding_service = get_embedding_service()

    try:
        category = db.query(Category).filter(Category.id == category_id).first()

        if not category:
            print(f"Category '{category_id}' not found.")
            return

        print(f"\nUpdating category: {category.title}")
        print(f"\nOld descriptions ({len(category.description)} phrases):")
        for i, desc in enumerate(category.description, 1):
            print(f"  {i}. {desc}")

        print(f"\nNew descriptions ({len(new_descriptions)} phrases):")
        for i, desc in enumerate(new_descriptions, 1):
            print(f"  {i}. {desc}")

        # Generate new embeddings for all phrases
        logger.info(f"Generating embeddings for {len(new_descriptions)} phrases...")
        new_embeddings = embedding_service.embed_batch(new_descriptions)

        # Update category
        category.description = new_descriptions
        category.embedding = new_embeddings

        db.commit()
        print(f"\n✓ Successfully updated category '{category.title}'")
        print(f"✓ Generated {len(new_embeddings)} embeddings")

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
    """Interactively edit a category's description phrases using an editor"""
    db = SessionLocal()

    try:
        category = db.query(Category).filter(Category.id == category_id).first()

        if not category:
            print(f"Category '{category_id}' not found.")
            return

        print(f"\nEditing category: {category.title}")
        print(f"\nOpening editor to edit {len(category.description)} description phrases...")
        print("Each line is a separate phrase that will be embedded independently.")
        print("Empty lines will be ignored.")

        # Create temp file with current descriptions
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tf:
            temp_path = tf.name
            tf.write("# Edit category descriptions below\n")
            tf.write("# Each line is a separate phrase for embedding\n")
            tf.write("# Empty lines and lines starting with # will be ignored\n")
            tf.write(f"# Category: {category.title}\n")
            tf.write("\n")
            for desc in category.description:
                tf.write(f"{desc}\n")

        # Open in editor
        editor = os.environ.get('EDITOR', 'nano')
        try:
            subprocess.call([editor, temp_path])
        except Exception as e:
            print(f"Error opening editor: {e}")
            print("Trying with 'nano'...")
            subprocess.call(['nano', temp_path])

        # Read back the edited content
        with open(temp_path, 'r') as f:
            lines = f.readlines()

        # Parse descriptions (ignore comments and empty lines)
        new_descriptions = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                new_descriptions.append(line)

        # Clean up temp file
        os.unlink(temp_path)

        if not new_descriptions:
            print("No descriptions found. Cancelled.")
            return

        # Show what will be updated
        print(f"\nParsed {len(new_descriptions)} description phrases:")
        for i, desc in enumerate(new_descriptions, 1):
            print(f"  {i}. {desc}")

        confirm = input("\nProceed with update? (y/n): ")

        if confirm.lower() != 'y':
            print("Cancelled.")
            return

        db.close()  # Close before calling update function
        update_category_descriptions(category_id, new_descriptions)

    except KeyboardInterrupt:
        print("\n\nCancelled.")
        if 'temp_path' in locals():
            try:
                os.unlink(temp_path)
            except:
                pass
    finally:
        if db.is_active:
            db.close()


def simple_edit(category_id: str):
    """Simple line-by-line interactive editing in the terminal"""
    db = SessionLocal()

    try:
        category = db.query(Category).filter(Category.id == category_id).first()

        if not category:
            print(f"Category '{category_id}' not found.")
            return

        print(f"\nEditing category: {category.title}")
        print(f"\nCurrent descriptions:")
        for i, desc in enumerate(category.description, 1):
            print(f"  {i}. {desc}")

        print("\nEnter new descriptions (one per line, press Enter twice to finish):")
        print("Tip: Include keywords and phrases that tips in this category typically mention\n")

        new_descriptions = []
        empty_count = 0

        while True:
            line = input(f"{len(new_descriptions) + 1}. ").strip()

            if not line:
                empty_count += 1
                if empty_count >= 2 or (empty_count >= 1 and new_descriptions):
                    break
            else:
                empty_count = 0
                new_descriptions.append(line)

        if not new_descriptions:
            print("No descriptions entered. Cancelled.")
            return

        # Show what will be updated
        print(f"\nNew descriptions ({len(new_descriptions)} phrases):")
        for i, desc in enumerate(new_descriptions, 1):
            print(f"  {i}. {desc}")

        confirm = input("\nProceed with update? (y/n): ")

        if confirm.lower() != 'y':
            print("Cancelled.")
            return

        db.close()  # Close before calling update function
        update_category_descriptions(category_id, new_descriptions)

    except KeyboardInterrupt:
        print("\n\nCancelled.")
    finally:
        if db.is_active:
            db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python edit_category.py <command> [args]")
        print("\nCommands:")
        print("  list                      List all categories")
        print("  view <category-id>        View a specific category")
        print("  edit <category-id>        Edit category in text editor (recommended)")
        print("  simple <category-id>      Simple line-by-line editing in terminal")
        print("\nExamples:")
        print("  python edit_category.py list")
        print("  python edit_category.py view food-dining")
        print("  python edit_category.py edit food-dining")
        print("  python edit_category.py simple food-dining")
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

    elif command == "simple":
        if len(sys.argv) < 3:
            print("Error: category-id required")
            print("Usage: python edit_category.py simple <category-id>")
            sys.exit(1)
        simple_edit(sys.argv[2])

    else:
        print(f"Unknown command: {command}")
        print("Use -h or --help for usage information")
        sys.exit(1)
