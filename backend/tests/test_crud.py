"""
Test CRUD operations.
"""
import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from crud import user_crud, project_crud, sgy_file_crud, file_crud, client_crud, contact_crud
from schemas.user_schema import UserCreate, UserUpdate
from schemas.project_schema import ProjectCreate, ProjectUpdate
from schemas.sgy_file_schema import SgyFileCreate, SgyFileUpdate
from schemas.file_schema import FileCreate, FileUpdate
from schemas.client_schema import ClientCreate, ClientUpdate
from schemas.contact_schema import ContactCreate
from models.user_model import UserDBModel
from models.project_model import ProjectDBModel


class TestUserCRUD:
    """Test user CRUD operations."""
    
    @pytest.mark.db
    def test_create_user(self, test_db: Session):
        """Test creating a user."""
        user_data = UserCreate(
            username="crudtest",
            password="password123",
            email="crud@test.com",
            full_name="CRUD Test",
            disabled=False,
            auth_level=1
        )
        
        user = user_crud.create_user(db=test_db, user=user_data)
        
        assert user.username == "crudtest"
        assert user.email == "crud@test.com"
        assert user.hashed_password != "password123"  # Should be hashed
        assert user_crud.verify_password("password123", user.hashed_password)
    
    @pytest.mark.db
    def test_get_user_by_id(self, test_db: Session):
        """Test getting user by ID."""
        # Create user
        user_data = UserCreate(
            username="getbyid",
            password="password123",
            disabled=False,
            auth_level=1
        )
        created_user = user_crud.create_user(db=test_db, user=user_data)
        
        # Get user
        fetched_user = user_crud.get_user(db=test_db, user_id=created_user.id)
        
        assert fetched_user is not None
        assert fetched_user.id == created_user.id
        assert fetched_user.username == "getbyid"
    
    @pytest.mark.db
    def test_get_user_by_username(self, test_db: Session):
        """Test getting user by username."""
        # Create user
        user_data = UserCreate(
            username="getbyusername",
            password="password123",
            disabled=False,
            auth_level=1
        )
        user_crud.create_user(db=test_db, user=user_data)
        
        # Get user
        fetched_user = user_crud.get_user_by_username(db=test_db, username="getbyusername")
        
        assert fetched_user is not None
        assert fetched_user.username == "getbyusername"
    
    @pytest.mark.db
    def test_get_users_list(self, test_db: Session):
        """Test getting list of users."""
        # Create multiple users
        for i in range(3):
            user_data = UserCreate(
                username=f"listuser{i}",
                password="password123",
                disabled=False,
                auth_level=1
            )
            user_crud.create_user(db=test_db, user=user_data)
        
        # Get users
        users = user_crud.get_users(db=test_db, skip=0, limit=10)
        
        assert len(users) >= 3
        usernames = [u.username for u in users]
        assert "listuser0" in usernames
        assert "listuser1" in usernames
        assert "listuser2" in usernames
    
    @pytest.mark.db
    def test_update_user(self, test_db: Session):
        """Test updating user."""
        # Create user
        user_data = UserCreate(
            username="updatetest",
            password="password123",
            email="old@test.com",
            disabled=False,
            auth_level=1
        )
        user = user_crud.create_user(db=test_db, user=user_data)
        
        # Update user
        update_data = UserUpdate(
            email="new@test.com",
            full_name="Updated Name",
            auth_level=2
        )
        updated_user = user_crud.update_user(
            db=test_db,
            user_id=user.id,
            user_update=update_data
        )
        
        assert updated_user.email == "new@test.com"
        assert updated_user.full_name == "Updated Name"
        assert updated_user.auth_level == 2
        assert updated_user.username == "updatetest"  # Unchanged
    
    @pytest.mark.db
    def test_delete_user(self, test_db: Session):
        """Test deleting user."""
        # Create user
        user_data = UserCreate(
            username="deletetest",
            password="password123",
            disabled=False,
            auth_level=1
        )
        user = user_crud.create_user(db=test_db, user=user_data)
        user_id = user.id
        
        # Delete user
        result = user_crud.delete_user(db=test_db, user_id=user_id)
        assert result is True
        
        # Verify deletion
        deleted_user = user_crud.get_user(db=test_db, user_id=user_id)
        assert deleted_user is None


class TestProjectCRUD:
    """Test project CRUD operations."""
    
    @pytest.mark.db
    def test_create_project(self, test_db: Session):
        """Test creating a project."""
        project_data = ProjectCreate(
            unique_id="crud_proj_001",
            name="CRUD Test Project",
            description="Testing CRUD operations",
            status="active"
        )
        
        project = project_crud.create_project(db=test_db, project=project_data)
        
        assert project.unique_id == "crud_proj_001"
        assert project.name == "CRUD Test Project"
        assert project.status == "active"
        assert project.created_date is not None
    
    @pytest.mark.db
    def test_get_project_by_id(self, test_db: Session):
        """Test getting project by ID."""
        # Create project
        project_data = ProjectCreate(
            unique_id="get_proj_001",
            name="Get Project Test",
            status="active"
        )
        created_project = project_crud.create_project(db=test_db, project=project_data)
        
        # Get project
        fetched_project = project_crud.get_project(db=test_db, project_id=created_project.id)
        
        assert fetched_project is not None
        assert fetched_project.id == created_project.id
        assert fetched_project.name == "Get Project Test"
    
    @pytest.mark.db
    def test_get_project_by_unique_id(self, test_db: Session):
        """Test getting project by unique ID."""
        # Create project
        project_data = ProjectCreate(
            unique_id="unique_proj_001",
            name="Unique Project Test",
            status="active"
        )
        project_crud.create_project(db=test_db, project=project_data)
        
        # Get project
        fetched_project = project_crud.get_project_by_unique_id(
            db=test_db,
            unique_id="unique_proj_001"
        )
        
        assert fetched_project is not None
        assert fetched_project.unique_id == "unique_proj_001"
    
    @pytest.mark.db
    def test_get_projects_list(self, test_db: Session):
        """Test getting list of projects."""
        # Create multiple projects
        for i in range(3):
            project_data = ProjectCreate(
                unique_id=f"list_proj_{i}",
                name=f"List Project {i}",
                status="active"
            )
            project_crud.create_project(db=test_db, project=project_data)
        
        # Get projects
        projects = project_crud.get_projects(db=test_db, skip=0, limit=10)
        
        assert len(projects) >= 3
        project_names = [p.name for p in projects]
        assert "List Project 0" in project_names
        assert "List Project 1" in project_names
        assert "List Project 2" in project_names
    
    @pytest.mark.db
    def test_update_project(self, test_db: Session):
        """Test updating project."""
        # Create project
        project_data = ProjectCreate(
            unique_id="update_proj_001",
            name="Original Name",
            description="Original description",
            status="active"
        )
        project = project_crud.create_project(db=test_db, project=project_data)
        
        # Update project
        update_data = ProjectUpdate(
            name="Updated Name",
            description="Updated description",
            status="completed"
        )
        updated_project = project_crud.update_project(
            db=test_db,
            project_id=project.id,
            project_update=update_data
        )
        
        assert updated_project.name == "Updated Name"
        assert updated_project.description == "Updated description"
        assert updated_project.status == "completed"
        assert updated_project.unique_id == "update_proj_001"  # Unchanged
    
    @pytest.mark.db
    def test_delete_project(self, test_db: Session):
        """Test deleting project."""
        # Create project
        project_data = ProjectCreate(
            unique_id="delete_proj_001",
            name="Delete Test Project",
            status="active"
        )
        project = project_crud.create_project(db=test_db, project=project_data)
        project_id = project.id
        
        # Delete project
        result = project_crud.delete_project(db=test_db, project_id=project_id)
        assert result is True
        
        # Verify deletion
        deleted_project = project_crud.get_project(db=test_db, project_id=project_id)
        assert deleted_project is None


class TestSgyFileCRUD:
    """Test SGY file CRUD operations."""
    
    @pytest.mark.db
    def test_create_sgy_file(self, test_db: Session):
        """Test creating an SGY file."""
        sgy_data = SgyFileCreate(
            filename="test_crud.sgy",
            file_path="/data/test_crud.sgy",
            file_size=1024000,
            status="uploaded"
        )
        
        sgy_file = sgy_file_crud.create_sgy_file(db=test_db, sgy_file=sgy_data)
        
        assert sgy_file.filename == "test_crud.sgy"
        assert sgy_file.file_size == 1024000
        assert sgy_file.upload_date is not None
    
    @pytest.mark.db
    def test_get_sgy_file(self, test_db: Session):
        """Test getting SGY file by ID."""
        # Create SGY file
        sgy_data = SgyFileCreate(
            filename="get_test.sgy",
            file_path="/data/get_test.sgy",
            file_size=512000,
            status="uploaded"
        )
        created_file = sgy_file_crud.create_sgy_file(db=test_db, sgy_file=sgy_data)
        
        # Get file
        fetched_file = sgy_file_crud.get_sgy_file(db=test_db, file_id=created_file.id)
        
        assert fetched_file is not None
        assert fetched_file.id == created_file.id
        assert fetched_file.filename == "get_test.sgy"
    
    @pytest.mark.db
    def test_get_sgy_files_list(self, test_db: Session):
        """Test getting list of SGY files."""
        # Create multiple files
        for i in range(3):
            sgy_data = SgyFileCreate(
                filename=f"list_test_{i}.sgy",
                file_path=f"/data/list_test_{i}.sgy",
                file_size=256000 * (i + 1),
                status="uploaded"
            )
            sgy_file_crud.create_sgy_file(db=test_db, sgy_file=sgy_data)
        
        # Get files
        files = sgy_file_crud.get_sgy_files(db=test_db, skip=0, limit=10)
        
        assert len(files) >= 3
        filenames = [f.filename for f in files]
        assert "list_test_0.sgy" in filenames
        assert "list_test_1.sgy" in filenames
        assert "list_test_2.sgy" in filenames
    
    @pytest.mark.db
    def test_update_sgy_file(self, test_db: Session):
        """Test updating SGY file."""
        # Create file
        sgy_data = SgyFileCreate(
            filename="update_test.sgy",
            file_path="/data/update_test.sgy",
            file_size=1024000,
            status="uploaded"
        )
        sgy_file = sgy_file_crud.create_sgy_file(db=test_db, sgy_file=sgy_data)
        
        # Update file
        update_data = SgyFileUpdate(
            status="processed",
            metadata={"traces": 1000, "samples": 2000}
        )
        updated_file = sgy_file_crud.update_sgy_file(
            db=test_db,
            file_id=sgy_file.id,
            sgy_file_update=update_data
        )
        
        assert updated_file.status == "processed"
        assert updated_file.metadata["traces"] == 1000
        assert updated_file.filename == "update_test.sgy"  # Unchanged


class TestClientCRUD:
    """Test client CRUD operations."""
    
    @pytest.mark.db
    def test_create_client(self, test_db: Session):
        """Test creating a client."""
        client_data = ClientCreate(
            name="CRUD Test Client",
            email="crudclient@test.com",
            phone="+1234567890",
            company="CRUD Corp"
        )
        
        client = client_crud.create_client(db=test_db, client=client_data)
        
        assert client.name == "CRUD Test Client"
        assert client.email == "crudclient@test.com"
        assert client.company == "CRUD Corp"
    
    @pytest.mark.db
    def test_get_clients(self, test_db: Session):
        """Test getting list of clients."""
        # Create multiple clients
        for i in range(3):
            client_data = ClientCreate(
                name=f"Client {i}",
                email=f"client{i}@test.com"
            )
            client_crud.create_client(db=test_db, client=client_data)
        
        # Get clients
        clients = client_crud.get_clients(db=test_db, skip=0, limit=10)
        
        assert len(clients) >= 3
        client_names = [c.name for c in clients]
        assert "Client 0" in client_names
        assert "Client 1" in client_names
        assert "Client 2" in client_names


class TestContactCRUD:
    """Test contact CRUD operations."""
    
    @pytest.mark.db
    def test_create_contact(self, test_db: Session):
        """Test creating a contact."""
        contact_data = ContactCreate(
            name="CRUD Contact",
            email="crudcontact@test.com",
            phone="+9876543210",
            company="Contact Corp",
            message="Test message"
        )
        
        contact = contact_crud.create_contact(db=test_db, contact=contact_data)
        
        assert contact.name == "CRUD Contact"
        assert contact.message == "Test message"
        assert contact.created_date is not None
    
    @pytest.mark.db
    def test_get_contacts(self, test_db: Session):
        """Test getting list of contacts."""
        # Create multiple contacts
        for i in range(3):
            contact_data = ContactCreate(
                name=f"Contact {i}",
                email=f"contact{i}@test.com",
                message=f"Message {i}"
            )
            contact_crud.create_contact(db=test_db, contact=contact_data)
        
        # Get contacts
        contacts = contact_crud.get_contacts(db=test_db, skip=0, limit=10)
        
        assert len(contacts) >= 3
        contact_names = [c.name for c in contacts]
        assert "Contact 0" in contact_names
        assert "Contact 1" in contact_names
        assert "Contact 2" in contact_names 