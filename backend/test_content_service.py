"""
Unit tests for ContentService.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from models.user import User
from models.project import Project
from models.section import Section
from models.slide import Slide
from services.content_service import ContentService
from services.auth_service import AuthService
from services.project_service import ProjectService
import uuid


# Create in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
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
        email="test@example.com",
        password="TestPassword123!",
        name="Test User"
    )
    return user


@pytest.fixture
def word_project(db, test_user):
    """Create a test Word project."""
    project = ProjectService.create_project(
        db=db,
        user_id=test_user.id,
        name="Test Word Document",
        document_type="word",
        topic="Test Topic"
    )
    return project


@pytest.fixture
def ppt_project(db, test_user):
    """Create a test PowerPoint project."""
    project = ProjectService.create_project(
        db=db,
        user_id=test_user.id,
        name="Test Presentation",
        document_type="powerpoint",
        topic="Test Topic"
    )
    return project


def test_create_section(db, word_project):
    """Test creating a section."""
    section = ContentService.create_section(
        db=db,
        project_id=word_project.id,
        header="Introduction",
        content=None,
        position=0
    )
    
    assert section.id is not None
    assert section.project_id == word_project.id
    assert section.header == "Introduction"
    assert section.content is None
    assert section.position == 0


def test_update_section(db, word_project):
    """Test updating a section."""
    # Create a section
    section = ContentService.create_section(
        db=db,
        project_id=word_project.id,
        header="Introduction",
        content=None,
        position=0
    )
    
    # Update the section
    updated_section = ContentService.update_section(
        db=db,
        section_id=section.id,
        header="Updated Introduction",
        content="This is the updated content",
        position=1
    )
    
    assert updated_section.id == section.id
    assert updated_section.header == "Updated Introduction"
    assert updated_section.content == "This is the updated content"
    assert updated_section.position == 1


def test_delete_section(db, word_project):
    """Test deleting a section."""
    # Create a section
    section = ContentService.create_section(
        db=db,
        project_id=word_project.id,
        header="Introduction",
        content=None,
        position=0
    )
    
    section_id = section.id
    
    # Delete the section
    ContentService.delete_section(db=db, section_id=section_id)
    
    # Verify it's deleted
    deleted_section = db.query(Section).filter(Section.id == section_id).first()
    assert deleted_section is None


def test_reorder_sections(db, word_project):
    """Test reordering sections."""
    # Create multiple sections
    section1 = ContentService.create_section(
        db=db, project_id=word_project.id, header="First", content=None, position=0
    )
    section2 = ContentService.create_section(
        db=db, project_id=word_project.id, header="Second", content=None, position=1
    )
    section3 = ContentService.create_section(
        db=db, project_id=word_project.id, header="Third", content=None, position=2
    )
    
    # Reorder: swap first and third
    section_positions = [
        {"section_id": str(section3.id), "position": 0},
        {"section_id": str(section2.id), "position": 1},
        {"section_id": str(section1.id), "position": 2}
    ]
    
    reordered = ContentService.reorder_sections(
        db=db,
        project_id=word_project.id,
        section_positions=section_positions
    )
    
    assert len(reordered) == 3
    assert reordered[0].header == "Third"
    assert reordered[0].position == 0
    assert reordered[1].header == "Second"
    assert reordered[1].position == 1
    assert reordered[2].header == "First"
    assert reordered[2].position == 2


def test_get_project_sections(db, word_project):
    """Test retrieving all sections for a project."""
    # Create multiple sections
    ContentService.create_section(
        db=db, project_id=word_project.id, header="Introduction", content=None, position=0
    )
    ContentService.create_section(
        db=db, project_id=word_project.id, header="Background", content=None, position=1
    )
    ContentService.create_section(
        db=db, project_id=word_project.id, header="Conclusion", content=None, position=2
    )
    
    sections = ContentService.get_project_sections(db=db, project_id=word_project.id)
    
    assert len(sections) == 3
    assert sections[0].header == "Introduction"
    assert sections[1].header == "Background"
    assert sections[2].header == "Conclusion"


def test_create_slide(db, ppt_project):
    """Test creating a slide."""
    slide = ContentService.create_slide(
        db=db,
        project_id=ppt_project.id,
        title="Title Slide",
        content=None,
        position=0
    )
    
    assert slide.id is not None
    assert slide.project_id == ppt_project.id
    assert slide.title == "Title Slide"
    assert slide.content is None
    assert slide.position == 0


def test_update_slide(db, ppt_project):
    """Test updating a slide."""
    # Create a slide
    slide = ContentService.create_slide(
        db=db,
        project_id=ppt_project.id,
        title="Title Slide",
        content=None,
        position=0
    )
    
    # Update the slide
    updated_slide = ContentService.update_slide(
        db=db,
        slide_id=slide.id,
        title="Updated Title",
        content="This is the updated content",
        position=1
    )
    
    assert updated_slide.id == slide.id
    assert updated_slide.title == "Updated Title"
    assert updated_slide.content == "This is the updated content"
    assert updated_slide.position == 1


def test_create_slide_placeholders(db, ppt_project):
    """Test creating placeholder slides."""
    # Create 5 placeholder slides
    slides = ContentService.create_slide_placeholders(
        db=db,
        project_id=ppt_project.id,
        slide_count=5
    )
    
    assert len(slides) == 5
    assert slides[0].title == "Slide 1"
    assert slides[0].position == 0
    assert slides[0].content is None
    assert slides[4].title == "Slide 5"
    assert slides[4].position == 4
    assert slides[4].content is None


def test_get_project_slides(db, ppt_project):
    """Test retrieving all slides for a project."""
    # Create multiple slides
    ContentService.create_slide(
        db=db, project_id=ppt_project.id, title="Slide 1", content=None, position=0
    )
    ContentService.create_slide(
        db=db, project_id=ppt_project.id, title="Slide 2", content=None, position=1
    )
    ContentService.create_slide(
        db=db, project_id=ppt_project.id, title="Slide 3", content=None, position=2
    )
    
    slides = ContentService.get_project_slides(db=db, project_id=ppt_project.id)
    
    assert len(slides) == 3
    assert slides[0].title == "Slide 1"
    assert slides[1].title == "Slide 2"
    assert slides[2].title == "Slide 3"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
