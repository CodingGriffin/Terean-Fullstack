import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from crud import client_crud
from schemas.client_schema import Client, ClientCreate, ClientUpdate
from schemas.user_schema import User
from utils.authentication import get_current_user, check_permissions

logger = logging.getLogger(__name__)
client_router = APIRouter(prefix="/clients", tags=["Clients"])

@client_router.post("/", response_model=Client, status_code=status.HTTP_201_CREATED)
async def create_client(
    client: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new client."""
    check_permissions(current_user, 1)
    
    try:
        db_client = client_crud.create_client(db=db, new_client=client)
        return db_client
    except Exception as e:
        logger.error(f"Error creating client: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating client: {str(e)}"
        )

@client_router.get("/", response_model=List[Client])
async def get_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    name_search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of all clients with optional filtering."""
    check_permissions(current_user, 1)
    
    try:
        # TODO: Add name_search filtering in client_crud
        clients = client_crud.get_clients(db=db, skip=skip, limit=limit)
        return clients
    except Exception as e:
        logger.error(f"Error fetching clients: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching clients: {str(e)}"
        )

@client_router.get("/{client_id}", response_model=Client)
async def get_client(
    client_id: int,
    include_projects: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific client by ID."""
    check_permissions(current_user, 1)
    
    client = client_crud.get_client(db=db, client_id=client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )
    
    return client

@client_router.put("/{client_id}", response_model=Client)
async def update_client(
    client_id: int,
    client_update: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a client."""
    check_permissions(current_user, 1)
    
    updated_client = client_crud.update_client(
        db=db, 
        client_id=client_id, 
        client_update=client_update
    )
    
    if not updated_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )
    
    return updated_client

@client_router.delete("/{client_id}")
async def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a client."""
    check_permissions(current_user, 2)  # Higher permission required for deletion
    
    # Check if client has associated projects
    client = client_crud.get_client(db=db, client_id=client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )
    
    if client.projects:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete client with associated projects. Found {len(client.projects)} projects."
        )
    
    success = client_crud.delete_client(db=db, client_id=client_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete client"
        )
    
    return {"detail": f"Client {client_id} deleted successfully"}

@client_router.get("/{client_id}/projects")
async def get_client_projects(
    client_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all projects associated with a client."""
    check_permissions(current_user, 1)
    
    client = client_crud.get_client(db=db, client_id=client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )
    
    # Return paginated projects
    projects = client.projects[skip:skip + limit]
    return {
        "client_id": client_id,
        "client_name": client.name,
        "projects": projects,
        "total": len(client.projects)
    }