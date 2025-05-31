from sqlalchemy.orm import Session
from models.client_model import ClientDBModel
from schemas.client_schema import ClientCreate

def create_client(
    db: Session,
    new_client: ClientCreate,
):
    db_client = ClientDBModel(**new_client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

def get_client(
    db: Session,
    client_id: int,
):
    return db.query(ClientDBModel).filter(ClientDBModel.id == client_id).first()

def get_clients(
    db: Session,
    skip: int = 0,
    limit: int = 100,
):
    return db.query(ClientDBModel).offset(skip).limit(limit).all() 