"""
Basic verification test for ProjectService using the actual PostgreSQL database.
"""
from sqlalchemy.orm import Session
from database import SessionLocal, init_db
from models.user import User
from models.project import Project
from services.project_service import ProjectService
from services.auth_service import AuthService
from fastapi import HTTPException
import uuid


def test_project_service():
    """Test the project service with actual database."""
    
    print("=" * 60)
    print("Testing ProjectService")
    print("=" * 60)
    
    # Initialize database
    init_db()
    db = SessionLocal()
    
    try:
        # Create a test user
        print("\n1. Creating test user...")
        test_email = f"test_project_{uuid.uuid4().hex[:8]}@example.com"
        test_user = AuthService.register_user(
            db=db,
            email=test_email,
            password="TestPassword123!",
            name="Test Project User"
        )
        print(f"   ✓ User created: {test_user.email}")
        
        # Test 1: Create a Word project
        print("\n2. Creating Word document project...")
        word_project = ProjectService.create_project(
            db=db,
            user_id=test_user.id,
            name="Test Word Document",
            document_type="word",
            topic="Introduction to Machine Learning"
        )
        assert word_project.id is not None
        assert word_project.user_id == test_user.id
        assert word_project.name == "Test Word Document"
        assert word_project.document_type == "word"
        assert word_project.topic == "Introduction to Machine Learning"
        assert word_project.status == "configuring"
        print(f"   ✓ Word project created: {word_project.name} (ID: {word_project.id})")
        
        # Test 2: Create a PowerPoint project
        print("\n3. Creating PowerPoint project...")
        ppt_project = ProjectService.create_project(
            db=db,
            user_id=test_user.id,
            name="Test Presentation",
            document_type="powerpoint",
            topic="Data Science Best Practices"
        )
        assert ppt_project.id is not None
        assert ppt_project.document_type == "powerpoint"
        print(f"   ✓ PowerPoint project created: {ppt_project.name} (ID: {ppt_project.id})")
        
        # Test 3: Get all user projects
        print("\n4. Retrieving all user projects...")
        projects = ProjectService.get_user_projects(db, test_user.id)
        assert len(projects) == 2
        project_names = [p.name for p in projects]
        assert "Test Word Document" in project_names
        assert "Test Presentation" in project_names
        print(f"   ✓ Retrieved {len(projects)} projects")
        for project in projects:
            print(f"     - {project.name} ({project.document_type})")
        
        # Test 4: Get specific project
        print(f"\n5. Retrieving specific project (ID: {word_project.id})...")
        retrieved_project = ProjectService.get_project(
            db=db,
            project_id=word_project.id,
            user_id=test_user.id
        )
        assert retrieved_project.id == word_project.id
        assert retrieved_project.name == "Test Word Document"
        print(f"   ✓ Project retrieved: {retrieved_project.name}")
        
        # Test 5: Test authorization - create another user
        print("\n6. Testing authorization with another user...")
        another_email = f"another_{uuid.uuid4().hex[:8]}@example.com"
        another_user = AuthService.register_user(
            db=db,
            email=another_email,
            password="TestPassword123!",
            name="Another User"
        )
        
        # Try to access first user's project
        try:
            ProjectService.get_project(
                db=db,
                project_id=word_project.id,
                user_id=another_user.id
            )
            print("   ✗ Authorization check failed - should have raised exception")
            assert False, "Should have raised HTTPException"
        except HTTPException as e:
            assert e.status_code == 403
            print(f"   ✓ Authorization check passed (403 Forbidden)")
        
        # Test 6: Test project not found
        print("\n7. Testing project not found...")
        fake_project_id = uuid.uuid4()
        try:
            ProjectService.get_project(
                db=db,
                project_id=fake_project_id,
                user_id=test_user.id
            )
            print("   ✗ Not found check failed - should have raised exception")
            assert False, "Should have raised HTTPException"
        except HTTPException as e:
            assert e.status_code == 404
            print(f"   ✓ Not found check passed (404 Not Found)")
        
        # Test 7: Delete project
        print(f"\n8. Deleting project (ID: {ppt_project.id})...")
        ProjectService.delete_project(
            db=db,
            project_id=ppt_project.id,
            user_id=test_user.id
        )
        print(f"   ✓ Project deleted")
        
        # Verify deletion
        print("\n9. Verifying project was deleted...")
        projects = ProjectService.get_user_projects(db, test_user.id)
        assert len(projects) == 1
        assert projects[0].name == "Test Word Document"
        print(f"   ✓ Remaining projects: {len(projects)}")
        
        # Try to access deleted project
        try:
            ProjectService.get_project(
                db=db,
                project_id=ppt_project.id,
                user_id=test_user.id
            )
            print("   ✗ Deleted project still accessible")
            assert False, "Should have raised HTTPException"
        except HTTPException as e:
            assert e.status_code == 404
            print(f"   ✓ Deleted project not found (404)")
        
        # Test 8: Test unique project IDs
        print("\n10. Testing unique project IDs...")
        project_ids = set()
        for i in range(5):
            project = ProjectService.create_project(
                db=db,
                user_id=test_user.id,
                name=f"Project {i}",
                document_type="word" if i % 2 == 0 else "powerpoint",
                topic=f"Topic {i}"
            )
            project_ids.add(project.id)
        
        assert len(project_ids) == 5
        print(f"   ✓ All {len(project_ids)} project IDs are unique")
        
        # Cleanup - delete test projects
        print("\n11. Cleaning up test data...")
        all_projects = ProjectService.get_user_projects(db, test_user.id)
        for project in all_projects:
            ProjectService.delete_project(db, project.id, test_user.id)
        
        # Delete test users
        db.delete(test_user)
        db.delete(another_user)
        db.commit()
        print(f"   ✓ Cleaned up {len(all_projects)} projects and 2 users")
        
        print("\n" + "=" * 60)
        print("✓ All ProjectService tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    test_project_service()
