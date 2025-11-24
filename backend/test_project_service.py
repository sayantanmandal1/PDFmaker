"""
Unit tests for ProjectService.
Tests the project management service layer directly without requiring API server.
"""
import pytest
from sqlalchemy import create_engine, event, TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import sessionmaker
from database import Base
from models.user import User
from models.project import Project
from services.project_service import ProjectService
from services.auth_service import AuthService
from fastapi import HTTPException
import uuid


# Custom UUID type that works with SQLite
class UUID(TypeDecorator):
    """Platform-independent UUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(36), storing as stringified hex values.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            else:
                return value


# Monkey patch the UUID type in models before creating tables
import sys
from sqlalchemy.dialects import postgresql
original_uuid = postgresql.UUID

def patched_uuid(*args, **kwargs):
    return UUID()

postgresql.UUID = patched_uuid

# Create in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

# Enable foreign key support for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db):
    """Create a test user."""
    user = AuthService.register_user(
        db=db,
        email=f"test_{uuid.uuid4().hex[:8]}@example.com",
        password="TestPassword123!",
        name="Test User"
    )
    return user


@pytest.fixture
def another_user(db):
    """Create another test user for authorization tests."""
    user = AuthService.register_user(
        db=db,
        email=f"another_{uuid.uuid4().hex[:8]}@example.com",
        password="TestPassword123!",
        name="Another User"
    )
    return user


def test_create_project_word(db, test_user):
    """Test creating a Word document project."""
    project = ProjectService.create_project(
        db=db,
        user_id=test_user.id,
        name="Test Word Document",
        document_type="word",
        topic="Introduction to Python"
    )
    
    assert project.id is not None
    assert project.user_id == test_user.id
    assert project.name == "Test Word Document"
    assert project.document_type == "word"
    assert project.topic == "Introduction to Python"
    assert project.status == "configuring"
    assert project.created_at is not None
    assert project.updated_at is not None
    print("✓ test_create_project_word passed")


def test_create_project_powerpoint(db, test_user):
    """Test creating a PowerPoint project."""
    project = ProjectService.create_project(
        db=db,
        user_id=test_user.id,
        name="Test Presentation",
        document_type="powerpoint",
        topic="Data Science Fundamentals"
    )
    
    assert project.id is not None
    assert project.user_id == test_user.id
    assert project.name == "Test Presentation"
    assert project.document_type == "powerpoint"
    assert project.topic == "Data Science Fundamentals"
    assert project.status == "configuring"
    print("✓ test_create_project_powerpoint passed")


def test_get_user_projects_empty(db, test_user):
    """Test getting projects when user has none."""
    projects = ProjectService.get_user_projects(db, test_user.id)
    
    assert projects == []
    assert len(projects) == 0
    print("✓ test_get_user_projects_empty passed")


def test_get_user_projects_multiple(db, test_user):
    """Test getting multiple projects for a user."""
    # Create multiple projects
    project1 = ProjectService.create_project(
        db=db,
        user_id=test_user.id,
        name="Project 1",
        document_type="word",
        topic="Topic 1"
    )
    
    project2 = ProjectService.create_project(
        db=db,
        user_id=test_user.id,
        name="Project 2",
        document_type="powerpoint",
        topic="Topic 2"
    )
    
    project3 = ProjectService.create_project(
        db=db,
        user_id=test_user.id,
        name="Project 3",
        document_type="word",
        topic="Topic 3"
    )
    
    # Get all projects
    projects = ProjectService.get_user_projects(db, test_user.id)
    
    assert len(projects) == 3
    project_names = [p.name for p in projects]
    assert "Project 1" in project_names
    assert "Project 2" in project_names
    assert "Project 3" in project_names
    print("✓ test_get_user_projects_multiple passed")


def test_get_user_projects_filtered_by_user(db, test_user, another_user):
    """Test that get_user_projects only returns projects for the specified user."""
    # Create projects for test_user
    ProjectService.create_project(
        db=db,
        user_id=test_user.id,
        name="User 1 Project",
        document_type="word",
        topic="Topic 1"
    )
    
    # Create projects for another_user
    ProjectService.create_project(
        db=db,
        user_id=another_user.id,
        name="User 2 Project",
        document_type="powerpoint",
        topic="Topic 2"
    )
    
    # Get projects for test_user
    user1_projects = ProjectService.get_user_projects(db, test_user.id)
    assert len(user1_projects) == 1
    assert user1_projects[0].name == "User 1 Project"
    
    # Get projects for another_user
    user2_projects = ProjectService.get_user_projects(db, another_user.id)
    assert len(user2_projects) == 1
    assert user2_projects[0].name == "User 2 Project"
    
    print("✓ test_get_user_projects_filtered_by_user passed")


def test_get_project_success(db, test_user):
    """Test getting a specific project successfully."""
    # Create a project
    created_project = ProjectService.create_project(
        db=db,
        user_id=test_user.id,
        name="Test Project",
        document_type="word",
        topic="Test Topic"
    )
    
    # Get the project
    retrieved_project = ProjectService.get_project(
        db=db,
        project_id=created_project.id,
        user_id=test_user.id
    )
    
    assert retrieved_project.id == created_project.id
    assert retrieved_project.name == "Test Project"
    assert retrieved_project.document_type == "word"
    assert retrieved_project.topic == "Test Topic"
    print("✓ test_get_project_success passed")


def test_get_project_not_found(db, test_user):
    """Test getting a non-existent project."""
    fake_project_id = uuid.uuid4()
    
    with pytest.raises(HTTPException) as exc_info:
        ProjectService.get_project(
            db=db,
            project_id=fake_project_id,
            user_id=test_user.id
        )
    
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail.lower()
    print("✓ test_get_project_not_found passed")


def test_get_project_unauthorized(db, test_user, another_user):
    """Test that users cannot access other users' projects."""
    # Create a project for test_user
    project = ProjectService.create_project(
        db=db,
        user_id=test_user.id,
        name="Private Project",
        document_type="word",
        topic="Private Topic"
    )
    
    # Try to access it as another_user
    with pytest.raises(HTTPException) as exc_info:
        ProjectService.get_project(
            db=db,
            project_id=project.id,
            user_id=another_user.id
        )
    
    assert exc_info.value.status_code == 403
    assert "permission" in exc_info.value.detail.lower()
    print("✓ test_get_project_unauthorized passed")


def test_delete_project_success(db, test_user):
    """Test deleting a project successfully."""
    # Create a project
    project = ProjectService.create_project(
        db=db,
        user_id=test_user.id,
        name="Project to Delete",
        document_type="word",
        topic="Delete Topic"
    )
    
    project_id = project.id
    
    # Delete the project
    ProjectService.delete_project(
        db=db,
        project_id=project_id,
        user_id=test_user.id
    )
    
    # Verify it's deleted
    with pytest.raises(HTTPException) as exc_info:
        ProjectService.get_project(
            db=db,
            project_id=project_id,
            user_id=test_user.id
        )
    
    assert exc_info.value.status_code == 404
    print("✓ test_delete_project_success passed")


def test_delete_project_unauthorized(db, test_user, another_user):
    """Test that users cannot delete other users' projects."""
    # Create a project for test_user
    project = ProjectService.create_project(
        db=db,
        user_id=test_user.id,
        name="Protected Project",
        document_type="word",
        topic="Protected Topic"
    )
    
    # Try to delete it as another_user
    with pytest.raises(HTTPException) as exc_info:
        ProjectService.delete_project(
            db=db,
            project_id=project.id,
            user_id=another_user.id
        )
    
    assert exc_info.value.status_code == 403
    assert "permission" in exc_info.value.detail.lower()
    
    # Verify project still exists
    existing_project = ProjectService.get_project(
        db=db,
        project_id=project.id,
        user_id=test_user.id
    )
    assert existing_project is not None
    print("✓ test_delete_project_unauthorized passed")


def test_delete_project_not_found(db, test_user):
    """Test deleting a non-existent project."""
    fake_project_id = uuid.uuid4()
    
    with pytest.raises(HTTPException) as exc_info:
        ProjectService.delete_project(
            db=db,
            project_id=fake_project_id,
            user_id=test_user.id
        )
    
    assert exc_info.value.status_code == 404
    print("✓ test_delete_project_not_found passed")


def test_project_unique_ids(db, test_user):
    """Test that all created projects have unique IDs."""
    project_ids = set()
    
    for i in range(10):
        project = ProjectService.create_project(
            db=db,
            user_id=test_user.id,
            name=f"Project {i}",
            document_type="word" if i % 2 == 0 else "powerpoint",
            topic=f"Topic {i}"
        )
        project_ids.add(project.id)
    
    # All IDs should be unique
    assert len(project_ids) == 10
    print("✓ test_project_unique_ids passed")


if __name__ == "__main__":
    print("=" * 60)
    print("Running ProjectService Unit Tests")
    print("=" * 60)
    print()
    
    # Run tests manually without pytest runner
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Setup
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    
    test_functions = [
        test_create_project_word,
        test_create_project_powerpoint,
        test_get_user_projects_empty,
        test_get_user_projects_multiple,
        test_get_user_projects_filtered_by_user,
        test_get_project_success,
        test_get_project_not_found,
        test_get_project_unauthorized,
        test_delete_project_success,
        test_delete_project_unauthorized,
        test_delete_project_not_found,
        test_project_unique_ids,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            # Create fresh database session
            TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            db = TestingSessionLocal()
            
            # Create test users
            test_user = AuthService.register_user(
                db=db,
                email=f"test_{uuid.uuid4().hex[:8]}@example.com",
                password="TestPassword123!",
                name="Test User"
            )
            
            another_user = AuthService.register_user(
                db=db,
                email=f"another_{uuid.uuid4().hex[:8]}@example.com",
                password="TestPassword123!",
                name="Another User"
            )
            
            # Run test
            if test_func.__code__.co_argcount == 2:
                test_func(db, test_user)
            elif test_func.__code__.co_argcount == 3:
                test_func(db, test_user, another_user)
            else:
                test_func(db)
            
            passed += 1
            
        except AssertionError as e:
            print(f"✗ {test_func.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__} error: {e}")
            failed += 1
        finally:
            db.close()
            Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)
    
    print()
    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("✓ All tests passed!")
    else:
        print(f"✗ {failed} test(s) failed")
