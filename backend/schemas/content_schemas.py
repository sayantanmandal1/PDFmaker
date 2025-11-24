"""
Pydantic schemas for content-related API requests and responses.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from validators import (
    validate_section_header,
    validate_slide_title,
    validate_comment_text,
    validate_refinement_prompt,
    validate_feedback_type,
    validate_document_type,
    validate_position_list,
    ValidationMixin,
    create_field_with_validation
)


# Section schemas

class SectionConfig(BaseModel, ValidationMixin):
    """Schema for section configuration."""
    header: str = create_field_with_validation(
        min_length=1,
        max_length=500,
        description="Section header text (no line breaks)"
    )
    position: int = Field(
        ..., 
        ge=0, 
        description="Position of the section in the document (starting from 0)"
    )
    
    @validator('header')
    def validate_header(cls, v):
        return validate_section_header(v)


class SectionCreate(BaseModel):
    """Schema for creating a section."""
    header: str = Field(..., min_length=1, max_length=500)
    content: Optional[str] = None
    position: int = Field(..., ge=0)


class SectionUpdate(BaseModel):
    """Schema for updating a section."""
    header: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = None
    position: Optional[int] = Field(None, ge=0)


class SectionResponse(BaseModel):
    """Schema for section response."""
    id: UUID
    project_id: UUID
    header: str
    content: Optional[str]
    position: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Slide schemas

class SlideConfig(BaseModel, ValidationMixin):
    """Schema for slide configuration."""
    title: str = create_field_with_validation(
        min_length=1,
        max_length=500,
        description="Slide title (no line breaks)"
    )
    position: int = Field(
        ..., 
        ge=0, 
        description="Position of the slide in the presentation (starting from 0)"
    )
    
    @validator('title')
    def validate_title(cls, v):
        return validate_slide_title(v)


class SlideCreate(BaseModel):
    """Schema for creating a slide."""
    title: str = Field(..., min_length=1, max_length=500)
    content: Optional[str] = None
    position: int = Field(..., ge=0)


class SlideUpdate(BaseModel):
    """Schema for updating a slide."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = None
    position: Optional[int] = Field(None, ge=0)


class SlideResponse(BaseModel):
    """Schema for slide response."""
    id: UUID
    project_id: UUID
    title: str
    content: Optional[str]
    position: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Configuration schemas

class WordConfigurationRequest(BaseModel, ValidationMixin):
    """Schema for Word document configuration request."""
    sections: List[SectionConfig] = Field(
        ..., 
        min_items=1,
        max_items=50,
        description="List of section configurations (1-50 sections)"
    )
    
    @validator('sections')
    def validate_section_positions(cls, v):
        if not v:
            raise ValueError("At least one section is required")
        
        positions = [section.position for section in v]
        validate_position_list(positions, max_count=50)
        return v


class PowerPointConfigurationRequest(BaseModel, ValidationMixin):
    """Schema for PowerPoint configuration request."""
    slides: List[SlideConfig] = Field(
        ..., 
        min_items=1,
        max_items=100,
        description="List of slide configurations (1-100 slides)"
    )
    
    @validator('slides')
    def validate_slide_positions(cls, v):
        if not v:
            raise ValueError("At least one slide is required")
        
        positions = [slide.position for slide in v]
        validate_position_list(positions, max_count=100)
        return v


class ConfigurationResponse(BaseModel):
    """Schema for configuration response."""
    message: str
    sections: Optional[List[SectionResponse]] = None
    slides: Optional[List[SlideResponse]] = None


class SectionReorderRequest(BaseModel):
    """Schema for reordering sections."""
    section_positions: List[dict] = Field(
        ..., 
        description="List of objects with section_id and position"
    )


# Refinement schemas

class RefinementRequest(BaseModel, ValidationMixin):
    """Schema for content refinement request."""
    prompt: str = create_field_with_validation(
        min_length=5,
        max_length=1000,
        description="Refinement instructions from the user (5-1000 characters)"
    )
    
    @validator('prompt')
    def validate_prompt(cls, v):
        return validate_refinement_prompt(v)


class RefinementHistoryResponse(BaseModel):
    """Schema for refinement history response."""
    id: UUID
    refinement_prompt: str
    previous_content: Optional[str]
    new_content: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Feedback schemas

class FeedbackCreate(BaseModel, ValidationMixin):
    """Schema for creating feedback."""
    feedback_type: str = Field(
        ..., 
        pattern="^(like|dislike)$", 
        description="Type of feedback: 'like' or 'dislike'"
    )
    
    @validator('feedback_type')
    def validate_feedback_type(cls, v):
        return validate_feedback_type(v)


class FeedbackResponse(BaseModel):
    """Schema for feedback response."""
    id: UUID
    section_id: Optional[UUID]
    slide_id: Optional[UUID]
    user_id: UUID
    feedback_type: str
    created_at: datetime

    class Config:
        from_attributes = True


# Comment schemas

class CommentCreate(BaseModel, ValidationMixin):
    """Schema for creating a comment."""
    comment_text: str = create_field_with_validation(
        min_length=1,
        max_length=2000,
        description="Comment text content (1-2000 characters)"
    )
    
    @validator('comment_text')
    def validate_comment_text(cls, v):
        return validate_comment_text(v)


class CommentUpdate(BaseModel, ValidationMixin):
    """Schema for updating a comment."""
    comment_text: str = create_field_with_validation(
        min_length=1,
        max_length=2000,
        description="Updated comment text content (1-2000 characters)"
    )
    
    @validator('comment_text')
    def validate_comment_text(cls, v):
        return validate_comment_text(v)


class CommentResponse(BaseModel):
    """Schema for comment response."""
    id: UUID
    section_id: Optional[UUID]
    slide_id: Optional[UUID]
    user_id: UUID
    comment_text: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Template generation schemas

class TemplateGenerationRequest(BaseModel, ValidationMixin):
    """Schema for AI template generation request."""
    topic: str = create_field_with_validation(
        min_length=1,
        max_length=5000,
        description="Main topic for template generation"
    )
    document_type: str = Field(
        ..., 
        pattern="^(word|powerpoint)$", 
        description="Document type: 'word' or 'powerpoint'"
    )
    
    @validator('document_type')
    def validate_doc_type(cls, v):
        return validate_document_type(v)


class WordTemplateResponse(BaseModel):
    """Schema for Word document template response."""
    headers: List[str] = Field(..., description="List of suggested section headers")


class PowerPointTemplateResponse(BaseModel):
    """Schema for PowerPoint template response."""
    slide_titles: List[str] = Field(..., description="List of suggested slide titles")


class TemplateResponse(BaseModel):
    """Schema for template generation response."""
    document_type: str
    template: WordTemplateResponse | PowerPointTemplateResponse


class TemplateAcceptanceRequest(BaseModel, ValidationMixin):
    """Schema for accepting and modifying a generated template."""
    headers: Optional[List[str]] = Field(
        None, 
        min_items=1,
        max_items=50,
        description="Modified section headers for Word documents (1-50 headers)"
    )
    slide_titles: Optional[List[str]] = Field(
        None, 
        min_items=1,
        max_items=100,
        description="Modified slide titles for PowerPoint presentations (1-100 titles)"
    )
    
    @validator('headers')
    def validate_headers(cls, v):
        if v is not None:
            for header in v:
                validate_section_header(header)
        return v
    
    @validator('slide_titles')
    def validate_slide_titles(cls, v):
        if v is not None:
            for title in v:
                validate_slide_title(title)
        return v
    
    @validator('*')
    def validate_at_least_one_field(cls, v, values):
        """Ensure at least one of headers or slide_titles is provided."""
        if 'headers' in values and 'slide_titles' in values:
            if values.get('headers') is None and values.get('slide_titles') is None:
                raise ValueError("Either headers or slide_titles must be provided")
        return v

