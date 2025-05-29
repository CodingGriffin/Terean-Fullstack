import json
import logging
import os
import aiofiles
from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.crud.project_crud import update_project
from backend.crud.file_crud import create_file_info, get_files_info_by_project, delete_file_info, get_file_info
from backend.database import get_db
from backend.models.project_model import ProjectDBModel
from backend.schemas.project_schema import ProjectCreate
from backend.schemas.file_schema import FileCreate, FileSchema
from backend.schemas.user_schema import User
from backend.utils.authentication import get_current_user, check_permissions
from backend.utils.project_utils import init_project
from backend.utils.utils import CHUNK_SIZE
from tereancore.utils import generate_time_based_uid
from backend.schemas.additional_models import (
    DisperSettingsModel,
    OptionsModel,
    PickData
)

logger = logging.getLogger(__name__)
project_router = APIRouter(prefix="/project", tags=["Project"])

# Dependency
db_dependency = Depends(get_db)

# Create a global directory for storing project files
GLOBAL_DATA_DIR = os.getenv("MQ_SAVE_DIR", "data")
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
