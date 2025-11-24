"""
Comment model for user comments on sections and slides.
"""
from sqlalchemy import Column, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from database import Base


class Comment(Base):
    """
    Comment model representing user comments on content.
    """
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    section_id = Column(UUID(as_uuid=True), ForeignKey("sections.id", ondelete="CASCADE"), nullable=True, index=True)
    slide_id = Column(UUID(as_uuid=True), ForeignKey("slides.id", ondelete="CASCADE"), nullable=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    comment_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Add check constraint to ensure either section_id or slide_id is set, but not both
    __table_args__ = (
        CheckConstraint(
            "(section_id IS NOT NULL AND slide_id IS NULL) OR (section_id IS NULL AND slide_id IS NOT NULL)",
            name="check_section_or_slide_comment"
        ),
    )

    # Relationships
    section = relationship("Section", back_populates="comments")
    slide = relationship("Slide", back_populates="comments")
    user = relationship("User", back_populates="comments")

    def __repr__(self):
        content_type = "section" if self.section_id else "slide"
        content_id = self.section_id if self.section_id else self.slide_id
        return f"<Comment(id={self.id}, {content_type}_id={content_id}, user_id={self.user_id})>"
