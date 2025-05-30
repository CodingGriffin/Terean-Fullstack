import logging
import os
import aiofiles
import tempfile
import zipfile

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from fastapi.responses import StreamingResponse

from tereancore.utils import generate_time_based_uid

from backend.database import get_db
from backend.crud.sgy_file_crud import (
    get_sgy_file_info,
    get_sgy_files_info,
    get_sgy_files_info_by_project,
    create_sgy_file_info,
    delete_sgy_file_info,
)
from backend.schemas.sgy_file_schema import SgyFile, SgyFileCreate
from backend.schemas.user_schema import User
from backend.utils.authentication import get_current_user, check_permissions
from backend.utils.utils import CHUNK_SIZE

logger = logging.getLogger(__name__)
sgy_file_router = APIRouter(prefix="/sgy-files", tags=["SEG-Y Files"])

# Dependency
db_dependency = Depends(get_db)

# Create a global directory for storing SGY files
load_dotenv("backend/settings/.env", override=True)
GLOBAL_DATA_DIR = os.getenv("MQ_SAVE_DIR", "data")
GLOBAL_SGY_FILES_DIR = os.path.join(GLOBAL_DATA_DIR, "SGYFiles")
os.makedirs(GLOBAL_SGY_FILES_DIR, exist_ok=True)


@sgy_file_router.get("/", response_model=List[SgyFile])
async def get_sgy_files_info_endpoint(
        skip: int = 0,
        limit: int = 100,
        db: Session = db_dependency,
        current_user: User = Depends(get_current_user)
):
    """
    Retrieve all SEG-Y files data with pagination. Optional filter by project ID.
    Requires authentication.
    """
    check_permissions(current_user, 1)
    query_return = get_sgy_files_info(db, skip=skip, limit=limit)
    return query_return


@sgy_file_router.get("/{sgy_file_id}", response_model=SgyFile)
async def read_sgy_file_endpoint(
        sgy_file_id: str,
        db: Session = db_dependency,
        current_user: User = Depends(get_current_user)
):
    """
    Retrieve a specific SEG-Y file by ID.
    Requires authentication.
    """
    check_permissions(current_user, 1)
    db_sgy_file = get_sgy_file_info(db, sgy_file_id)
    if db_sgy_file is None:
        raise HTTPException(status_code=404, detail="SEG-Y file not found")
    return db_sgy_file


@sgy_file_router.get("/project/{project_id}", response_model=List[SgyFile])
async def read_project_sgy_files_endpoint(
        project_id: str,
        skip: int = 0,
        limit: int = 100,
        db: Session = db_dependency,
        current_user: User = Depends(get_current_user)
):
    """
    Retrieve all SEG-Y files for a specific project.
    Requires authentication.
    """
    check_permissions(current_user, 1)
    return get_sgy_files_info_by_project(db, project_id, skip=skip, limit=limit)


@sgy_file_router.post("/project/{project_id}/upload", status_code=status.HTTP_201_CREATED)
async def upload_sgy_files_to_project_endpoint(
        project_id: str,
        files: List[UploadFile] = File(...),
        db: Session = db_dependency,
        current_user: User = Depends(get_current_user)
):
    """
    Upload one or more sgy files to a specific project.
    Requires authentication.
    """
    check_permissions(current_user, 1)

    logger.info(f"=== SGY File Upload START ===")
    logger.info(f"Project ID: {project_id}")
    logger.info(f"Number of files: {len(files)}")
    logger.info(f"User: {current_user.username}")

    # Get the dir to write to (Adding project ID)
    write_dir = os.path.join(GLOBAL_SGY_FILES_DIR, project_id)

    # Ensure the directory exists
    os.makedirs(write_dir, exist_ok=True)
    logger.info(f"Write directory: {write_dir}")
    
    try:
        result_files = []

        for i, sgy_file in enumerate(files):
            try:
                # Get original filename
                original_filename = sgy_file.filename
                logger.info(f"Processing file {i}: {original_filename}")
                
                if not original_filename:
                    logger.warning(f"File {i} has no name, skipping")
                    continue  # Skip files with no name

                # Assign the file a unique id
                file_id = generate_time_based_uid()
                logger.info(f"Generated file ID: {file_id}")

                file_extension = original_filename.split('.')[-1] if '.' in original_filename else 'sgy'
                unique_filename = f"{file_id}.{file_extension}"
                file_path = os.path.join(write_dir, unique_filename)

                logger.info(f"Saving file to: {file_path}")

                # Save the file
                async with aiofiles.open(file_path, 'wb') as f:
                    while chunk := await sgy_file.read(CHUNK_SIZE):
                        await f.write(chunk)

                file_size = os.path.getsize(file_path)
                logger.info(f"File saved successfully. Size: {file_size} bytes")

                # Create SgyFileCreate object
                sgy_file_create = SgyFileCreate(
                    id=file_id,
                    original_name=original_filename,
                    path=file_path,
                    size=file_size,
                    type=file_extension.upper(),
                    project_id=project_id,
                    upload_date=datetime.now(),
                )

                # Add it to the DB
                db_sgy_file = create_sgy_file_info(db=db, sgy_file=sgy_file_create)
                logger.info(f"File info saved to database with ID: {file_id}")

                result_files.append({
                    "id": sgy_file_create.id,
                    "original_name": sgy_file_create.original_name,
                    "path": sgy_file_create.path,
                    "size": sgy_file_create.size,
                    "upload_date": sgy_file_create.upload_date.isoformat(),
                    "file_type": sgy_file_create.type
                })
                logger.info(f"Successfully processed file: {original_filename} with ID: {file_id}")

            except Exception as file_error:
                logger.error(f"Error processing file {sgy_file.filename}: {str(file_error)}")
                # Continue with other files
                
        if not result_files:
            logger.error("No files were successfully uploaded")
            raise HTTPException(status_code=400, detail="No files were successfully uploaded")

        logger.info(f"=== Upload Complete ===")
        logger.info(f"Successfully uploaded {len(result_files)} files")
        
        return {
            "status": "success",
            "message": f"{len(result_files)} file(s) uploaded successfully",
            "file_infos": result_files
        }
    except Exception as e:
        logger.error(f"=== Upload Error ===")
        logger.error(f"Error in upload_sgy_files_to_project: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading files: {str(e)}")


@sgy_file_router.delete("/{sgy_file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_sgy_file_endpoint(
        sgy_file_id: str,
        db: Session = db_dependency,
        current_user: User = Depends(get_current_user)
):
    """
    Delete a SEG-Y file.
    Requires authentication and auth_level >= 1.
    """
    check_permissions(current_user, 1)
    sgy_file_info = get_sgy_file_info(db, sgy_file_id)
    if not sgy_file_info:
        raise HTTPException(status_code=404, detail="SEG-Y file not found")

    sgy_file_path = sgy_file_info.path
    try:
        if os.path.exists(sgy_file_path):
            os.remove(sgy_file_path)
    except Exception as e:
        logger.error(f"Error deleting file {sgy_file_path}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting physical file: {str(e)}")

    success = delete_sgy_file_info(db, sgy_file_id)
    if not success:
        raise HTTPException(status_code=404, detail="SEG-Y file not found")
    return {"status": "success", "message": f"SEG-Y file {sgy_file_id} deleted successfully"}


@sgy_file_router.get("/download_file/{sgy_file_id}", status_code=status.HTTP_200_OK)
async def download_sgy_file_endpoint(
        sgy_file_id: str,
        db: Session = db_dependency,
        current_user: User = Depends(get_current_user)
):
    """
    Download a specific SEG-Y file by ID.
    Requires authentication and auth_level >= 1.
    """
    check_permissions(current_user, 1)

    # Get file info from database
    sgy_file_info = get_sgy_file_info(db, sgy_file_id)
    if not sgy_file_info:
        raise HTTPException(status_code=404, detail="SEG-Y file not found")

    # Check if file exists physically
    if not os.path.exists(sgy_file_info.path):
        raise HTTPException(status_code=404, detail="File not found on server")

    # Return file as streaming response
    return StreamingResponse(
        open(sgy_file_info.path, 'rb'),
        media_type='application/octet-stream',
        headers={
            'Content-Disposition': f'attachment; filename="{sgy_file_info.original_name}"'
        }
    )

@sgy_file_router.get("/download_project_sgy/{project_id}", status_code=status.HTTP_200_OK)
async def download_sgy_files_for_project_endpoint(
        project_id: str,
        db: Session = db_dependency,
        current_user: User = Depends(get_current_user)
):
    """
    Download all SEG-Y files for a specific project as a zip archive.
    Requires authentication and auth_level >= 1.
    """
    check_permissions(current_user, 1)

    # Get all files for the project
    sgy_files = get_sgy_files_info_by_project(db, project_id)
    if not sgy_files:
        err_string = f"No SEG-Y files found for project {project_id}"
        logger.error(err_string)
        raise HTTPException(status_code=404, detail=err_string)
    logger.info(f"Found {len(sgy_files)} files for project {project_id}")

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')

    try:
        with zipfile.ZipFile(temp_file, 'w') as zipf:
            for sgy_file in sgy_files:
                logger.info(f"Adding sgy file {sgy_file.path} to archive.")
                if os.path.exists(sgy_file.path):
                    zipf.write(sgy_file.path, arcname=sgy_file.original_name)

        # Return the zip file as streaming response
        return StreamingResponse(
            open(temp_file.name, 'rb'),
            media_type='application/zip',
            headers={
                'Content-Disposition': f'attachment; filename="project_{project_id}_records.zip"'
            }
        )
    except Exception as e:
        logger.error(f"Error creating zip file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating zip file: {str(e)}")
    finally:
        # Clean up the temporary file
        try:
            os.unlink(temp_file.name)
        except Exception as e:
            logger.error(f"Error cleaning up temporary file: {str(e)}")
