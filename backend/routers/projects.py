"""
Projects router for project management endpoints.
"""
from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database import get_db
from dependencies.auth import get_current_user
from models.user import User
from models.project import Project
from schemas.project_schemas import (
    ProjectCreate,
    ProjectResponse,
    ProjectListResponse,
    ProjectDeleteResponse,
    GenerationResponse
)
from schemas.content_schemas import (
    WordConfigurationRequest,
    PowerPointConfigurationRequest,
    ConfigurationResponse,
    SectionResponse,
    SlideResponse,
    TemplateGenerationRequest,
    TemplateResponse,
    WordTemplateResponse,
    PowerPointTemplateResponse,
    TemplateAcceptanceRequest
)
from services.project_service import ProjectService
from services.content_service import ContentService
from services.llm_service import LLMService
from services.export_service import ExportService
from exceptions import (
    ValidationException,
    ResourceNotFoundException,
    AuthorizationException,
    ServiceUnavailableException
)

router = APIRouter()


@router.get("", response_model=ProjectListResponse)
async def get_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all projects for the authenticated user.
    
    Returns:
        List of projects belonging to the user
    """
    projects = ProjectService.get_user_projects(db, current_user.id)
    return ProjectListResponse(projects=projects)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new project for the authenticated user.
    
    Args:
        project_data: Project creation data (name, document_type, topic)
        
    Returns:
        Created project object
    """
    project = ProjectService.create_project(
        db=db,
        user_id=current_user.id,
        name=project_data.name,
        document_type=project_data.document_type,
        topic=project_data.topic
    )
    return project


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific project by ID with authorization check.
    
    Args:
        project_id: UUID of the project to retrieve
        
    Returns:
        Project object if found and authorized
        
    Raises:
        404: If project not found
        403: If user not authorized to access the project
    """
    project = ProjectService.get_project(db, project_id, current_user.id)
    return project


@router.delete("/{project_id}", response_model=ProjectDeleteResponse)
async def delete_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a project with authorization check.
    
    Args:
        project_id: UUID of the project to delete
        
    Returns:
        Success message
        
    Raises:
        404: If project not found
        403: If user not authorized to delete the project
    """
    ProjectService.delete_project(db, project_id, current_user.id)
    return ProjectDeleteResponse(message="Project deleted successfully")


@router.put("/{project_id}/configuration", response_model=ConfigurationResponse)
async def configure_project(
    project_id: UUID,
    configuration: WordConfigurationRequest | PowerPointConfigurationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Configure a project with sections (Word) or slides (PowerPoint).
    
    This endpoint handles both Word document and PowerPoint presentation configuration.
    For Word documents, provide a list of section configurations.
    For PowerPoint presentations, provide a list of slide configurations.
    
    Args:
        project_id: UUID of the project to configure
        configuration: Configuration data (sections or slides)
        
    Returns:
        Configuration response with created sections or slides
        
    Raises:
        404: If project not found
        403: If user not authorized to configure the project
        422: If document type doesn't match configuration type
    """
    # Verify project exists and user has access
    project = ProjectService.get_project(db, project_id, current_user.id)
    
    # Handle Word document configuration
    if isinstance(configuration, WordConfigurationRequest):
        if project.document_type != "word":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Cannot configure Word sections for a PowerPoint project"
            )
        
        # Delete existing sections for this project
        existing_sections = ContentService.get_project_sections(db, project_id)
        for section in existing_sections:
            ContentService.delete_section(db, section.id)
        
        # Create new sections
        created_sections = []
        for section_config in configuration.sections:
            section = ContentService.create_section(
                db=db,
                project_id=project_id,
                header=section_config.header,
                content=None,
                position=section_config.position
            )
            created_sections.append(section)
        
        return ConfigurationResponse(
            message="Word document configuration saved successfully",
            sections=created_sections
        )
    
    # Handle PowerPoint configuration
    elif isinstance(configuration, PowerPointConfigurationRequest):
        if project.document_type != "powerpoint":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Cannot configure PowerPoint slides for a Word project"
            )
        
        # Delete existing slides for this project
        existing_slides = ContentService.get_project_slides(db, project_id)
        for slide in existing_slides:
            db.delete(slide)
        db.commit()
        
        # Create new slides
        created_slides = []
        for slide_config in configuration.slides:
            slide = ContentService.create_slide(
                db=db,
                project_id=project_id,
                title=slide_config.title,
                content=None,
                position=slide_config.position
            )
            created_slides.append(slide)
        
        return ConfigurationResponse(
            message="PowerPoint configuration saved successfully",
            slides=created_slides
        )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid configuration type"
        )


@router.post("/{project_id}/generate", response_model=GenerationResponse)
async def generate_content(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate AI content for all sections or slides in a project.
    
    This endpoint triggers the content generation workflow that:
    1. Retrieves all sections (Word) or slides (PowerPoint) for the project
    2. Iterates through each section/slide and generates content using the LLM
    3. Updates each section/slide with the generated content
    4. Updates the project status to indicate generation is complete
    
    Args:
        project_id: UUID of the project to generate content for
        
    Returns:
        Generation response with status and updated project
        
    Raises:
        404: If project not found
        403: If user not authorized to access the project
        422: If project has no configured sections/slides
        503: If LLM service is unavailable
    """
    # Verify project exists and user has access
    project = ProjectService.get_project(db, project_id, current_user.id)
    
    # Initialize LLM service
    try:
        llm_service = LLMService()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service configuration error"
        )
    
    # Handle Word document generation
    if project.document_type == "word":
        sections = ContentService.get_project_sections(db, project_id)
        
        if not sections:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Project has no configured sections. Please configure the document structure first."
            )
        
        # Generate content for each section
        generated_count = 0
        failed_sections = []
        
        for section in sections:
            try:
                # Generate content using LLM
                content = llm_service.generate_section_content(
                    topic=project.topic,
                    section_header=section.header,
                    context=None
                )
                
                # Update section with generated content
                ContentService.update_section(
                    db=db,
                    section_id=section.id,
                    content=content
                )
                
                generated_count += 1
                
            except Exception as e:
                # Log the error and continue with other sections
                failed_sections.append(section.header)
                # In production, you would log this error properly
                continue
        
        # Update project status
        if generated_count == len(sections):
            project = ProjectService.update_project_status(db, project_id, "ready_for_refinement")
            message = f"Successfully generated content for all {generated_count} sections"
        elif generated_count > 0:
            project = ProjectService.update_project_status(db, project_id, "partially_generated")
            message = f"Generated content for {generated_count} of {len(sections)} sections. Failed: {', '.join(failed_sections)}"
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Content generation service temporarily unavailable. Please try again later."
            )
        
        return GenerationResponse(
            status="success" if generated_count == len(sections) else "partial",
            message=message,
            project=project
        )
    
    # Handle PowerPoint generation
    elif project.document_type == "powerpoint":
        slides = ContentService.get_project_slides(db, project_id)
        
        if not slides:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Project has no configured slides. Please configure the presentation structure first."
            )
        
        # Generate content for each slide
        generated_count = 0
        failed_slides = []
        
        for slide in slides:
            try:
                # Generate content using LLM
                content = llm_service.generate_slide_content(
                    topic=project.topic,
                    slide_title=slide.title,
                    context=None
                )
                
                # Update slide with generated content
                ContentService.update_slide(
                    db=db,
                    slide_id=slide.id,
                    content=content
                )
                
                generated_count += 1
                
            except Exception as e:
                # Log the error and continue with other slides
                failed_slides.append(slide.title)
                # In production, you would log this error properly
                continue
        
        # Update project status
        if generated_count == len(slides):
            project = ProjectService.update_project_status(db, project_id, "ready_for_refinement")
            message = f"Successfully generated content for all {generated_count} slides"
        elif generated_count > 0:
            project = ProjectService.update_project_status(db, project_id, "partially_generated")
            message = f"Generated content for {generated_count} of {len(slides)} slides. Failed: {', '.join(failed_slides)}"
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Content generation service temporarily unavailable. Please try again later."
            )
        
        return GenerationResponse(
            status="success" if generated_count == len(slides) else "partial",
            message=message,
            project=project
        )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid document type"
        )


@router.get("/{project_id}/export")
async def export_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export a project as a Word document (.docx) or PowerPoint presentation (.pptx).
    
    This endpoint generates a downloadable file based on the project's document type.
    For Word projects, it creates a .docx file with all sections and content.
    For PowerPoint projects, it creates a .pptx file with all slides and content.
    
    Args:
        project_id: UUID of the project to export
        
    Returns:
        StreamingResponse with the generated file
        
    Raises:
        404: If project not found
        403: If user not authorized to access the project
        422: If project has no content or is not ready for export
        500: If document generation fails
    """
    # Verify project exists and user has access
    project = ProjectService.get_project(db, project_id, current_user.id)
    
    # Export based on document type
    if project.document_type == "word":
        file_stream, filename = ExportService.export_word_document(db, project_id)
        
        return StreamingResponse(
            file_stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    elif project.document_type == "powerpoint":
        file_stream, filename = ExportService.export_powerpoint_presentation(db, project_id)
        
        return StreamingResponse(
            file_stream,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid document type"
        )


@router.post("/{project_id}/generate-template", response_model=TemplateResponse)
async def generate_template(
    project_id: UUID,
    request: TemplateGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate an AI-suggested document structure template.
    
    This endpoint uses the LLM to generate a suggested document structure
    based on the provided topic and document type. For Word documents,
    it generates section headers. For PowerPoint presentations, it generates
    slide titles.
    
    Args:
        project_id: UUID of the project to generate template for
        request: Template generation request with topic and document type
        
    Returns:
        Template response with suggested structure
        
    Raises:
        404: If project not found
        403: If user not authorized to access the project
        422: If document type doesn't match project type
        503: If LLM service is unavailable
    """
    # Verify project exists and user has access
    project = ProjectService.get_project(db, project_id, current_user.id)
    
    # Verify document type matches project
    if request.document_type != project.document_type:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Document type '{request.document_type}' doesn't match project type '{project.document_type}'"
        )
    
    # Initialize LLM service
    try:
        llm_service = LLMService()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service configuration error"
        )
    
    try:
        # Generate template using LLM
        template_items = llm_service.generate_template(
            topic=request.topic,
            document_type=request.document_type
        )
        
        # Format response based on document type
        if request.document_type == "word":
            template = WordTemplateResponse(headers=template_items)
        else:  # powerpoint
            template = PowerPointTemplateResponse(slide_titles=template_items)
        
        return TemplateResponse(
            document_type=request.document_type,
            template=template
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Template generation service temporarily unavailable. Please try again later."
        )


@router.post("/{project_id}/accept-template", response_model=ConfigurationResponse)
async def accept_template(
    project_id: UUID,
    request: TemplateAcceptanceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Accept and apply an AI-generated template to the project configuration.
    
    This endpoint takes the template structure (either modified or as-is from
    the generate-template endpoint) and applies it to the project by creating
    the appropriate sections or slides.
    
    Args:
        project_id: UUID of the project to configure
        request: Template acceptance request with headers or slide titles
        
    Returns:
        Configuration response with created sections or slides
        
    Raises:
        404: If project not found
        403: If user not authorized to access the project
        422: If template data doesn't match project type or is invalid
    """
    # Verify project exists and user has access
    project = ProjectService.get_project(db, project_id, current_user.id)
    
    # Handle Word document template acceptance
    if project.document_type == "word":
        if not request.headers:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Headers are required for Word document template"
            )
        
        # Delete existing sections for this project
        existing_sections = ContentService.get_project_sections(db, project_id)
        for section in existing_sections:
            ContentService.delete_section(db, section.id)
        
        # Create new sections from template
        created_sections = []
        for position, header in enumerate(request.headers):
            section = ContentService.create_section(
                db=db,
                project_id=project_id,
                header=header,
                content=None,
                position=position
            )
            created_sections.append(section)
        
        return ConfigurationResponse(
            message="Word document template applied successfully",
            sections=created_sections
        )
    
    # Handle PowerPoint template acceptance
    elif project.document_type == "powerpoint":
        if not request.slide_titles:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Slide titles are required for PowerPoint template"
            )
        
        # Delete existing slides for this project
        existing_slides = ContentService.get_project_slides(db, project_id)
        for slide in existing_slides:
            db.delete(slide)
        db.commit()
        
        # Create new slides from template
        created_slides = []
        for position, title in enumerate(request.slide_titles):
            slide = ContentService.create_slide(
                db=db,
                project_id=project_id,
                title=title,
                content=None,
                position=position
            )
            created_slides.append(slide)
        
        return ConfigurationResponse(
            message="PowerPoint template applied successfully",
            slides=created_slides
        )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid document type"
        )