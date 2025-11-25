"""
Database migration script to add image metadata columns.
Adds image_url, image_placement, and image_position columns to sections and slides tables.
"""
import os
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

def check_column_exists(engine, table_name, column_name):
    """
    Check if a column exists in a table.
    """
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def migrate_add_image_columns():
    """
    Add image metadata columns to sections and slides tables.
    """
    engine = create_engine(DATABASE_URL)
    
    print("Starting database migration: Adding image metadata columns...")
    print(f"Database URL: {engine.url}")
    
    try:
        with engine.connect() as conn:
            # Check if tables exist
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            if 'sections' not in tables:
                print("✗ Error: 'sections' table does not exist")
                return False
            
            if 'slides' not in tables:
                print("✗ Error: 'slides' table does not exist")
                return False
            
            # Add columns to sections table
            print("\nMigrating 'sections' table...")
            
            if not check_column_exists(engine, 'sections', 'image_url'):
                conn.execute(text("ALTER TABLE sections ADD COLUMN image_url TEXT"))
                conn.commit()
                print("  ✓ Added 'image_url' column to sections")
            else:
                print("  - 'image_url' column already exists in sections")
            
            if not check_column_exists(engine, 'sections', 'image_placement'):
                conn.execute(text("ALTER TABLE sections ADD COLUMN image_placement VARCHAR(20)"))
                conn.commit()
                print("  ✓ Added 'image_placement' column to sections")
            else:
                print("  - 'image_placement' column already exists in sections")
            
            # Add columns to slides table
            print("\nMigrating 'slides' table...")
            
            if not check_column_exists(engine, 'slides', 'image_url'):
                conn.execute(text("ALTER TABLE slides ADD COLUMN image_url TEXT"))
                conn.commit()
                print("  ✓ Added 'image_url' column to slides")
            else:
                print("  - 'image_url' column already exists in slides")
            
            if not check_column_exists(engine, 'slides', 'image_placement'):
                conn.execute(text("ALTER TABLE slides ADD COLUMN image_placement VARCHAR(20)"))
                conn.commit()
                print("  ✓ Added 'image_placement' column to slides")
            else:
                print("  - 'image_placement' column already exists in slides")
            
            if not check_column_exists(engine, 'slides', 'image_position'):
                conn.execute(text("ALTER TABLE slides ADD COLUMN image_position VARCHAR(50)"))
                conn.commit()
                print("  ✓ Added 'image_position' column to slides")
            else:
                print("  - 'image_position' column already exists in slides")
            
            print("\n✓ Migration completed successfully!")
            return True
            
    except Exception as e:
        print(f"\n✗ Error during migration: {e}")
        raise
    finally:
        engine.dispose()

def main():
    """
    Main function to run the migration.
    """
    try:
        success = migrate_add_image_columns()
        if success:
            print("\nDatabase schema updated successfully.")
            print("New columns added:")
            print("  sections table:")
            print("    - image_url (TEXT)")
            print("    - image_placement (VARCHAR(20))")
            print("  slides table:")
            print("    - image_url (TEXT)")
            print("    - image_placement (VARCHAR(20))")
            print("    - image_position (VARCHAR(50))")
    except Exception as e:
        print(f"\nMigration failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()
