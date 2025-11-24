"""
Feedback service for managing user feedback on sections and slides.
"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.feedback import Feedback
from models.section import Section
from models.slide import Slide
from fastapi import HTTPException, status
import uuid


class FeedbackService:
    """Service for handling feedback CRUD operations."""

    @staticmethod
    def add_feedback(
        db: Session,
        user_id: uuid.UUID,
        feedback_type: str,
        section_id: Optional[uuid.UUID] = None,
        slide_id: Optional[uuid.UUID] = None
    ) -> Feedback:
        """
        Add or update feedback for a section or slide.
        
        If feedback already exists for this user and content, it will be updated.
        Otherwise, a new feedback record will be created.
        
        Args:
            db: Database session
            user_id: UUID of the user providing feedback
            feedback_type: Type of feedback ('like' or 'dislike')
            section_id: UUID of the section (optional)
            slide_id: UUID of the slide (optional)
            
        Returns:
            Feedback object (created or updated)
            
        Raises:
            HTTPException: If feedback operation fails or validation fails
        """
        # Validate that exactly one of section_id or slide_id is provided
        if (section_id is None and slide_id is None) or (section_id is not None and slide_id is not None):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Must provide exactly one of section_id or slide_id"
            )
        
        # Validate feedback_type
        if feedback_type not in ['like', 'dislike']:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Feedback type must be 'like' or 'dislike'"
            )
        
        try:
            # Check if feedback already exists for this user and content
            existing_feedback = db.query(Feedback).filter(
                Feedback.user_id == user_id,
                Feedback.section_id == section_id if section_id else Feedback.slide_id == slide_id
            ).first()
            
            if existing_feedback:
                # Update existing feedback
                existing_feedback.feedback_type = feedback_type
                db.commit()
                db.refresh(existing_feedback)
                return existing_feedback
            else:
                # Create new feedback
                new_feedback = Feedback(
                    user_id=user_id,
                    section_id=section_id,
                    slide_id=slide_id,
                    feedback_type=feedback_type
                )
                
                db.add(new_feedback)
                db.commit()
                db.refresh(new_feedback)
                
                return new_feedback
                
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add feedback"
            )

    @staticmethod
    def get_feedback(
        db: Session,
        user_id: uuid.UUID,
        section_id: Optional[uuid.UUID] = None,
        slide_id: Optional[uuid.UUID] = None
    ) -> Optional[Feedback]:
        """
        Get feedback for a specific user and content.
        
        Args:
            db: Database session
            user_id: UUID of the user
            section_id: UUID of the section (optional)
            slide_id: UUID of the slide (optional)
            
        Returns:
            Feedback object if found, None otherwise
        """
        try:
            if section_id:
                feedback = db.query(Feedback).filter(
                    Feedback.user_id == user_id,
                    Feedback.section_id == section_id
                ).first()
            elif slide_id:
                feedback = db.query(Feedback).filter(
                    Feedback.user_id == user_id,
                    Feedback.slide_id == slide_id
                ).first()
            else:
                return None
            
            return feedback
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve feedback"
            )

    @staticmethod
    def delete_feedback(
        db: Session,
        feedback_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> None:
        """
        Delete feedback (only by the user who created it).
        
        Args:
            db: Database session
            feedback_id: UUID of the feedback to delete
            user_id: UUID of the user (for authorization)
            
        Raises:
            HTTPException: If feedback not found, unauthorized, or deletion fails
        """
        try:
            feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
            
            if not feedback:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Feedback not found"
                )
            
            # Verify user owns the feedback
            if feedback.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to delete this feedback"
                )
            
            db.delete(feedback)
            db.commit()
            
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete feedback"
            )
