import logging

from sqlalchemy.orm import Session

from backend.crud.project_crud import get_project, create_default_project
from backend.schemas.project_schema import Project

logger = logging.getLogger(__name__)

def init_project(project_id: str, db: Session) -> Project:
    # See if project exists in db
    logger.info(f"Checking Project ID: {project_id}")
    db_project = get_project(db, project_id)
    logger.info(f"DB Project: {db_project}")

    # No project yet
    if db_project is None:
        # Create a default
        ret_project = create_default_project(db=db, project_id=project_id)
    else:
        ret_project = Project.from_db(db_project)
    logger.info(f"Returning Project: {ret_project}")
    return ret_project
