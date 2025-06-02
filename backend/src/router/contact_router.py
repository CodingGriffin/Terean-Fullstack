import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from crud import contact_crud, client_crud
from schemas.contact_schema import Contact, ContactCreate, ContactUpdate
from schemas.user_schema import User
from utils.authentication import get_current_user, check_permissions

logger = logging.getLogger(__name__)
contact_router = APIRouter(prefix="/contacts", tags=["Contacts"])

@contact_router.post("/", response_model=Contact, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new contact."""
    check_permissions(current_user, 1)
    
    # Verify client exists
    client = client_crud.get_client(db=db, client_id=contact.client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {contact.client_id} not found"
        )
    
    try:
        db_contact = contact_crud.create_contact(db=db, new_contact=contact)
        return db_contact
    except Exception as e:
        logger.error(f"Error creating contact: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating contact: {str(e)}"
        )

@contact_router.get("/", response_model=List[Contact])
async def get_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    client_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of all contacts with optional filtering by client."""
    check_permissions(current_user, 1)
    
    try:
        if client_id:
            contacts = contact_crud.get_contacts_by_client(
                db=db, client_id=client_id, skip=skip, limit=limit
            )
        else:
            contacts = contact_crud.get_contacts(db=db, skip=skip, limit=limit)
        return contacts
    except Exception as e:
        logger.error(f"Error fetching contacts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching contacts: {str(e)}"
        )

@contact_router.get("/{contact_id}", response_model=Contact)
async def get_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific contact by ID."""
    check_permissions(current_user, 1)
    
    contact = contact_crud.get_contact(db=db, contact_id=contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with ID {contact_id} not found"
        )
    
    return contact

@contact_router.put("/{contact_id}", response_model=Contact)
async def update_contact(
    contact_id: int,
    contact_update: ContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a contact."""
    check_permissions(current_user, 1)
    
    # If changing client_id, verify new client exists
    if contact_update.client_id is not None:
        client = client_crud.get_client(db=db, client_id=contact_update.client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client with ID {contact_update.client_id} not found"
            )
    
    updated_contact = contact_crud.update_contact(
        db=db, 
        contact_id=contact_id, 
        contact_update=contact_update
    )
    
    if not updated_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with ID {contact_id} not found"
        )
    
    return updated_contact

@contact_router.delete("/{contact_id}")
async def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a contact."""
    check_permissions(current_user, 1)
    
    success = contact_crud.delete_contact(db=db, contact_id=contact_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with ID {contact_id} not found"
        )
    
    return {"detail": f"Contact {contact_id} deleted successfully"}

@contact_router.get("/client/{client_id}", response_model=List[Contact])
async def get_contacts_by_client(
    client_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all contacts for a specific client."""
    check_permissions(current_user, 1)
    
    # Verify client exists
    client = client_crud.get_client(db=db, client_id=client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )
    
    contacts = contact_crud.get_contacts_by_client(
        db=db, client_id=client_id, skip=skip, limit=limit
    )
    
    return contacts