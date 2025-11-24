"""
Content router for refinement endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database import get_db
from dependencies.auth import get_current_user
from models.user import User
from models.section import Section
from models.slide import Slide
from schemas.content_schemas import (
    RefinementRequest,
    SectionResponse,
    SlideResponse,
    RefinementHistoryResponse,
    FeedbackCreate,
    FeedbackResponse,
    CommentCreate,
    CommentUpdate,
    CommentResponse
)
from services.llm_service import LLMService
from services.content_service import ContentService
from services.refinement_service import RefinementHistoryService
from services.feedback_service import FeedbackService
from services.comment_service import CommentService
from openai import RateLimitError, APIError, APIConnectionError

router = APIRouter()


@router.post("/sections/{section_id}/refine", response_model=SectionResponse)
async def refine_section(
    section_id: UUID,
    refinement_request: RefinementRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Refine content for a specific section using AI.
    
    Args:
        section_id: UUID of the section to refine
        refinement_request: Refinement instructions
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Updated section with refined content
        
    Raises:
        HTTPException: If section not found, unauthorized, or refinement fails
    """
    # Get the section
    section = db.query(Section).filter(Section.id == section_id).first()
    
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )
    
    # Verify user owns the project
    if section.project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this section"
        )
    
    # Store the current content before refinement
    previous_content = section.content
    
    if not previous_content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot refine section without existing content"
        )
    
    try:
        # Initialize LLM service and refine content
        llm_service = LLMService()
        refined_content = llm_service.refine_content(
            current_content=previous_content,
            refinement_prompt=refinement_request.prompt
        )
        
        # Update the section with refined content
        updated_section = ContentService.update_section(
            db=db,
            section_id=section_id,
            content=refined_content
        )
        
        # Store refinement history
        RefinementHistoryService.store_refinement_history(
            db=db,
            section_id=section_id,
            slide_id=None,
            refinement_prompt=refinement_request.prompt,
            previous_content=previous_content,
            new_content=refined_content
        )
        
        return updated_section
        
    except RateLimitError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded, please try again later"
        )
    except (APIError, APIConnectionError):
        # Preserve current content on failure
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Content generation service temporarily unavailable"
        )
    except Exception as e:
        # Preserve current content on any other failure
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Refinement failed, content preserved"
        )


@router.post("/slides/{slide_id}/refine", response_model=SlideResponse)
async def refine_slide(
    slide_id: UUID,
    refinement_request: RefinementRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Refine content for a specific slide using AI.
    
    Args:
        slide_id: UUID of the slide to refine
        refinement_request: Refinement instructions
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Updated slide with refined content
        
    Raises:
        HTTPException: If slide not found, unauthorized, or refinement fails
    """
    # Get the slide
    slide = db.query(Slide).filter(Slide.id == slide_id).first()
    
    if not slide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slide not found"
        )
    
    # Verify user owns the project
    if slide.project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this slide"
        )
    
    # Store the current content before refinement
    previous_content = slide.content
    
    if not previous_content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot refine slide without existing content"
        )
    
    try:
        # Initialize LLM service and refine content
        llm_service = LLMService()
        refined_content = llm_service.refine_content(
            current_content=previous_content,
            refinement_prompt=refinement_request.prompt
        )
        
        # Update the slide with refined content
        updated_slide = ContentService.update_slide(
            db=db,
            slide_id=slide_id,
            content=refined_content
        )
        
        # Store refinement history
        RefinementHistoryService.store_refinement_history(
            db=db,
            section_id=None,
            slide_id=slide_id,
            refinement_prompt=refinement_request.prompt,
            previous_content=previous_content,
            new_content=refined_content
        )
        
        return updated_slide
        
    except RateLimitError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded, please try again later"
        )
    except (APIError, APIConnectionError):
        # Preserve current content on failure
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Content generation service temporarily unavailable"
        )
    except Exception as e:
        # Preserve current content on any other failure
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Refinement failed, content preserved"
        )


@router.get("/sections/{section_id}/refinement-history", response_model=List[RefinementHistoryResponse])
async def get_section_refinement_history(
    section_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get refinement history for a section.
    
    Args:
        section_id: UUID of the section
        db: Database session
        current_user: Authenticated user
        
    Returns:
        List of refinement history records
        
    Raises:
        HTTPException: If section not found or unauthorized
    """
    # Get the section
    section = db.query(Section).filter(Section.id == section_id).first()
    
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )
    
    # Verify user owns the project
    if section.project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this section"
        )
    
    # Get refinement history
    history = RefinementHistoryService.get_section_refinement_history(
        db=db,
        section_id=section_id
    )
    
    return history


@router.get("/slides/{slide_id}/refinement-history", response_model=List[RefinementHistoryResponse])
async def get_slide_refinement_history(
    slide_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get refinement history for a slide.
    
    Args:
        slide_id: UUID of the slide
        db: Database session
        current_user: Authenticated user
        
    Returns:
        List of refinement history records
        
    Raises:
        HTTPException: If slide not found or unauthorized
    """
    # Get the slide
    slide = db.query(Slide).filter(Slide.id == slide_id).first()
    
    if not slide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slide not found"
        )
    
    # Verify user owns the project
    if slide.project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this slide"
        )
    
    # Get refinement history
    history = RefinementHistoryService.get_slide_refinement_history(
        db=db,
        slide_id=slide_id
    )
    
    return history



# Feedback endpoints

@router.post("/sections/{section_id}/feedback", response_model=FeedbackResponse)
async def add_section_feedback(
    section_id: UUID,
    feedback_request: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add or update feedback for a section.
    
    If feedback already exists for this user and section, it will be updated.
    
    Args:
        section_id: UUID of the section
        feedback_request: Feedback data (like/dislike)
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Feedback record
        
    Raises:
        HTTPException: If section not found, unauthorized, or operation fails
    """
    # Get the section
    section = db.query(Section).filter(Section.id == section_id).first()
    
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )
    
    # Verify user owns the project
    if section.project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this section"
        )
    
    # Add or update feedback
    feedback = FeedbackService.add_feedback(
        db=db,
        user_id=current_user.id,
        feedback_type=feedback_request.feedback_type,
        section_id=section_id
    )
    
    return feedback


@router.post("/slides/{slide_id}/feedback", response_model=FeedbackResponse)
async def add_slide_feedback(
    slide_id: UUID,
    feedback_request: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add or update feedback for a slide.
    
    If feedback already exists for this user and slide, it will be updated.
    
    Args:
        slide_id: UUID of the slide
        feedback_request: Feedback data (like/dislike)
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Feedback record
        
    Raises:
        HTTPException: If slide not found, unauthorized, or operation fails
    """
    # Get the slide
    slide = db.query(Slide).filter(Slide.id == slide_id).first()
    
    if not slide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slide not found"
        )
    
    # Verify user owns the project
    if slide.project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this slide"
        )
    
    # Add or update feedback
    feedback = FeedbackService.add_feedback(
        db=db,
        user_id=current_user.id,
        feedback_type=feedback_request.feedback_type,
        slide_id=slide_id
    )
    
    return feedback


# Comment endpoints

@router.post("/sections/{section_id}/comments", response_model=CommentResponse)
async def add_section_comment(
    section_id: UUID,
    comment_request: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a comment to a section.
    
    Args:
        section_id: UUID of the section
        comment_request: Comment data
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Created comment
        
    Raises:
        HTTPException: If section not found, unauthorized, or operation fails
    """
    # Get the section
    section = db.query(Section).filter(Section.id == section_id).first()
    
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )
    
    # Verify user owns the project
    if section.project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this section"
        )
    
    # Create comment
    comment = CommentService.create_comment(
        db=db,
        user_id=current_user.id,
        comment_text=comment_request.comment_text,
        section_id=section_id
    )
    
    return comment


@router.post("/slides/{slide_id}/comments", response_model=CommentResponse)
async def add_slide_comment(
    slide_id: UUID,
    comment_request: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a comment to a slide.
    
    Args:
        slide_id: UUID of the slide
        comment_request: Comment data
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Created comment
        
    Raises:
        HTTPException: If slide not found, unauthorized, or operation fails
    """
    # Get the slide
    slide = db.query(Slide).filter(Slide.id == slide_id).first()
    
    if not slide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slide not found"
        )
    
    # Verify user owns the project
    if slide.project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this slide"
        )
    
    # Create comment
    comment = CommentService.create_comment(
        db=db,
        user_id=current_user.id,
        comment_text=comment_request.comment_text,
        slide_id=slide_id
    )
    
    return comment


@router.get("/sections/{section_id}/comments", response_model=List[CommentResponse])
async def get_section_comments(
    section_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all comments for a section.
    
    Args:
        section_id: UUID of the section
        db: Database session
        current_user: Authenticated user
        
    Returns:
        List of comments
        
    Raises:
        HTTPException: If section not found or unauthorized
    """
    # Get the section
    section = db.query(Section).filter(Section.id == section_id).first()
    
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )
    
    # Verify user owns the project
    if section.project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this section"
        )
    
    # Get comments
    comments = CommentService.get_comments(db=db, section_id=section_id)
    
    return comments


@router.get("/slides/{slide_id}/comments", response_model=List[CommentResponse])
async def get_slide_comments(
    slide_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all comments for a slide.
    
    Args:
        slide_id: UUID of the slide
        db: Database session
        current_user: Authenticated user
        
    Returns:
        List of comments
        
    Raises:
        HTTPException: If slide not found or unauthorized
    """
    # Get the slide
    slide = db.query(Slide).filter(Slide.id == slide_id).first()
    
    if not slide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slide not found"
        )
    
    # Verify user owns the project
    if slide.project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this slide"
        )
    
    # Get comments
    comments = CommentService.get_comments(db=db, slide_id=slide_id)
    
    return comments


@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: UUID,
    comment_update: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a comment.
    
    Only the user who created the comment can update it.
    
    Args:
        comment_id: UUID of the comment
        comment_update: Updated comment data
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Updated comment
        
    Raises:
        HTTPException: If comment not found, unauthorized, or operation fails
    """
    # Update comment (service handles authorization)
    comment = CommentService.update_comment(
        db=db,
        comment_id=comment_id,
        user_id=current_user.id,
        comment_text=comment_update.comment_text
    )
    
    return comment


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a comment.
    
    Only the user who created the comment can delete it.
    
    Args:
        comment_id: UUID of the comment
        db: Database session
        current_user: Authenticated user
        
    Raises:
        HTTPException: If comment not found, unauthorized, or operation fails
    """
    # Delete comment (service handles authorization)
    CommentService.delete_comment(
        db=db,
        comment_id=comment_id,
        user_id=current_user.id
    )
    
    return None
