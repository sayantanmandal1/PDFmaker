"""
Feedback model for user feedback on sections and slides.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from database import Base


class Feedback(Base):
    """
    Feedback model representing user feedback (like/dislike) on content.
    """
    __tablename__ = "feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    section_id = Column(UUID(as_uuid=True), ForeignKey("sections.id", ondelete="CASCADE"), nullable=True, index=True)
    slide_id = Column(UUID(as_uuid=True), ForeignKey("slides.id", ondelete="CASCADE"), nullable=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    feedback_type = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Add check constraints
    __table_args__ = (
        CheckConstraint(
            "(section_id IS NOT NULL AND slide_id IS NULL) OR (section_id IS NULL AND slide_id IS NOT NULL)",
            name="check_section_or_slide_feedback"
        ),
        CheckConstraint(
            "feedback_type IN ('like', 'dislike')",
            name="check_feedback_type"
        ),
    )

    # Relationships
    section = relationship("Section", back_populates="feedback")
    slide = relationship("Slide", back_populates="feedback")
    user = relationship("User", back_populates="feedback")

    def __repr__(self):
        content_type = "section" if self.section_id else "slide"
        content_id = self.section_id if self.section_id else self.slide_id
        return f"<Feedback(id={self.id}, type={self.feedback_type}, {content_type}_id={content_id})>"
