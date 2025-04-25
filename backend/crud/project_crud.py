from sqlalchemy.orm import Session
from backend.models.project_model import ProjectModel
from backend.schemas.project_schema import ProjectCreate


# Create
def create_project(
        db: Session,
        new_project: ProjectCreate,
):
    db_project = ProjectModel(**new_project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def get_projects(
        db: Session,
        max_responses: int,
        query_filters: list[any],
        skip: int = 0,
):
    return db.query(ProjectModel).filter(*query_filters).offset(skip).limit(max_responses).all()
