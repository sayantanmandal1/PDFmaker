"""
Pydantic schemas for project-related API requests and responses.
"""
from pydantic import BaseModel, Field, validator
from typing import Literal, Optional
from datetime import datetime
from uuid import UUID
from validators import (
    validate_project_name,
    validate_topic_content,
    validate_document_type,
    ValidationMixin,
    create_field_with_validation
)


class ProjectCreate(BaseModel, ValidationMixin):
    """Schema for creating a new project."""
    name: str = create_field_with_validation(
        min_length=1,
        max_length=255,
        description="Project name (no special characters: <>:\"/\\|?*)"
    )
    document_type: Literal["word", "powerpoint"] = Field(
        ..., 
        description="Type of document to generate: 'word' or 'powerpoint'"
    )
    topic: str = create_field_with_validation(
        min_length=1,
        max_length=5000,
        description="Main topic or prompt for the document"
    )
    
    @validator('name')
    def validate_name(cls, v):
        return validate_project_name(v)
    
    @validator('topic')
    def validate_topic(cls, v):
        return validate_topic_content(v)
    
    @validator('document_type')
    def validate_doc_type(cls, v):
        return validate_document_type(v)


class ProjectResponse(BaseModel):
    """Schema for project response."""
    id: UUID
    user_id: UUID
    name: str
    document_type: str
    topic: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """Schema for list of projects response."""
    projects: list[ProjectResponse]


class ProjectDeleteResponse(BaseModel):
    """Schema for project deletion response."""
    message: str


class GenerationResponse(BaseModel):
    """Schema for content generation response."""
    status: str
    message: str
    project: ProjectResponse
