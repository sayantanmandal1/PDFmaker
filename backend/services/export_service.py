"""
Export service for generating Word and PowerPoint documents.
"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from io import BytesIO
import uuid

from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from pptx import Presentation
from pptx.util import Inches as PptxInches, Pt as PptxPt

from models.project import Project
from models.section import Section
from models.slide import Slide
from services.content_service import ContentService


class ExportService:
    """Service for exporting projects as Word or PowerPoint documents."""

    @staticmethod
    def export_word_document(
        db: Session,
        project_id: uuid.UUID
    ) -> tuple[BytesIO, str]:
        """
        Export a Word project as a .docx file.
        
        Args:
            db: Database session
            project_id: UUID of the project to export
            
        Returns:
            Tuple of (BytesIO file stream, filename)
            
        Raises:
            HTTPException: If export fails or content is missing
        """
        try:
            # Retrieve project
            project = db.query(Project).filter(Project.id == project_id).first()
            
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            
            if project.document_type != "word":
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Cannot export non-Word project as Word document"
                )
            
            # Retrieve all sections ordered by position
            sections = ContentService.get_project_sections(db, project_id)
            
            if not sections:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Cannot export project without configured sections"
                )
            
            # Check if content has been generated
            if any(section.content is None or section.content.strip() == "" for section in sections):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Cannot export project without generated content"
                )
            
            # Create Word document
            doc = ExportService._format_word_document(project, sections)
            
            # Save to BytesIO
            file_stream = BytesIO()
            doc.save(file_stream)
            file_stream.seek(0)
            
            # Generate filename
            filename = f"{project.name.replace(' ', '_')}.docx"
            
            return file_stream, filename
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Document export failed"
            )

    @staticmethod
    def export_powerpoint_presentation(
        db: Session,
        project_id: uuid.UUID
    ) -> tuple[BytesIO, str]:
        """
        Export a PowerPoint project as a .pptx file.
        
        Args:
            db: Database session
            project_id: UUID of the project to export
            
        Returns:
            Tuple of (BytesIO file stream, filename)
            
        Raises:
            HTTPException: If export fails or content is missing
        """
        try:
            # Retrieve project
            project = db.query(Project).filter(Project.id == project_id).first()
            
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            
            if project.document_type != "powerpoint":
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Cannot export non-PowerPoint project as PowerPoint presentation"
                )
            
            # Retrieve all slides ordered by position
            slides = ContentService.get_project_slides(db, project_id)
            
            if not slides:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Cannot export project without configured slides"
                )
            
            # Check if content has been generated
            if any(slide.content is None or slide.content.strip() == "" for slide in slides):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Cannot export project without generated content"
                )
            
            # Create PowerPoint presentation
            prs = ExportService._format_powerpoint_presentation(project, slides)
            
            # Save to BytesIO
            file_stream = BytesIO()
            prs.save(file_stream)
            file_stream.seek(0)
            
            # Generate filename
            filename = f"{project.name.replace(' ', '_')}.pptx"
            
            return file_stream, filename
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Document export failed"
            )

    @staticmethod
    def _format_word_document(project: Project, sections: list[Section]) -> Document:
        """
        Format sections into a Word document with proper styling.
        
        Args:
            project: Project object
            sections: List of Section objects ordered by position
            
        Returns:
            Formatted Document object
        """
        doc = Document()
        
        # Set document properties
        core_properties = doc.core_properties
        core_properties.title = project.name
        core_properties.subject = project.topic
        
        # Add document title
        title = doc.add_heading(project.name, level=0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Add topic as subtitle
        topic_para = doc.add_paragraph(project.topic)
        topic_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        topic_para.runs[0].italic = True
        
        # Add spacing
        doc.add_paragraph()
        
        # Add each section
        for section in sections:
            # Add section header as Heading 1
            heading = doc.add_heading(section.header, level=1)
            
            # Add section content as body text
            if section.content:
                # Split content into paragraphs
                paragraphs = section.content.split('\n')
                for para_text in paragraphs:
                    if para_text.strip():  # Only add non-empty paragraphs
                        para = doc.add_paragraph(para_text.strip())
                        # Set font size for body text
                        for run in para.runs:
                            run.font.size = Pt(11)
            
            # Add spacing between sections
            doc.add_paragraph()
        
        return doc

    @staticmethod
    def _format_powerpoint_presentation(project: Project, slides: list[Slide]) -> Presentation:
        """
        Format slides into a PowerPoint presentation with proper styling.
        
        Args:
            project: Project object
            slides: List of Slide objects ordered by position
            
        Returns:
            Formatted Presentation object
        """
        prs = Presentation()
        
        # Set slide dimensions (standard 16:9)
        prs.slide_width = PptxInches(10)
        prs.slide_height = PptxInches(7.5)
        
        # Add title slide
        title_slide_layout = prs.slide_layouts[0]  # Title slide layout
        title_slide = prs.slides.add_slide(title_slide_layout)
        
        title = title_slide.shapes.title
        subtitle = title_slide.placeholders[1]
        
        title.text = project.name
        subtitle.text = project.topic
        
        # Add content slides
        for slide_data in slides:
            # Use title and content layout
            slide_layout = prs.slide_layouts[1]  # Title and content layout
            slide = prs.slides.add_slide(slide_layout)
            
            # Set slide title
            title_shape = slide.shapes.title
            title_shape.text = slide_data.title
            
            # Add content to the content placeholder
            if slide_data.content:
                # Get the content placeholder (usually index 1)
                content_placeholder = slide.placeholders[1]
                text_frame = content_placeholder.text_frame
                text_frame.clear()  # Clear default text
                
                # Split content into paragraphs
                paragraphs = slide_data.content.split('\n')
                
                for i, para_text in enumerate(paragraphs):
                    if para_text.strip():  # Only add non-empty paragraphs
                        if i == 0:
                            # Use the first paragraph in the existing text frame
                            p = text_frame.paragraphs[0]
                        else:
                            # Add new paragraphs
                            p = text_frame.add_paragraph()
                        
                        p.text = para_text.strip()
                        p.level = 0
                        
                        # Set font size
                        for run in p.runs:
                            run.font.size = PptxPt(18)
        
        return prs

