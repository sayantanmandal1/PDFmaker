"""
Custom validators and validation utilities for API endpoints.
"""
import re
from typing import Any, Dict, List, Optional
from pydantic import validator, Field
from uuid import UUID


def validate_password_strength(password: str) -> str:
    """
    Validate password strength requirements.
    
    Requirements:
    - At least 6 characters long
    """
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters long")
    
    return password


def validate_project_name(name: str) -> str:
    """
    Validate project name requirements.
    
    Requirements:
    - Not empty or only whitespace
    - No leading/trailing whitespace
    - Maximum 255 characters
    - No special characters that could cause issues
    """
    name = name.strip()
    
    if not name:
        raise ValueError("Project name cannot be empty")
    
    if len(name) > 255:
        raise ValueError("Project name cannot exceed 255 characters")
    
    # Check for potentially problematic characters
    if re.search(r'[<>:"/\\|?*]', name):
        raise ValueError("Project name contains invalid characters")
    
    return name


def validate_topic_content(topic: str) -> str:
    """
    Validate topic/content requirements.
    
    Requirements:
    - Not empty or only whitespace
    - Reasonable length limits
    """
    topic = topic.strip()
    
    if not topic:
        raise ValueError("Topic cannot be empty")
    
    if len(topic) > 5000:
        raise ValueError("Topic cannot exceed 5000 characters")
    
    return topic


def validate_section_header(header: str) -> str:
    """
    Validate section header requirements.
    
    Requirements:
    - Not empty or only whitespace
    - Maximum 500 characters
    - No line breaks
    """
    header = header.strip()
    
    if not header:
        raise ValueError("Section header cannot be empty")
    
    if len(header) > 500:
        raise ValueError("Section header cannot exceed 500 characters")
    
    if '\n' in header or '\r' in header:
        raise ValueError("Section header cannot contain line breaks")
    
    return header


def validate_slide_title(title: str) -> str:
    """
    Validate slide title requirements.
    
    Requirements:
    - Not empty or only whitespace
    - Maximum 500 characters
    - No line breaks
    """
    title = title.strip()
    
    if not title:
        raise ValueError("Slide title cannot be empty")
    
    if len(title) > 500:
        raise ValueError("Slide title cannot exceed 500 characters")
    
    if '\n' in title or '\r' in title:
        raise ValueError("Slide title cannot contain line breaks")
    
    return title


def validate_comment_text(text: str) -> str:
    """
    Validate comment text requirements.
    
    Requirements:
    - Not empty or only whitespace
    - Maximum 2000 characters
    """
    text = text.strip()
    
    if not text:
        raise ValueError("Comment text cannot be empty")
    
    if len(text) > 2000:
        raise ValueError("Comment text cannot exceed 2000 characters")
    
    return text


def validate_refinement_prompt(prompt: str) -> str:
    """
    Validate refinement prompt requirements.
    
    Requirements:
    - Not empty or only whitespace
    - Maximum 1000 characters
    - Minimum 5 characters for meaningful prompts
    """
    prompt = prompt.strip()
    
    if not prompt:
        raise ValueError("Refinement prompt cannot be empty")
    
    if len(prompt) < 5:
        raise ValueError("Refinement prompt must be at least 5 characters long")
    
    if len(prompt) > 1000:
        raise ValueError("Refinement prompt cannot exceed 1000 characters")
    
    return prompt


def validate_position_list(positions: List[int], max_count: Optional[int] = None) -> List[int]:
    """
    Validate a list of positions for ordering.
    
    Requirements:
    - All positions must be non-negative
    - No duplicate positions
    - Positions should be sequential starting from 0
    """
    if not positions:
        raise ValueError("Position list cannot be empty")
    
    if max_count and len(positions) > max_count:
        raise ValueError(f"Cannot have more than {max_count} positions")
    
    # Check for negative positions
    if any(pos < 0 for pos in positions):
        raise ValueError("Positions must be non-negative")
    
    # Check for duplicates
    if len(positions) != len(set(positions)):
        raise ValueError("Positions must be unique")
    
    # Check for sequential ordering (should start from 0 and be consecutive)
    sorted_positions = sorted(positions)
    expected_positions = list(range(len(positions)))
    
    if sorted_positions != expected_positions:
        raise ValueError("Positions must be sequential starting from 0")
    
    return positions


def validate_uuid_format(uuid_str: str) -> str:
    """
    Validate UUID string format.
    """
    try:
        UUID(uuid_str)
        return uuid_str
    except ValueError:
        raise ValueError("Invalid UUID format")


def validate_email_domain(email: str) -> str:
    """
    Additional email validation beyond basic format.
    
    Requirements:
    - Valid email format (handled by EmailStr)
    - Not from obviously fake domains
    - Reasonable length limits
    """
    if len(email) > 254:  # RFC 5321 limit
        raise ValueError("Email address is too long")
    
    # Split email into local and domain parts
    try:
        local, domain = email.rsplit('@', 1)
    except ValueError:
        raise ValueError("Invalid email format")
    
    # Check local part length (RFC 5321 limit is 64)
    if len(local) > 64:
        raise ValueError("Email local part is too long")
    
    # Check domain part length
    if len(domain) > 253:
        raise ValueError("Email domain is too long")
    
    # Basic domain validation
    if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$', domain):
        raise ValueError("Invalid email domain format")
    
    return email


def validate_document_type(doc_type: str) -> str:
    """
    Validate document type.
    """
    valid_types = ["word", "powerpoint"]
    if doc_type not in valid_types:
        raise ValueError(f"Document type must be one of: {', '.join(valid_types)}")
    
    return doc_type


def validate_feedback_type(feedback_type: str) -> str:
    """
    Validate feedback type.
    """
    valid_types = ["like", "dislike"]
    if feedback_type not in valid_types:
        raise ValueError(f"Feedback type must be one of: {', '.join(valid_types)}")
    
    return feedback_type


class ValidationMixin:
    """
    Mixin class to add common validation methods to Pydantic models.
    """
    
    @validator('*', pre=True)
    def strip_strings(cls, v):
        """Strip whitespace from string fields."""
        if isinstance(v, str):
            return v.strip()
        return v
    
    @validator('*')
    def validate_no_null_bytes(cls, v):
        """Ensure no null bytes in string fields (security measure)."""
        if isinstance(v, str) and '\x00' in v:
            raise ValueError("Null bytes are not allowed")
        return v


def create_field_with_validation(
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    pattern: Optional[str] = None,
    description: Optional[str] = None,
    **kwargs
) -> Field:
    """
    Create a Pydantic Field with common validation parameters.
    """
    field_kwargs = {}
    
    if min_length is not None:
        field_kwargs['min_length'] = min_length
    
    if max_length is not None:
        field_kwargs['max_length'] = max_length
    
    if pattern is not None:
        field_kwargs['regex'] = pattern
    
    if description is not None:
        field_kwargs['description'] = description
    
    # Merge with any additional kwargs
    field_kwargs.update(kwargs)
    
    return Field(**field_kwargs)