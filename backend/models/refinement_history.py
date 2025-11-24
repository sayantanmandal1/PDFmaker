"""
RefinementHistory model for tracking content refinements.
"""
from sqlalchemy import Column, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from database import Base


class RefinementHistory(Base):
    """
    RefinementHistory model representing the history of content refinements.
    """
    __tablename__ = "refinement_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    section_id = Column(UUID(as_uuid=True), ForeignKey("sections.id", ondelete="CASCADE"), nullable=True, index=True)
    slide_id = Column(UUID(as_uuid=True), ForeignKey("slides.id", ondelete="CASCADE"), nullable=True, index=True)
    refinement_prompt = Column(Text, nullable=False)
    previous_content = Column(Text, nullable=True)
    new_content = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Add check constraint to ensure either section_id or slide_id is set, but not both
    __table_args__ = (
        CheckConstraint(
            "(section_id IS NOT NULL AND slide_id IS NULL) OR (section_id IS NULL AND slide_id IS NOT NULL)",
            name="check_section_or_slide"
        ),
    )

    # Relationships
    section = relationship("Section", back_populates="refinement_history")
    slide = relationship("Slide", back_populates="refinement_history")

    def __repr__(self):
        content_type = "section" if self.section_id else "slide"
        content_id = self.section_id if self.section_id else self.slide_id
        return f"<RefinementHistory(id={self.id}, {content_type}_id={content_id})>"
