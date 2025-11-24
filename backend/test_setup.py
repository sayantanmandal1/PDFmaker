"""
Test script to verify database setup and models.
"""
import pytest
from sqlalchemy import inspect
from database import engine, SessionLocal
from models import User, Project, Section, Slide, RefinementHistory, Feedback, Comment


def test_database_connection():
    """Test that database connection is working."""
    with engine.connect() as connection:
        assert connection is not None
        print("✓ Database connection successful")


def test_all_tables_exist():
    """Test that all required tables exist in the database."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    required_tables = [
        "users",
        "projects", 
        "sections",
        "slides",
        "refinement_history",
        "feedback",
        "comments"
    ]
    
    for table in required_tables:
        assert table in tables, f"Table {table} not found in database"
        print(f"✓ Table '{table}' exists")


def test_user_model():
    """Test User model can be instantiated."""
    user = User(
        email="test@example.com",
        name="Test User",
        password_hash="hashed_password"
    )
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    print("✓ User model works correctly")


def test_project_model():
    """Test Project model can be instantiated."""
    project = Project(
        name="Test Project",
        document_type="word",
        topic="Test Topic",
        status="configuring"
    )
    assert project.name == "Test Project"
    assert project.document_type == "word"
    print("✓ Project model works correctly")


def test_section_model():
    """Test Section model can be instantiated."""
    section = Section(
        header="Test Header",
        content="Test Content",
        position=1
    )
    assert section.header == "Test Header"
    assert section.position == 1
    print("✓ Section model works correctly")


def test_slide_model():
    """Test Slide model can be instantiated."""
    slide = Slide(
        title="Test Title",
        content="Test Content",
        position=1
    )
    assert slide.title == "Test Title"
    assert slide.position == 1
    print("✓ Slide model works correctly")


if __name__ == "__main__":
    print("\nRunning database setup tests...\n")
    
    test_database_connection()
    test_all_tables_exist()
    test_user_model()
    test_project_model()
    test_section_model()
    test_slide_model()
    
    print("\n✓ All setup tests passed!")
