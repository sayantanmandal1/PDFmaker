"""
Database initialization script.
Creates all tables in the database based on SQLAlchemy models.
"""
from database import engine, Base, init_db
from models import User, Project, Section, Slide, RefinementHistory, Feedback, Comment

def main():
    """
    Initialize the database by creating all tables.
    """
    print("Initializing database...")
    print(f"Database URL: {engine.url}")
    
    try:
        # Create all tables
        init_db()
        print("✓ Database tables created successfully!")
        
        # Print created tables
        print("\nCreated tables:")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")
            
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        raise

if __name__ == "__main__":
    main()
