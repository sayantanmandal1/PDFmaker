"""
Test database integrity, relationships, and constraints.
"""
from sqlalchemy import inspect
from database import engine, SessionLocal
from models import User, Project, Section, Slide, RefinementHistory, Feedback, Comment


def test_foreign_key_constraints():
    """Test that foreign key constraints are properly set up."""
    inspector = inspect(engine)
    
    # Test projects table has foreign key to users
    fks = inspector.get_foreign_keys("projects")
    assert any(fk["referred_table"] == "users" for fk in fks), "Projects should reference users"
    print("✓ Projects table has foreign key to users")
    
    # Test sections table has foreign key to projects
    fks = inspector.get_foreign_keys("sections")
    assert any(fk["referred_table"] == "projects" for fk in fks), "Sections should reference projects"
    print("✓ Sections table has foreign key to projects")
    
    # Test slides table has foreign key to projects
    fks = inspector.get_foreign_keys("slides")
    assert any(fk["referred_table"] == "projects" for fk in fks), "Slides should reference projects"
    print("✓ Slides table has foreign key to projects")
    
    # Test refinement_history has foreign keys to sections and slides
    fks = inspector.get_foreign_keys("refinement_history")
    assert any(fk["referred_table"] == "sections" for fk in fks), "Refinement history should reference sections"
    assert any(fk["referred_table"] == "slides" for fk in fks), "Refinement history should reference slides"
    print("✓ Refinement history table has foreign keys to sections and slides")
    
    # Test feedback has foreign keys
    fks = inspector.get_foreign_keys("feedback")
    assert any(fk["referred_table"] == "sections" for fk in fks), "Feedback should reference sections"
    assert any(fk["referred_table"] == "slides" for fk in fks), "Feedback should reference slides"
    assert any(fk["referred_table"] == "users" for fk in fks), "Feedback should reference users"
    print("✓ Feedback table has foreign keys to sections, slides, and users")
    
    # Test comments has foreign keys
    fks = inspector.get_foreign_keys("comments")
    assert any(fk["referred_table"] == "sections" for fk in fks), "Comments should reference sections"
    assert any(fk["referred_table"] == "slides" for fk in fks), "Comments should reference slides"
    assert any(fk["referred_table"] == "users" for fk in fks), "Comments should reference users"
    print("✓ Comments table has foreign keys to sections, slides, and users")


def test_check_constraints():
    """Test that check constraints are properly set up."""
    inspector = inspect(engine)
    
    # Test projects table has document_type constraint
    constraints = inspector.get_check_constraints("projects")
    assert any("document_type" in str(c.get("sqltext", "")).lower() for c in constraints), \
        "Projects should have document_type check constraint"
    print("✓ Projects table has document_type check constraint")
    
    # Test feedback table has feedback_type constraint
    constraints = inspector.get_check_constraints("feedback")
    assert any("feedback_type" in str(c.get("sqltext", "")).lower() for c in constraints), \
        "Feedback should have feedback_type check constraint"
    print("✓ Feedback table has feedback_type check constraint")


def test_indexes():
    """Test that indexes are properly created."""
    inspector = inspect(engine)
    
    # Test users table has email index
    indexes = inspector.get_indexes("users")
    index_columns = [idx["column_names"] for idx in indexes]
    assert any("email" in cols for cols in index_columns), "Users should have email index"
    print("✓ Users table has email index")
    
    # Test projects table has user_id index
    indexes = inspector.get_indexes("projects")
    index_columns = [idx["column_names"] for idx in indexes]
    assert any("user_id" in cols for cols in index_columns), "Projects should have user_id index"
    print("✓ Projects table has user_id index")


def test_cascade_delete_setup():
    """Test that cascade delete is properly configured in the database."""
    db = SessionLocal()
    try:
        # Create a test user
        user = User(
            email="cascade_test@example.com",
            name="Cascade Test",
            password_hash="test_hash"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create a test project
        project = Project(
            user_id=user.id,
            name="Test Project",
            document_type="word",
            topic="Test Topic"
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        
        # Create a test section
        section = Section(
            project_id=project.id,
            header="Test Header",
            position=1
        )
        db.add(section)
        db.commit()
        db.refresh(section)
        
        project_id = project.id
        section_id = section.id
        user_id = user.id
        
        # Delete the user (should cascade to project and section)
        db.delete(user)
        db.commit()
        
        # Verify project and section are deleted
        assert db.query(Project).filter(Project.id == project_id).first() is None, \
            "Project should be deleted when user is deleted"
        assert db.query(Section).filter(Section.id == section_id).first() is None, \
            "Section should be deleted when project is deleted"
        
        print("✓ Cascade delete works correctly (user -> project -> section)")
        
    finally:
        # Cleanup: try to delete test user if it still exists
        test_user = db.query(User).filter(User.email == "cascade_test@example.com").first()
        if test_user:
            db.delete(test_user)
            db.commit()
        db.close()


if __name__ == "__main__":
    print("\nRunning database integrity tests...\n")
    
    test_foreign_key_constraints()
    test_check_constraints()
    test_indexes()
    test_cascade_delete_setup()
    
    print("\n✓ All database integrity tests passed!")
