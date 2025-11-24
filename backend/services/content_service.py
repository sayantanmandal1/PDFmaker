"""
Content service for managing sections and slides.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.section import Section
from models.slide import Slide
from models.project import Project
from fastapi import HTTPException, status
import uuid


class ContentService:
    """Service for handling section and slide CRUD operations."""

    # Section operations
    
    @staticmethod
    def create_section(
        db: Session,
        project_id: uuid.UUID,
        header: str,
        content: Optional[str],
        position: int
    ) -> Section:
        """
        Create a new section for a Word document project.
        
        Args:
            db: Database session
            project_id: UUID of the project
            header: Section header text
            content: Section content (optional)
            position: Position of the section in the document
            
        Returns:
            Created Section object
            
        Raises:
            HTTPException: If section creation fails
        """
        try:
            new_section = Section(
                project_id=project_id,
                header=header,
                content=content,
                position=position
            )
            
            db.add(new_section)
            db.commit()
            db.refresh(new_section)
            
            return new_section
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create section"
            )

    @staticmethod
    def update_section(
        db: Session,
        section_id: uuid.UUID,
        header: Optional[str] = None,
        content: Optional[str] = None,
        position: Optional[int] = None
    ) -> Section:
        """
        Update an existing section.
        
        Args:
            db: Database session
            section_id: UUID of the section to update
            header: New header text (optional)
            content: New content (optional)
            position: New position (optional)
            
        Returns:
            Updated Section object
            
        Raises:
            HTTPException: If section not found or update fails
        """
        try:
            section = db.query(Section).filter(Section.id == section_id).first()
            
            if not section:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Section not found"
                )
            
            # Update fields if provided
            if header is not None:
                section.header = header
            if content is not None:
                section.content = content
            if position is not None:
                section.position = position
            
            db.commit()
            db.refresh(section)
            
            return section
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update section"
            )

    @staticmethod
    def delete_section(
        db: Session,
        section_id: uuid.UUID
    ) -> None:
        """
        Delete a section (cascade will handle related records).
        
        Args:
            db: Database session
            section_id: UUID of the section to delete
            
        Raises:
            HTTPException: If section not found or deletion fails
        """
        try:
            section = db.query(Section).filter(Section.id == section_id).first()
            
            if not section:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Section not found"
                )
            
            db.delete(section)
            db.commit()
            
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete section"
            )

    @staticmethod
    def reorder_sections(
        db: Session,
        project_id: uuid.UUID,
        section_positions: List[dict]
    ) -> List[Section]:
        """
        Reorder sections by updating their positions.
        
        Args:
            db: Database session
            project_id: UUID of the project
            section_positions: List of dicts with 'section_id' and 'position'
            
        Returns:
            List of updated Section objects
            
        Raises:
            HTTPException: If reordering fails
        """
        try:
            updated_sections = []
            
            for item in section_positions:
                section_id = item.get('section_id')
                new_position = item.get('position')
                
                # Convert string UUID to UUID object if needed
                if isinstance(section_id, str):
                    section_id = uuid.UUID(section_id)
                
                section = db.query(Section).filter(
                    Section.id == section_id,
                    Section.project_id == project_id
                ).first()
                
                if not section:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Section {section_id} not found"
                    )
                
                section.position = new_position
                updated_sections.append(section)
            
            db.commit()
            
            # Refresh all sections and return them ordered by position
            for section in updated_sections:
                db.refresh(section)
            
            return sorted(updated_sections, key=lambda s: s.position)
            
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reorder sections"
            )

    @staticmethod
    def get_project_sections(
        db: Session,
        project_id: uuid.UUID
    ) -> List[Section]:
        """
        Get all sections for a project, ordered by position.
        
        Args:
            db: Database session
            project_id: UUID of the project
            
        Returns:
            List of Section objects ordered by position
        """
        try:
            sections = db.query(Section).filter(
                Section.project_id == project_id
            ).order_by(Section.position).all()
            
            return sections
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve sections"
            )

    # Slide operations
    
    @staticmethod
    def create_slide(
        db: Session,
        project_id: uuid.UUID,
        title: str,
        content: Optional[str],
        position: int
    ) -> Slide:
        """
        Create a new slide for a PowerPoint project.
        
        Args:
            db: Database session
            project_id: UUID of the project
            title: Slide title
            content: Slide content (optional)
            position: Position of the slide in the presentation
            
        Returns:
            Created Slide object
            
        Raises:
            HTTPException: If slide creation fails
        """
        try:
            new_slide = Slide(
                project_id=project_id,
                title=title,
                content=content,
                position=position
            )
            
            db.add(new_slide)
            db.commit()
            db.refresh(new_slide)
            
            return new_slide
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create slide"
            )

    @staticmethod
    def update_slide(
        db: Session,
        slide_id: uuid.UUID,
        title: Optional[str] = None,
        content: Optional[str] = None,
        position: Optional[int] = None
    ) -> Slide:
        """
        Update an existing slide.
        
        Args:
            db: Database session
            slide_id: UUID of the slide to update
            title: New title (optional)
            content: New content (optional)
            position: New position (optional)
            
        Returns:
            Updated Slide object
            
        Raises:
            HTTPException: If slide not found or update fails
        """
        try:
            slide = db.query(Slide).filter(Slide.id == slide_id).first()
            
            if not slide:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Slide not found"
                )
            
            # Update fields if provided
            if title is not None:
                slide.title = title
            if content is not None:
                slide.content = content
            if position is not None:
                slide.position = position
            
            db.commit()
            db.refresh(slide)
            
            return slide
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update slide"
            )

    @staticmethod
    def create_slide_placeholders(
        db: Session,
        project_id: uuid.UUID,
        slide_count: int
    ) -> List[Slide]:
        """
        Create placeholder slides for a PowerPoint project.
        
        This method generates N empty slides with default titles like "Slide 1", "Slide 2", etc.
        
        Args:
            db: Database session
            project_id: UUID of the project
            slide_count: Number of slides to create
            
        Returns:
            List of created Slide objects
            
        Raises:
            HTTPException: If slide creation fails
        """
        try:
            created_slides = []
            
            for i in range(slide_count):
                new_slide = Slide(
                    project_id=project_id,
                    title=f"Slide {i + 1}",
                    content=None,
                    position=i
                )
                db.add(new_slide)
                created_slides.append(new_slide)
            
            db.commit()
            
            # Refresh all slides
            for slide in created_slides:
                db.refresh(slide)
            
            return created_slides
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create slide placeholders"
            )

    @staticmethod
    def get_project_slides(
        db: Session,
        project_id: uuid.UUID
    ) -> List[Slide]:
        """
        Get all slides for a project, ordered by position.
        
        Args:
            db: Database session
            project_id: UUID of the project
            
        Returns:
            List of Slide objects ordered by position
        """
        try:
            slides = db.query(Slide).filter(
                Slide.project_id == project_id
            ).order_by(Slide.position).all()
            
            return slides
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve slides"
            )
