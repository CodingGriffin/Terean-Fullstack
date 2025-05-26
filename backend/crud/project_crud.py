import json

from sqlalchemy.orm import Session
from typing import List, Optional, Any, Type

from tereancore.utils import generate_time_based_uid

from backend.models import SgyFileDBModel
from backend.models.project_model import ProjectDBModel
from backend.schemas.project_schema import ProjectCreate, Project

# Default values for project fields
DEFAULT_PROJECT_NAME = "Untitled Project"
DEFAULT_GEOMETRY = []
DEFAULT_RECORD_OPTIONS = []
DEFAULT_PLOT_LIMITS = {
    "numFreq": 50,
    "maxFreq": 50,
    "numSlow": 50,
    "maxSlow": 0.015
}
DEFAULT_FREQ = []
DEFAULT_SLOW = []
DEFAULT_PICKS = []
DEFAULT_DISPER_SETTINGS = {
    "layers": [
        {"startDepth": 0.0, "endDepth": 30.0, "velocity": 760.0, "density": 2.0, "ignore": 0},
        {"startDepth": 30.0, "endDepth": 44.0, "velocity": 1061.0, "density": 2.0, "ignore": 0},
        {"startDepth": 44.0, "endDepth": 144.0, "velocity": 1270.657, "density": 2.0, "ignore": 0},
    ],
    "displayUnits": "m",
    "asceVersion": "ASCE 7-22",
    "curveAxisLimits": {
        "xmin": 0.001,
        "xmax": 0.6,
        "ymin": 30,
        "ymax": 500
    },
    "modelAxisLimits": {
        "xmin": 50,
        "xmax": 1400,
        "ymin": 0,
        "ymax": 50
    },
    "numPoints": 10,
    "velocityUnit": "velocity",
    "periodUnit": "period",
    "velocityReversed": False,
    "periodReversed": False,
    "axesSwapped": False
}


def get_project(db: Session, project_id: str) -> Optional[ProjectDBModel]:
    return db.query(ProjectDBModel).filter(ProjectDBModel.id == project_id).first()


def get_projects(db: Session, skip: int = 0, limit: int = 100) -> list[Type[ProjectDBModel]]:
    return db.query(ProjectDBModel).offset(skip).limit(limit).all()


def create_project(db: Session, project: ProjectCreate | Project) -> ProjectDBModel:
    db_project = ProjectDBModel(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def create_default_project(
    db: Session,
    project_id: str,
):
    # Create a ProjectCreate with all defaults
    default_project_create = Project(
        id=project_id,
        name=DEFAULT_PROJECT_NAME,
        geometry=json.dumps(DEFAULT_GEOMETRY),
        record_options=json.dumps(DEFAULT_RECORD_OPTIONS),
        plot_limits=json.dumps(DEFAULT_PLOT_LIMITS),
        freq=json.dumps(DEFAULT_FREQ),
        slow=json.dumps(DEFAULT_SLOW),
        picks=json.dumps(DEFAULT_PICKS),
        disper_settings=json.dumps(DEFAULT_DISPER_SETTINGS)
    )
    created_project = create_project(db, default_project_create)
    return created_project


def update_project(db: Session, project_id: str, project: ProjectCreate) -> Optional[ProjectDBModel]:
    db_project = get_project(db, project_id)
    if db_project:
        for key, value in project.model_dump().items():
            setattr(db_project, key, value)
        db.commit()
        db.refresh(db_project)
    return db_project


def delete_project(db: Session, project_id: str) -> bool:
    db_project = get_project(db, project_id)
    if db_project:
        db.delete(db_project)
        db.commit()
        return True
    return False


def get_project_records(db: Session, project_id: str, json_return=True, brief_info=True) -> List[Any] | str:
    """
    Gets record info for all records in a project, returning it as a json formatted string.
    
    :param brief_info: Whether to include full record info.
    :param json_return: Whether to return as a json formatted string or a list of dicts.
    :param db: DB session object. 
    :param project_id: ID of the project to get records for.
    :return: JSON formatted string of record info, returning an empty list if no records are found.
    """
    query_results =  db.query(SgyFileDBModel).filter(SgyFileDBModel.project_id == project_id).all()

    if not query_results or len(query_results) <= 0:
        if json_return:
            return json.dumps([])
        else:
            return []
    
    records = []
    for record in query_results:
        if brief_info:
            records.append({
                "id": record.id,
                "original_name": record.original_name,
                "type": record.type
            })
        else:
            records.append({
                "id": record.id,
                "original_name": record.original_name,
                "path": record.path,
                "size": record.size,
                "upload_date": record.upload_date.isoformat() if record.upload_date else None,
                "type": record.type
            })            
    if json_return:
        return json.dumps(records)
    else:
        return records
