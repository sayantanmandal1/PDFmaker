"""
Comment service for managing user comments on sections and slides.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.comment import Comment
from models.section import Section
from models.slide import Slide
from fastapi import HTTPException, status
import uuid


class CommentService:
    """Service for handling comment CRUD operations."""

    @staticmethod
    def create_comment(
        db: Session,
        user_id: uuid.UUID,
        comment_text: str,
        section_id: Optional[uuid.UUID] = None,
        slide_id: Optional[uuid.UUID] = None
    ) -> Comment:
        """
        Create a new comment for a section or slide.
        
        Args:
            db: Database session
            user_id: UUID of the user creating the comment
            comment_text: Text content of the comment
            section_id: UUID of the section (optional)
            slide_id: UUID of the slide (optional)
            
        Returns:
            Created Comment object
            
        Raises:
            HTTPException: If comment creation fails or validation fails
        """
        # Validate that exactly one of section_id or slide_id is provided
        if (section_id is None and slide_id is None) or (section_id is not None and slide_id is not None):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Must provide exactly one of section_id or slide_id"
            )
        
        # Validate comment_text is not empty
        if not comment_text or not comment_text.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Comment text cannot be empty"
            )
        
        try:
            new_comment = Comment(
                user_id=user_id,
                section_id=section_id,
                slide_id=slide_id,
                comment_text=comment_text
            )
            
            db.add(new_comment)
            db.commit()
            db.refresh(new_comment)
            
            return new_comment
            
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create comment"
            )

    @staticmethod
    def get_comments(
        db: Session,
        section_id: Optional[uuid.UUID] = None,
        slide_id: Optional[uuid.UUID] = None
    ) -> List[Comment]:
        """
        Get all comments for a section or slide.
        
        Args:
            db: Database session
            section_id: UUID of the section (optional)
            slide_id: UUID of the slide (optional)
            
        Returns:
            List of Comment objects ordered by creation date
        """
        try:
            if section_id:
                comments = db.query(Comment).filter(
                    Comment.section_id == section_id
                ).order_by(Comment.created_at).all()
            elif slide_id:
                comments = db.query(Comment).filter(
                    Comment.slide_id == slide_id
                ).order_by(Comment.created_at).all()
            else:
                return []
            
            return comments
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve comments"
            )

    @staticmethod
    def get_comment(
        db: Session,
        comment_id: uuid.UUID
    ) -> Optional[Comment]:
        """
        Get a specific comment by ID.
        
        Args:
            db: Database session
            comment_id: UUID of the comment
            
        Returns:
            Comment object if found, None otherwise
        """
        try:
            comment = db.query(Comment).filter(Comment.id == comment_id).first()
            return comment
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve comment"
            )

    @staticmethod
    def update_comment(
        db: Session,
        comment_id: uuid.UUID,
        user_id: uuid.UUID,
        comment_text: str
    ) -> Comment:
        """
        Update an existing comment (only by the user who created it).
        
        Args:
            db: Database session
            comment_id: UUID of the comment to update
            user_id: UUID of the user (for authorization)
            comment_text: New comment text
            
        Returns:
            Updated Comment object
            
        Raises:
            HTTPException: If comment not found, unauthorized, or update fails
        """
        # Validate comment_text is not empty
        if not comment_text or not comment_text.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Comment text cannot be empty"
            )
        
        try:
            comment = db.query(Comment).filter(Comment.id == comment_id).first()
            
            if not comment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Comment not found"
                )
            
            # Verify user owns the comment
            if comment.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to update this comment"
                )
            
            comment.comment_text = comment_text
            db.commit()
            db.refresh(comment)
            
            return comment
            
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update comment"
            )

    @staticmethod
    def delete_comment(
        db: Session,
        comment_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> None:
        """
        Delete a comment (only by the user who created it).
        
        Args:
            db: Database session
            comment_id: UUID of the comment to delete
            user_id: UUID of the user (for authorization)
            
        Raises:
            HTTPException: If comment not found, unauthorized, or deletion fails
        """
        try:
            comment = db.query(Comment).filter(Comment.id == comment_id).first()
            
            if not comment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Comment not found"
                )
            
            # Verify user owns the comment
            if comment.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to delete this comment"
                )
            
            db.delete(comment)
            db.commit()
            
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete comment"
            )
