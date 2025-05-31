from sqlalchemy.orm import Session
from models.contact_model import ContactDBModel
from schemas.contact_schema import ContactCreate

def create_contact(
    db: Session,
    new_contact: ContactCreate,
):
    db_contact = ContactDBModel(**new_contact.model_dump())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def get_contact(
    db: Session,
    contact_id: int,
):
    return db.query(ContactDBModel).filter(ContactDBModel.id == contact_id).first()

def get_contacts(
    db: Session,
    skip: int = 0,
    limit: int = 100,
):
    return db.query(ContactDBModel).offset(skip).limit(limit).all() 