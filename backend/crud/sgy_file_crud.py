import logging

from sqlalchemy.orm import Session
from backend.models.sgy_file_model import SgyFileDBModel
from backend.schemas.sgy_file_schema import SgyFileCreate

logger = logging.getLogger(__name__)


def get_sgy_file_info(db: Session, sgy_file_id: str):
    return db.query(SgyFileDBModel).filter(SgyFileDBModel.id == sgy_file_id).first()


def get_sgy_files_info(db: Session, skip: int = 0, limit: int = 100):
    query_return = db.query(SgyFileDBModel).offset(skip).limit(limit).all()
    return query_return


def get_sgy_files_info_by_project(db: Session, project_id: str, skip: int = 0, limit: int = 100):
    return db.query(SgyFileDBModel).filter(SgyFileDBModel.project_id == project_id).offset(skip).limit(limit).all()


def create_sgy_file_info(db: Session, sgy_file: SgyFileCreate):
    db_sgy_file = SgyFileDBModel(**sgy_file.model_dump())
    db.add(db_sgy_file)
    db.commit()
    db.refresh(db_sgy_file)
    return db_sgy_file


def delete_sgy_file_info(db: Session, sgy_file_id: str):
    db_sgy_file = db.query(SgyFileDBModel).filter(SgyFileDBModel.id == sgy_file_id).first()
    if db_sgy_file:
        db.delete(db_sgy_file)
        db.commit()
        return True
    return False


def update_sgy_file_info(db: Session, sgy_file_id: str, sgy_file: SgyFileCreate):
    db_sgy_file = db.query(SgyFileDBModel).filter(SgyFileDBModel.id == sgy_file_id).first()
    if db_sgy_file:
        for key, value in sgy_file.model_dump().items():
            setattr(db_sgy_file, key, value)
        db.commit()
        db.refresh(db_sgy_file)
        return db_sgy_file
    return None
