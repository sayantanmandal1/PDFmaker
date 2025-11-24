"""
Project service for managing document generation projects.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.project import Project
from fastapi import HTTPException, status
import uuid


class ProjectService:
    """Service for handling project CRUD operations."""

    @staticmethod
    def create_project(
        db: Session,
        user_id: uuid.UUID,
        name: str,
        document_type: str,
        topic: str
    ) -> Project:
        """
        Create a new project for a user.
        
        Args:
            db: Database session
            user_id: UUID of the user creating the project
            name: Project name
            document_type: Type of document ('word' or 'powerpoint')
            topic: Main topic or prompt for the document
            
        Returns:
            Created Project object
            
        Raises:
            HTTPException: If project creation fails
        """
        try:
            new_project = Project(
                user_id=user_id,
                name=name,
                document_type=document_type,
                topic=topic,
                status="configuring"
            )
            
            db.add(new_project)
            db.commit()
            db.refresh(new_project)
            
            return new_project
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create project"
            )

    @staticmethod
    def get_user_projects(db: Session, user_id: uuid.UUID) -> List[Project]:
        """
        Retrieve all projects for a specific user.
        
        Args:
            db: Database session
            user_id: UUID of the user
            
        Returns:
            List of Project objects belonging to the user
        """
        try:
            projects = db.query(Project).filter(
                Project.user_id == user_id
            ).order_by(Project.updated_at.desc()).all()
            
            return projects
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve projects"
            )

    @staticmethod
    def get_project(
        db: Session,
        project_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> Project:
        """
        Retrieve a specific project with authorization check.
        
        Args:
            db: Database session
            project_id: UUID of the project
            user_id: UUID of the requesting user
            
        Returns:
            Project object if found and authorized
            
        Raises:
            HTTPException: If project not found or user not authorized
        """
        try:
            project = db.query(Project).filter(
                Project.id == project_id
            ).first()
            
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            
            # Authorization check: ensure the project belongs to the requesting user
            if project.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to access this project"
                )
            
            return project
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve project"
            )

    @staticmethod
    def delete_project(
        db: Session,
        project_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> None:
        """
        Delete a project with authorization check.
        
        Args:
            db: Database session
            project_id: UUID of the project to delete
            user_id: UUID of the requesting user
            
        Raises:
            HTTPException: If project not found, user not authorized, or deletion fails
        """
        try:
            # First get the project with authorization check
            project = ProjectService.get_project(db, project_id, user_id)
            
            # Delete the project (cascade will handle related records)
            db.delete(project)
            db.commit()
            
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete project"
            )

    @staticmethod
    def update_project_status(
        db: Session,
        project_id: uuid.UUID,
        status: str
    ) -> Project:
        """
        Update the status of a project.
        
        Args:
            db: Database session
            project_id: UUID of the project
            status: New status value
            
        Returns:
            Updated Project object
            
        Raises:
            HTTPException: If project not found or update fails
        """
        try:
            project = db.query(Project).filter(
                Project.id == project_id
            ).first()
            
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            
            project.status = status
            db.commit()
            db.refresh(project)
            
            return project
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update project status"
            )
