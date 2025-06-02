import json
import logging
import os
from datetime import datetime
from enum import Enum
from typing import List, Optional

import aiofiles
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Query, Request, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import desc, asc, not_
from sqlalchemy.orm import Session
from tereancore.utils import generate_time_based_uid

from config import settings
from crud.file_crud import create_file_info, get_files_info_by_project, delete_file_info, get_file_info
from crud.project_crud import update_project, create_project, get_project
from crud.sgy_file_crud import create_sgy_file_info
from database import get_db
from models.project_model import ProjectDBModel
from schemas.additional_models import (
    DisperSettingsModel,
    OptionsModel,
    PickData
)
from schemas.file_schema import FileCreate, FileSchema
from schemas.project_schema import ProjectCreate, Project, ProjectUpdate
from schemas.sgy_file_schema import SgyFileCreate
from schemas.user_schema import User
from utils.authentication import get_current_user, check_permissions
from utils.custom_types.Priority import Priority
from utils.custom_types.ProjectStatus import ProjectStatus
from utils.project_utils import init_project
from utils.utils import CHUNK_SIZE, validate_id

logger = logging.getLogger(__name__)
project_router = APIRouter(prefix="/project", tags=["Project"])

# Dependency
db_dependency = Depends(get_db)

# Create a global directory for storing project files
GLOBAL_DATA_DIR = settings.MQ_SAVE_DIR
GLOBAL_PROJECT_FILES_DIR = os.path.join(GLOBAL_DATA_DIR, "ProjectFiles")
os.makedirs(GLOBAL_PROJECT_FILES_DIR, exist_ok=True)


# region disper-settings endpoint 
@project_router.get("/{project_id}/disper-settings")
async def get_disper_settings(
        project_id: str,
        db: Session = db_dependency,
        current_user: User = Depends(get_current_user),
) -> DisperSettingsModel:
    check_permissions(current_user, 1)
    project = init_project(project_id=project_id, db=db)
    return json.loads(project.disper_settings)


@project_router.post("/{project_id}/disper-settings")
async def save_disper_settings(
        project_id: str,
        model: DisperSettingsModel,
        db: Session = db_dependency,
        current_user: User = Depends(get_current_user),
):
    check_permissions(current_user, 1)
    project = init_project(project_id=project_id, db=db)
    project_update = ProjectCreate(**project.model_dump())
    project_update.disper_settings = json.dumps(model.model_dump())
    update_project(db=db, project_id=project_id, project=project_update)
    return {"status": "success"}


# endregion

# region pick options endpoint
@project_router.get("/{project_id}/options")
async def get_options(
        project_id: str,
        db: Session = db_dependency,
        current_user: User = Depends(get_current_user),
):
    logger.info(f"Hit options endpoint for project_id {project_id}.")
    check_permissions(current_user, 1)
    logger.info(f"Passed permissions check.")
    project = init_project(project_id=project_id, db=db)
    response_data = {}
    response_data["geometry"] = json.loads(project.geometry)
    response_data["records"] = json.loads(project.record_options)
    response_data["plotLimits"] = json.loads(project.plot_limits)

    return response_data


@project_router.post("/{project_id}/options")
async def save_options(
        project_id: str,
        options: OptionsModel,
        db: Session = db_dependency,
        current_user: User = Depends(get_current_user),
):
    check_permissions(current_user, 1)
    logger.info(f"Options: {options}")
    project = init_project(project_id=project_id, db=db)
    project_update = ProjectCreate(**project.model_dump())
    project_update.geometry = json.dumps(options.geometry)
    project_update.record_options = json.dumps(options.records)
    logger.info(f"options.plotLimits: {options.plotLimits}")
    project_update.plot_limits = json.dumps(options.plotLimits)
    update_project(db=db, project_id=project_id, project=project_update)
    return {"status": "success"}


# endregion

# region pick data endpoint
@project_router.get("/{project_id}/picks")
async def get_picks(
        project_id: str,
        db: Session = db_dependency,
        current_user: User = Depends(get_current_user),
):
    check_permissions(current_user, 1)
    project = init_project(project_id=project_id, db=db)
    return json.loads(project.picks)


@project_router.post("/{project_id}/picks")
async def save_picks(
        project_id: str,
        picks: List[PickData],
        db: Session = db_dependency,
        current_user: User = Depends(get_current_user),
):
    check_permissions(current_user, 1)
    project = init_project(project_id=project_id, db=db)
    project_update = ProjectCreate(**project.model_dump())
    project_update.picks = json.dumps(picks)
    update_project(db=db, project_id=project_id, project=project_update)
    return {"status": "success", "count": len(picks)}


# endregion


@project_router.get("/{project_id}/project-data")
async def get_project_data(
        project_id: str,
        db: Session = db_dependency,
        current_user: User = Depends(get_current_user),
):
    check_permissions(current_user, 1)
    try:
        project = init_project(project_id=project_id, db=db)
        return {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
            "disper_settings": json.loads(project.disper_settings),
            "geometry": json.loads(project.geometry),
            "record_options": json.loads(project.record_options),
            "plot_limits": json.loads(project.plot_limits),
            "picks": json.loads(project.picks)
        }
    except Exception as e:
        logger.error(f"Error getting project data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting project data: {str(e)}")


# region file management endpoints
@project_router.post("/{project_id}/upload-files", status_code=status.HTTP_201_CREATED)
async def upload_files_to_project(
        project_id: str,
        files: List[UploadFile] = File(...),
        db: Session = db_dependency,
        current_user: User = Depends(get_current_user)
):
    """
    Upload one or more files to a specific project.
    Requires authentication.
    """
    check_permissions(current_user, 1)

    # Validate project_id to prevent path traversal
    if not validate_id(project_id):
        raise HTTPException(status_code=400, detail="Invalid project ID")

    # Get the dir to write to (Adding project ID)
    write_dir = os.path.join(GLOBAL_PROJECT_FILES_DIR, project_id)

    # Ensure the directory exists
    os.makedirs(write_dir, exist_ok=True)
    try:
        result_files = []

        for file in files:
            try:
                # Get original filename
                original_filename = file.filename
                if not original_filename:
                    continue  # Skip files with no name

                # Get file extension and mime type
                file_extension = original_filename.split('.')[-1] if '.' in original_filename else ''
                mime_type = file.content_type or 'application/octet-stream'

                # Generate unique filename
                file_id = generate_time_based_uid()
                unique_filename = f"{file_id}.{file_extension}"
                file_path = os.path.join(write_dir, unique_filename)

                # Save the file
                async with aiofiles.open(file_path, 'wb') as f:
                    while chunk := await file.read(CHUNK_SIZE):
                        await f.write(chunk)

                # Create FileCreate object
                file_create = FileCreate(
                    id=file_id,
                    original_name=original_filename,
                    path=file_path,
                    size=os.path.getsize(file_path),
                    mime_type=mime_type,
                    file_extension=file_extension,
                    project_id=project_id,
                    upload_date=datetime.now()
                )

                # Add it to the DB
                db_file = create_file_info(db=db, file=file_create)

                result_files.append({
                    "id": file_create.id,
                    "original_name": file_create.original_name,
                    "path": file_create.path,
                    "size": file_create.size,
                    "upload_date": file_create.upload_date.isoformat(),
                    "mime_type": file_create.mime_type,
                    "file_extension": file_create.file_extension
                })
                logger.info(f"Successfully saved file: {original_filename} to {file_path} with ID: {file_id}")

            except Exception as file_error:
                logger.error(f"Error processing file {file.filename}: {str(file_error)}")
                # Continue with other files

        if not result_files:
            raise HTTPException(status_code=400, detail="No files were successfully uploaded")

        return {
            "status": "success",
            "message": f"{len(result_files)} file(s) uploaded successfully",
            "file_infos": result_files
        }
    except Exception as e:
        logger.error(f"Error in upload_files_to_project: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading files: {str(e)}")


@project_router.get("/{project_id}/files", response_model=List[FileSchema])
async def get_project_files(
        project_id: str,
        skip: int = 0,
        limit: int = 100,
        db: Session = db_dependency,
        current_user: User = Depends(get_current_user)
):
    """
    Get a list of files associated with a project.
    Requires authentication.
    """
    check_permissions(current_user, 1)

    try:
        files = get_files_info_by_project(db=db, project_id=project_id, skip=skip, limit=limit)
        return files
    except Exception as e:
        logger.error(f"Error getting project files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting project files: {str(e)}")


@project_router.delete("/{project_id}/files/{file_id}")
async def delete_project_file(
        project_id: str,
        file_id: str,
        db: Session = db_dependency,
        current_user: User = Depends(get_current_user)
):
    """
    Delete a file from a project.
    Requires authentication.
    """
    check_permissions(current_user, 1)

    try:
        # Get file info to check if it exists and belongs to the project
        file_info = get_files_info_by_project(db=db, project_id=project_id)
        file_to_delete = next((f for f in file_info if f.id == file_id), None)

        if not file_to_delete:
            raise HTTPException(
                status_code=404,
                detail=f"File with ID {file_id} not found in project {project_id}"
            )

        # Delete the physical file
        try:
            if os.path.exists(file_to_delete.path):
                os.remove(file_to_delete.path)
        except Exception as e:
            logger.error(f"Error deleting physical file {file_to_delete.path}: {str(e)}")
            # Continue with DB deletion even if physical file deletion fails

        # Delete from database
        if delete_file_info(db=db, file_id=file_id):
            return {"status": "success", "message": f"File {file_id} deleted successfully"}
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete file {file_id} from database"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting project file: {str(e)}")


@project_router.get("/{project_id}/files/{file_id}/download")
async def download_project_file(
        project_id: str,
        file_id: str,
        db: Session = db_dependency,
        current_user: User = Depends(get_current_user)
):
    """
    Download a file from a project.
    Requires authentication.
    """
    check_permissions(current_user, 1)

    try:
        # Get file info to check if it exists and belongs to the project
        file_info = get_file_info(db=db, file_id=file_id)

        if not file_info:
            raise HTTPException(
                status_code=404,
                detail=f"File with ID {file_id} not found"
            )

        if file_info.project_id != project_id:
            raise HTTPException(
                status_code=403,
                detail=f"File {file_id} does not belong to project {project_id}"
            )

        if not os.path.exists(file_info.path):
            raise HTTPException(
                status_code=404,
                detail=f"File {file_id} exists in database but not found on disk"
            )

        async def file_generator():
            async with aiofiles.open(file_info.path, 'rb') as f:
                while chunk := await f.read(CHUNK_SIZE):
                    yield chunk

        return StreamingResponse(
            file_generator(),
            media_type=file_info.mime_type,
            headers={
                "Content-Disposition": f'attachment; filename="{file_info.original_name}"'
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading project file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error downloading project file: {str(e)}")


# endregion

# region project management endpoints
@project_router.get("/{project_id}", response_model=Project)
async def get_project_by_id(
        project_id: str,
        db: Session = db_dependency,
        current_user: User = Depends(get_current_user)
):
    """
    Get a single project by ID.
    Requires authentication.
    """
    check_permissions(current_user, 1)

    try:
        project = get_project(db, project_id)
        if not project:
            raise HTTPException(
                status_code=404,
                detail=f"Project with ID {project_id} not found"
            )
        return Project.from_db(project)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting project: {str(e)}")


@project_router.patch("/{project_id}", response_model=Project)
async def update_project_fields(
    project_id: str,
    project_update: ProjectUpdate,
    db: Session = db_dependency,
    current_user: User = Depends(get_current_user)
):
    """
    Update specific fields of a project.
    Requires authentication.
    """
    check_permissions(current_user, 1)
    
    try:
        project = get_project(db, project_id)
        if not project:
            raise HTTPException(
                status_code=404,
                detail=f"Project with ID {project_id} not found"
            )
        
        # Use the project CRUD update function which includes client_id validation
        project_create = ProjectCreate(**project_update.model_dump(exclude_unset=True))
        
        try:
            updated_project = update_project(db=db, project_id=project_id, project=project_create)
        except ValueError as e:
            # Handle client not found error
            raise HTTPException(status_code=400, detail=str(e))
        
        return Project.from_db(updated_project)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating project: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating project: {str(e)}")


@project_router.patch("/{project_id}/client")
async def update_project_client(
    project_id: str,
    client_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update or remove the client associated with a project."""
    check_permissions(current_user, 1)
    
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=404,
            detail=f"Project with ID {project_id} not found"
        )
    
    if client_id is not None:
        # Verify client exists
        from crud.client_crud import get_client
        client = get_client(db, client_id)
        if not client:
            raise HTTPException(
                status_code=404,
                detail=f"Client with ID {client_id} not found"
            )
    
    project.client_id = client_id
    db.commit()
    db.refresh(project)
    
    return {"detail": f"Project client updated successfully", "client_id": client_id}


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class SortField(str, Enum):
    NAME = "name"
    STATUS = "status"
    PRIORITY = "priority"
    SURVEY_DATE = "survey_date"
    RECEIVED_DATE = "received_date"


class ProjectListResponse(BaseModel):
    items: List[Project]
    total: int
    page: int
    size: int
    pages: int


@project_router.get("/", response_model=ProjectListResponse)
async def get_all_projects(
        skip: int = 0,
        limit: int = 100,
        status: Optional[List[ProjectStatus]] = Query(None, description="Filter by project status(es)"),
        not_status: Optional[List[ProjectStatus]] = Query(None,
                                                          description="Filter out projects with these status(es)"),
        priority: Optional[List[Priority]] = Query(None, description="Filter by project priority(ies)"),
        not_priority: Optional[List[Priority]] = Query(None,
                                                       description="Filter out projects with these priority(ies)"),
        name_search: Optional[str] = None,
        survey_date_start: Optional[datetime] = Query(None, description="Filter by survey date (inclusive)"),
        survey_date_end: Optional[datetime] = Query(None, description="Filter by survey date (inclusive)"),
        received_date_start: Optional[datetime] = Query(None, description="Filter by received date (inclusive)"),
        received_date_end: Optional[datetime] = Query(None, description="Filter by received date (inclusive)"),
        sort_by: SortField = SortField.NAME,
        sort_order: SortOrder = SortOrder.ASC,
        db: Session = db_dependency,
        current_user: User = Depends(get_current_user)
):
    """
    Get a list of all projects with pagination, filtering, and sorting.
    Requires authentication.
    
    Parameters:
    - skip: Number of records to skip (for pagination)
    - limit: Maximum number of records to return
    - status: Filter by project status(es) (can provide multiple)
    - not_status: Filter out projects with these status(es) (can provide multiple)
    - priority: Filter by project priority(ies) (can provide multiple)
    - not_priority: Filter out projects with these priority(ies) (can provide multiple)
    - name_search: Search in project names (case-insensitive partial match)
    - survey_date_start: Filter by survey date (inclusive)
    - survey_date_end: Filter by survey date (inclusive)
    - received_date_start: Filter by received date (inclusive)
    - received_date_end: Filter by received date (inclusive)
    - sort_by: Field to sort by (name, status, priority, survey_date, received_date)
    - sort_order: Sort order (asc or desc)
    """
    check_permissions(current_user, 1)

    try:
        # Start with base query
        query = db.query(ProjectDBModel)

        # Apply status filters
        if status:
            query = query.filter(ProjectDBModel.status.in_(status))
        if not_status:
            query = query.filter(not_(ProjectDBModel.status.in_(not_status)))

        # Apply priority filters
        if priority:
            query = query.filter(ProjectDBModel.priority.in_(priority))
        if not_priority:
            query = query.filter(not_(ProjectDBModel.priority.in_(not_priority)))

        # Apply name search
        if name_search:
            query = query.filter(ProjectDBModel.name.ilike(f"%{name_search}%"))

        # Apply date range filters
        if survey_date_start:
            query = query.filter(ProjectDBModel.survey_date >= survey_date_start)
        if survey_date_end:
            query = query.filter(ProjectDBModel.survey_date <= survey_date_end)
        if received_date_start:
            query = query.filter(ProjectDBModel.received_date >= received_date_start)
        if received_date_end:
            query = query.filter(ProjectDBModel.received_date <= received_date_end)

        # Get total count before pagination
        total = query.count()

        # Apply sorting
        sort_column = getattr(ProjectDBModel, sort_by.value)
        if sort_order == SortOrder.DESC:
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        # Apply pagination
        query = query.offset(skip).limit(limit)

        # Execute query
        projects = query.all()

        # Calculate pagination info
        page = (skip // limit) + 1
        pages = (total + limit - 1) // limit  # Ceiling division

        return ProjectListResponse(
            items=[Project.from_db(project) for project in projects],
            total=total,
            page=page,
            size=limit,
            pages=pages
        )

    except Exception as e:
        logger.error(f"Error getting projects: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting projects: {str(e)}")


@project_router.post("/create", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_new_project(
        request: Request,
        project_data: str = Form(...),  # Project data as JSON string in form data
        project_id: Optional[str] = Query(None),
        client_id: Optional[int] = Form(None),  # Add client_id parameter
        sgy_files: List[UploadFile] = File(None),
        additional_files: List[UploadFile] = File(None),
        db: Session = db_dependency,
        current_user: User = Depends(get_current_user)
):
    """
    Create a new project with optional project ID, client association, and file uploads.
    If project_id is not provided, one will be generated.
    Requires authentication.
    
    Parameters:
    - project_data: Project creation data as JSON string
    - project_id: Optional project ID (will be generated if not provided)
    - client_id: Optional client ID to associate with the project
    - sgy_files: Optional list of SEG-Y files to upload
    - additional_files: Optional list of additional files to upload
    """
    check_permissions(current_user, 1)

    # Add detailed logging
    logger.info("=== CREATE PROJECT ENDPOINT ===")
    logger.info(f"Request URL: {request.url}")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Content-Type header: {request.headers.get('content-type', 'Not found')}")
    logger.info(f"Query params - project_id: {project_id}")
    logger.info(f"Form params - client_id: {client_id}")

    # Parse the project data from JSON string
    try:
        logger.info(f"Raw project data:\n{project_data}")
        project_dict = json.loads(project_data)
        
        # Add client_id if provided
        if client_id:
            project_dict["client_id"] = client_id
            
        logger.info(f"Parsed project data: {project_dict}")
        project = ProjectCreate(**project_dict)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in project_data: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON in project_data")
    except Exception as e:
        logger.error(f"Error creating ProjectCreate from data: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid project data: {str(e)}")

    # Log the received project data
    logger.info(f"Created ProjectCreate object: {project.model_dump()}")

    # Log file info
    logger.info(f"Number of sgy_files: {len(sgy_files) if sgy_files else 0}")
    logger.info(f"Number of additional_files: {len(additional_files) if additional_files else 0}")

    try:
        # Generate project ID if not provided
        if not project_id:
            project_id = generate_time_based_uid()
            logger.warning(f"Generated project ID: {project_id}")
        else:
            # Validate provided project_id to prevent path traversal
            if not validate_id(project_id):
                raise HTTPException(status_code=400, detail="Invalid project ID format")

        # Check if project with this ID already exists
        existing_project = get_project(db, project_id)
        if existing_project:
            raise HTTPException(
                status_code=400,
                detail=f"Project with ID {project_id} already exists"
            )

        # Create project directory
        project_dir = os.path.join(GLOBAL_PROJECT_FILES_DIR, project_id)
        os.makedirs(project_dir, exist_ok=True)

        # Create project in database - pass ProjectCreate with the ID set
        project_data = project.model_dump()
        project_data["id"] = project_id
        project_with_id = ProjectCreate(**project_data)
        
        try:
            db_project = create_project(db=db, project=project_with_id)
        except ValueError as e:
            # Handle client not found error
            raise HTTPException(status_code=400, detail=str(e))

        # Handle SEG-Y file uploads
        if sgy_files:
            # Get project dir and ensure it exists.
            sgy_project_dir = os.path.join(settings.MQ_SAVE_DIR, "SGYFiles", project_id)
            os.makedirs(sgy_project_dir, exist_ok=True)

            # Parse existing record_options from the project
            record_options = json.loads(project.record_options) if project.record_options else []
            updated_record_options = []
            file_index = 0

            for file in sgy_files:
                try:
                    # Get original filename
                    logger.info(f"Processing sgy file {file}")
                    original_filename = file.filename
                    if not original_filename:
                        continue
                    logger.info(f"Got original filename {original_filename}")

                    # Generate unique filename
                    file_id = generate_time_based_uid()
                    file_extension = original_filename.split('.')[-1] if '.' in original_filename else 'sgy'
                    unique_filename = f"{file_id}.{file_extension}"
                    file_path = os.path.join(sgy_project_dir, unique_filename)
                    logger.info(f"Generated unique filename {unique_filename} and file path {file_path}")

                    # Save the file
                    async with aiofiles.open(file_path, 'wb') as f:
                        while chunk := await file.read(CHUNK_SIZE):
                            await f.write(chunk)
                    logger.info(f"Successfully saved file to {file_path}")

                    # Create SgyFileCreate object
                    sgy_file_create = SgyFileCreate(
                        id=file_id,
                        original_name=original_filename,
                        path=file_path,
                        size=os.path.getsize(file_path),
                        type=file_extension.upper(),
                        project_id=project_id,
                        upload_date=datetime.now()
                    )
                    logger.info(f"Creating db entry with data {sgy_file_create}")

                    # Add it to the DB
                    create_sgy_file_info(db=db, sgy_file=sgy_file_create)
                    logger.info(f"Successfully saved SEG-Y file: {original_filename} to {file_path} with ID: {file_id}")

                    # Update record_options with the generated ID
                    if file_index < len(record_options):
                        # Update existing record option with the generated ID
                        record_option = record_options[file_index]
                        record_option['id'] = file_id
                        updated_record_options.append(record_option)
                    else:
                        # Create new record option if not provided in initial data
                        updated_record_options.append({
                            'id': file_id,
                            'enabled': False,
                            'weight': 100,
                            'fileName': original_filename
                        })

                    file_index += 1

                except Exception as file_error:
                    logger.error(f"Error processing SEG-Y file {file.filename}: {str(file_error)}")
                    continue

            # Update the project's record_options with the file IDs
            if updated_record_options:
                logger.info(f"Updating project record_options with file IDs: {updated_record_options}")
                db_project.record_options = json.dumps(updated_record_options)
                db.commit()
                db.refresh(db_project)
                logger.info("Successfully updated project record_options with file IDs")

        # Handle additional file uploads
        if additional_files:
            for file in additional_files:
                try:
                    # Get original filename
                    original_filename = file.filename
                    if not original_filename:
                        continue

                    # Get file extension and mime type
                    file_extension = original_filename.split('.')[-1] if '.' in original_filename else ''
                    mime_type = file.content_type or 'application/octet-stream'

                    # Generate unique filename
                    file_id = generate_time_based_uid()
                    unique_filename = f"{file_id}.{file_extension}"
                    file_path = os.path.join(project_dir, unique_filename)

                    # Save the file
                    async with aiofiles.open(file_path, 'wb') as f:
                        while chunk := await file.read(CHUNK_SIZE):
                            await f.write(chunk)

                    # Create FileCreate object
                    file_create = FileCreate(
                        id=file_id,
                        original_name=original_filename,
                        path=file_path,
                        size=os.path.getsize(file_path),
                        mime_type=mime_type,
                        file_extension=file_extension,
                        project_id=project_id,
                        upload_date=datetime.now()
                    )

                    # Add it to the DB
                    create_file_info(db=db, file=file_create)
                    logger.info(
                        f"Successfully saved additional file: {original_filename} to {file_path} with ID: {file_id}")

                except Exception as file_error:
                    logger.error(f"Error processing additional file {file.filename}: {str(file_error)}")
                    continue

        logger.info("Getting return data from db")
        ret_project = Project.from_db(db_project)
        logger.info(f"Return data:\n{ret_project}")
        return ret_project

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error creating project: {str(e)}")

# endregion
