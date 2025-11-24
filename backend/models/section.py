"""
Section model for Word document sections.
"""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from database import Base


class Section(Base):
    """
    Section model representing a section in a Word document.
    """
    __tablename__ = "sections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    header = Column(String(500), nullable=False)
    content = Column(Text, nullable=True)
    position = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="sections")
    refinement_history = relationship("RefinementHistory", back_populates="section", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="section", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="section", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Section(id={self.id}, header={self.header}, position={self.position})>"
