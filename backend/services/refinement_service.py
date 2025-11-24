"""
Refinement service for tracking content refinement history.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.refinement_history import RefinementHistory
from models.section import Section
from models.slide import Slide
from fastapi import HTTPException, status
import uuid


class RefinementHistoryService:
    """Service for handling refinement history operations."""

    @staticmethod
    def store_refinement_history(
        db: Session,
        section_id: Optional[uuid.UUID],
        slide_id: Optional[uuid.UUID],
        refinement_prompt: str,
        previous_content: Optional[str],
        new_content: Optional[str]
    ) -> RefinementHistory:
        """
        Store a refinement history record.
        
        Args:
            db: Database session
            section_id: UUID of the section (if refining a section)
            slide_id: UUID of the slide (if refining a slide)
            refinement_prompt: The user's refinement instructions
            previous_content: The content before refinement
            new_content: The content after refinement
            
        Returns:
            Created RefinementHistory object
            
        Raises:
            HTTPException: If history creation fails
            ValueError: If both or neither section_id and slide_id are provided
        """
        # Validate that exactly one of section_id or slide_id is provided
        if (section_id is None and slide_id is None) or (section_id is not None and slide_id is not None):
            raise ValueError("Exactly one of section_id or slide_id must be provided")
        
        try:
            history_record = RefinementHistory(
                section_id=section_id,
                slide_id=slide_id,
                refinement_prompt=refinement_prompt,
                previous_content=previous_content,
                new_content=new_content
            )
            
            db.add(history_record)
            db.commit()
            db.refresh(history_record)
            
            return history_record
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store refinement history"
            )

    @staticmethod
    def get_section_refinement_history(
        db: Session,
        section_id: uuid.UUID
    ) -> List[RefinementHistory]:
        """
        Get all refinement history for a section.
        
        Args:
            db: Database session
            section_id: UUID of the section
            
        Returns:
            List of RefinementHistory objects ordered by creation time
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            history = db.query(RefinementHistory).filter(
                RefinementHistory.section_id == section_id
            ).order_by(RefinementHistory.created_at).all()
            
            return history
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve refinement history"
            )

    @staticmethod
    def get_slide_refinement_history(
        db: Session,
        slide_id: uuid.UUID
    ) -> List[RefinementHistory]:
        """
        Get all refinement history for a slide.
        
        Args:
            db: Database session
            slide_id: UUID of the slide
            
        Returns:
            List of RefinementHistory objects ordered by creation time
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            history = db.query(RefinementHistory).filter(
                RefinementHistory.slide_id == slide_id
            ).order_by(RefinementHistory.created_at).all()
            
            return history
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve refinement history"
            )
