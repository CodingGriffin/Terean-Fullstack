import logging

from sqlalchemy.orm import Session

from models.file_model import FileDBModel
from schemas.file_schema import FileCreate

logger = logging.getLogger(__name__)


def get_file_info(db: Session, file_id: str):
    return db.query(FileDBModel).filter(FileDBModel.id == file_id).first()


def get_files_info(db: Session, skip: int = 0, limit: int = 100):
    return db.query(FileDBModel).offset(skip).limit(limit).all()


def get_files_info_by_project(db: Session, project_id: str, skip: int = 0, limit: int = 100):
    return db.query(FileDBModel).filter(FileDBModel.project_id == project_id).offset(skip).limit(limit).all()


def create_file_info(db: Session, file: FileCreate):
    db_file = FileDBModel(**file.model_dump())
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


def delete_file_info(db: Session, file_id: str):
    db_file = db.query(FileDBModel).filter(FileDBModel.id == file_id).first()
    if db_file:
        db.delete(db_file)
        db.commit()
        return True
    return False


def update_file_info(db: Session, file_id: str, file: FileCreate):
    db_file = db.query(FileDBModel).filter(FileDBModel.id == file_id).first()
    if db_file:
        for key, value in file.model_dump().items():
            setattr(db_file, key, value)
        db.commit()
        db.refresh(db_file)
        return db_file
    return None 