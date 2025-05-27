import json
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.crud.project_crud import update_project
from backend.database import get_db
from backend.models.project_model import ProjectDBModel
from backend.schemas.project_schema import ProjectCreate
from backend.schemas.user_schema import User
from backend.utils.authentication import get_current_user, check_permissions
from backend.utils.project_utils import init_project
from backend.schemas.additional_models import (
    DisperSettingsModel,
    OptionsModel,
    PickData
)

logger = logging.getLogger(__name__)
project_router = APIRouter(prefix="/project", tags=["Project"])

# Dependency
db_dependency = Depends(get_db)


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
