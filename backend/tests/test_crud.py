"""
Test CRUD operations.
"""
import pytest
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from schemas.user_schema import UserCreate, UserUpdate
from schemas.project_schema import ProjectCreate, ProjectUpdate
from schemas.sgy_file_schema import SgyFileCreate, SgyFileUpdate
from schemas.file_schema import FileCreate, FileUpdate
from schemas.client_schema import ClientCreate, ClientUpdate
from schemas.contact_schema import ContactCreate

from crud import user_crud, project_crud, sgy_file_crud, file_crud, client_crud, contact_crud
from models.user_model import UserDBModel
from models.project_model import ProjectDBModel
from models.sgy_file_model import SgyFileDBModel
from utils.custom_types.ProjectStatus import ProjectStatus


class TestUserCRUD:
    """Test user CRUD operations."""
    
    @pytest.mark.db
    def test_create_user(self, test_db: Session):
        """Test creating a user."""
        user_data = UserCreate(
            username="crudtest",
            password="password123",
            email="crud@test.com",
            full_name="CRUD Test User",
            disabled=False,
            auth_level=1
        )
        
        user = user_crud.create_user(db=test_db, user=user_data)
        
        assert user.username == "crudtest"
        assert user.email == "crud@test.com"
        assert user.full_name == "CRUD Test User"
        assert user.auth_level == 1
        assert user.disabled is False
        # Password should be hashed
        assert user.hashed_password != "password123"
    
    @pytest.mark.db
    def test_get_user_by_username(self, test_db: Session):
        """Test getting user by username."""
        # Create user
        user_data = UserCreate(
            username="getbyusername",
            password="password123",
            email="getbyusername@test.com",
            disabled=False,
            auth_level=1
        )
        created_user = user_crud.create_user(db=test_db, user=user_data)
        
        # Get user
        fetched_user = user_crud.get_user_by_username(
            db=test_db, 
            username="getbyusername"
        )
        
        assert fetched_user is not None
        assert fetched_user.id == created_user.id
        assert fetched_user.username == "getbyusername"
    
    @pytest.mark.db
    def test_get_user_by_email(self, test_db: Session):
        """Test getting user by email."""
        # Create user
        user_data = UserCreate(
            username="getbyemail",
            password="password123",
            email="unique@test.com",
            disabled=False,
            auth_level=1
        )
        created_user = user_crud.create_user(db=test_db, user=user_data)
        
        # Get user
        fetched_user = user_crud.get_user_by_email(
            db=test_db,
            email="unique@test.com"
        )
        
        assert fetched_user is not None
        assert fetched_user.id == created_user.id
        assert fetched_user.email == "unique@test.com"
    
    @pytest.mark.db
    def test_get_users_list(self, test_db: Session):
        """Test getting list of users."""
        # Create multiple users
        for i in range(5):
            user_data = UserCreate(
                username=f"listuser{i}",
                password="password123",
                email=f"listuser{i}@test.com",
                disabled=False,
                auth_level=1
            )
            user_crud.create_user(db=test_db, user=user_data)
        
        # Get all users
        users = user_crud.get_users(db=test_db, skip=0, limit=100)
        
        assert len(users) >= 5
        usernames = [u.username for u in users]
        for i in range(5):
            assert f"listuser{i}" in usernames
    
    @pytest.mark.db
    def test_update_user(self, test_db: Session):
        """Test updating user."""
        # Create user
        user_data = UserCreate(
            username="updateuser",
            password="password123",
            email="update@test.com",
            disabled=False,
            auth_level=1
        )
        user = user_crud.create_user(db=test_db, user=user_data)
        
        # Update user - using UserUpdate schema
        update_data = UserUpdate(
            email="updated@test.com",
            full_name="Updated Name",
            auth_level=2,
            disabled=True
        )
        updated_user = user_crud.update_user(
            db=test_db,
            user_id=user.id,
            user_update=update_data
        )
        
        assert updated_user.email == "updated@test.com"
        assert updated_user.full_name == "Updated Name"
        assert updated_user.auth_level == 2
        assert updated_user.disabled is True
        assert updated_user.username == "updateuser"  # Unchanged
    
    @pytest.mark.db
    def test_delete_user(self, test_db: Session):
        """Test deleting user."""
        # Create user
        user_data = UserCreate(
            username="deleteuser",
            password="password123",
            email="delete@test.com",
            disabled=False,
            auth_level=1
        )
        user = user_crud.create_user(db=test_db, user=user_data)
        user_id = user.id
        
        # Delete user
        result = user_crud.delete_user(db=test_db, user_id=user_id)
        assert result is True
        
        # Verify deleted
        deleted_user = user_crud.get_user(db=test_db, user_id=user_id)
        assert deleted_user is None


class TestProjectCRUD:
    """Test project CRUD operations."""
    
    @pytest.mark.db
    def test_create_project(self, test_db: Session):
        """Test creating a project."""
        # Create owner first
        user_data = UserCreate(
            username="projectowner",
            password="password123",
            email="owner@test.com",
            disabled=False,
            auth_level=1
        )
        owner = user_crud.create_user(db=test_db, user=user_data)
        
        project_data = ProjectCreate(
            name="CRUD Project",
            description="Test project for CRUD",
            status=ProjectStatus.not_started
        )
        
        project = project_crud.create_project(
            db=test_db,
            project=project_data,
            owner_id=owner.id
        )
        
        assert project.name == "CRUD Project"
        assert project.description == "Test project for CRUD"
        assert project.status == ProjectStatus.not_started
        assert project.owner_id == owner.id
    
    @pytest.mark.db
    def test_get_project_by_id(self, test_db: Session):
        """Test getting project by ID."""
        # Create owner and project
        user_data = UserCreate(
            username="getprojowner",
            password="password123",
            email="getprojowner@test.com",
            disabled=False,
            auth_level=1
        )
        owner = user_crud.create_user(db=test_db, user=user_data)
        
        project_data = ProjectCreate(
            name="Get Project Test",
            status=ProjectStatus.in_progress
        )
        created_project = project_crud.create_project(
            db=test_db,
            project=project_data,
            owner_id=owner.id
        )
        
        # Get project
        fetched_project = project_crud.get_project(
            db=test_db,
            project_id=created_project.id
        )
        
        assert fetched_project is not None
        assert fetched_project.id == created_project.id
        assert fetched_project.name == "Get Project Test"
    
    @pytest.mark.db
    def test_get_projects_list(self, test_db: Session):
        """Test getting list of projects."""
        # Create owner
        user_data = UserCreate(
            username="listprojowner",
            password="password123",
            email="listprojowner@test.com",
            disabled=False,
            auth_level=1
        )
        owner = user_crud.create_user(db=test_db, user=user_data)
        
        # Create multiple projects
        for i in range(5):
            project_data = ProjectCreate(
                name=f"List Project {i}",
                status=ProjectStatus.in_progress if i % 2 == 0 else ProjectStatus.completed
            )
            project_crud.create_project(
                db=test_db,
                project=project_data,
                owner_id=owner.id
            )
        
        # Get all projects
        projects = project_crud.get_projects(db=test_db, skip=0, limit=100)
        
        assert len(projects) >= 5
        names = [p.name for p in projects]
        for i in range(5):
            assert f"List Project {i}" in names
    
    @pytest.mark.db
    def test_update_project(self, test_db: Session):
        """Test updating project."""
        # Create owner and project
        user_data = UserCreate(
            username="updateprojowner",
            password="password123",
            email="updateprojowner@test.com",
            disabled=False,
            auth_level=1
        )
        owner = user_crud.create_user(db=test_db, user=user_data)
        
        project_data = ProjectCreate(
            name="Update Project",
            description="Original description",
            status=ProjectStatus.not_started
        )
        project = project_crud.create_project(
            db=test_db,
            project=project_data,
            owner_id=owner.id
        )
        
        # Update project - using ProjectUpdate schema
        update_data = ProjectUpdate(
            name="Updated Project Name",
            description="Updated description",
            status=ProjectStatus.completed
        )
        updated_project = project_crud.update_project(
            db=test_db,
            project_id=project.id,
            project_update=update_data
        )
        
        assert updated_project.name == "Updated Project Name"
        assert updated_project.description == "Updated description"
        assert updated_project.status == ProjectStatus.completed
    
    @pytest.mark.db
    def test_delete_project(self, test_db: Session):
        """Test deleting project."""
        # Create owner and project
        user_data = UserCreate(
            username="deleteprojowner",
            password="password123",
            email="deleteprojowner@test.com",
            disabled=False,
            auth_level=1
        )
        owner = user_crud.create_user(db=test_db, user=user_data)
        
        project_data = ProjectCreate(
            name="Delete Project",
            status=ProjectStatus.not_started
        )
        project = project_crud.create_project(
            db=test_db,
            project=project_data,
            owner_id=owner.id
        )
        project_id = project.id
        
        # Delete project
        result = project_crud.delete_project(db=test_db, project_id=project_id)
        assert result is True
        
        # Verify deleted
        deleted_project = project_crud.get_project(db=test_db, project_id=project_id)
        assert deleted_project is None


class TestSgyFileCRUD:
    """Test SGY file CRUD operations."""
    
    @pytest.mark.db
    def test_create_sgy_file(self, test_db: Session):
        """Test creating an SGY file."""
        # Create owner and project
        user_data = UserCreate(
            username="sgyowner",
            password="password123",
            email="sgyowner@test.com",
            disabled=False,
            auth_level=1
        )
        owner = user_crud.create_user(db=test_db, user=user_data)
        
        project_data = ProjectCreate(
            name="SGY Project",
            status=ProjectStatus.in_progress
        )
        project = project_crud.create_project(
            db=test_db,
            project=project_data,
            owner_id=owner.id
        )
        
        sgy_data = SgyFileCreate(
            filename="test_seismic.sgy",
            file_path="/data/test_seismic.sgy",
            file_size=1024000,
            status="uploaded"
        )
        
        sgy_file = sgy_file_crud.create_sgy_file(
            db=test_db,
            sgy_file=sgy_data,
            project_id=project.id,
            user_id=owner.id
        )
        
        assert sgy_file.filename == "test_seismic.sgy"
        assert sgy_file.file_size == 1024000
        assert sgy_file.status == "uploaded"
        assert sgy_file.project_id == project.id
        assert sgy_file.user_id == owner.id
    
    @pytest.mark.db
    def test_get_sgy_file_by_id(self, test_db: Session):
        """Test getting SGY file by ID."""
        # Create owner, project and SGY file
        user_data = UserCreate(
            username="getsgyowner",
            password="password123",
            email="getsgyowner@test.com",
            disabled=False,
            auth_level=1
        )
        owner = user_crud.create_user(db=test_db, user=user_data)
        
        project_data = ProjectCreate(
            name="Get SGY Project",
            status=ProjectStatus.in_progress
        )
        project = project_crud.create_project(
            db=test_db,
            project=project_data,
            owner_id=owner.id
        )
        
        sgy_data = SgyFileCreate(
            filename="get_test.sgy",
            file_path="/data/get_test.sgy",
            file_size=512000,
            status="processed"
        )
        created_sgy = sgy_file_crud.create_sgy_file(
            db=test_db,
            sgy_file=sgy_data,
            project_id=project.id,
            user_id=owner.id
        )
        
        # Get SGY file
        fetched_sgy = sgy_file_crud.get_sgy_file(
            db=test_db,
            sgy_file_id=created_sgy.id
        )
        
        assert fetched_sgy is not None
        assert fetched_sgy.id == created_sgy.id
        assert fetched_sgy.filename == "get_test.sgy"
    
    @pytest.mark.db
    def test_update_sgy_file(self, test_db: Session):
        """Test updating SGY file."""
        # Create owner, project and SGY file
        user_data = UserCreate(
            username="updatesgyowner",
            password="password123",
            email="updatesgyowner@test.com",
            disabled=False,
            auth_level=1
        )
        owner = user_crud.create_user(db=test_db, user=user_data)
        
        project_data = ProjectCreate(
            name="Update SGY Project",
            status=ProjectStatus.in_progress
        )
        project = project_crud.create_project(
            db=test_db,
            project=project_data,
            owner_id=owner.id
        )
        
        sgy_data = SgyFileCreate(
            filename="update_test.sgy",
            file_path="/data/update_test.sgy",
            file_size=256000,
            status="uploaded"
        )
        sgy_file = sgy_file_crud.create_sgy_file(
            db=test_db,
            sgy_file=sgy_data,
            project_id=project.id,
            user_id=owner.id
        )
        
        # Update SGY file - using SgyFileUpdate schema
        update_data = SgyFileUpdate(
            status="processing",
            metadata={"traces": 1000, "samples": 2000}
        )
        updated_sgy = sgy_file_crud.update_sgy_file(
            db=test_db,
            sgy_file_id=sgy_file.id,
            sgy_file_update=update_data
        )
        
        assert updated_sgy.status == "processing"
        assert updated_sgy.metadata["traces"] == 1000
        assert updated_sgy.filename == "update_test.sgy"  # Unchanged
    
    @pytest.mark.db
    def test_delete_sgy_file(self, test_db: Session):
        """Test deleting SGY file."""
        # Create owner, project and SGY file
        user_data = UserCreate(
            username="deletesgyowner",
            password="password123",
            email="deletesgyowner@test.com",
            disabled=False,
            auth_level=1
        )
        owner = user_crud.create_user(db=test_db, user=user_data)
        
        project_data = ProjectCreate(
            name="Delete SGY Project",
            status=ProjectStatus.in_progress
        )
        project = project_crud.create_project(
            db=test_db,
            project=project_data,
            owner_id=owner.id
        )
        
        sgy_data = SgyFileCreate(
            filename="delete_test.sgy",
            file_path="/data/delete_test.sgy",
            file_size=128000,
            status="uploaded"
        )
        sgy_file = sgy_file_crud.create_sgy_file(
            db=test_db,
            sgy_file=sgy_data,
            project_id=project.id,
            user_id=owner.id
        )
        sgy_id = sgy_file.id
        
        # Delete SGY file
        result = sgy_file_crud.delete_sgy_file(db=test_db, sgy_file_id=sgy_id)
        assert result is True
        
        # Verify deleted
        deleted_sgy = sgy_file_crud.get_sgy_file(db=test_db, sgy_file_id=sgy_id)
        assert deleted_sgy is None


class TestClientCRUD:
    """Test client CRUD operations."""
    
    @pytest.mark.db
    def test_create_client(self, test_db: Session):
        """Test creating a client."""
        client_data = ClientCreate(
            name="CRUD Client",
            email="crudclient@test.com",
            phone="+1234567890",
            company="CRUD Company",
            address="123 CRUD Street"
        )
        
        client = client_crud.create_client(db=test_db, client=client_data)
        
        assert client.name == "CRUD Client"
        assert client.email == "crudclient@test.com"
        assert client.phone == "+1234567890"
        assert client.company == "CRUD Company"
    
    @pytest.mark.db
    def test_get_client_by_id(self, test_db: Session):
        """Test getting client by ID."""
        # Create client
        client_data = ClientCreate(
            name="Get Client",
            email="getclient@test.com"
        )
        created_client = client_crud.create_client(db=test_db, client=client_data)
        
        # Get client
        fetched_client = client_crud.get_client(
            db=test_db,
            client_id=created_client.id
        )
        
        assert fetched_client is not None
        assert fetched_client.id == created_client.id
        assert fetched_client.name == "Get Client"
    
    @pytest.mark.db
    def test_update_client(self, test_db: Session):
        """Test updating client."""
        # Create client
        client_data = ClientCreate(
            name="Update Client",
            email="update@client.com"
        )
        client = client_crud.create_client(db=test_db, client=client_data)
        
        # Update client - using ClientUpdate schema
        update_data = ClientUpdate(
            email="updated@client.com",
            phone="+9876543210",
            company="Updated Company"
        )
        updated_client = client_crud.update_client(
            db=test_db,
            client_id=client.id,
            client_update=update_data
        )
        
        assert updated_client.email == "updated@client.com"
        assert updated_client.phone == "+9876543210"
        assert updated_client.company == "Updated Company"
        assert updated_client.name == "Update Client"  # Unchanged
    
    @pytest.mark.db
    def test_delete_client(self, test_db: Session):
        """Test deleting client."""
        # Create client
        client_data = ClientCreate(
            name="Delete Client",
            email="delete@client.com"
        )
        client = client_crud.create_client(db=test_db, client=client_data)
        client_id = client.id
        
        # Delete client
        result = client_crud.delete_client(db=test_db, client_id=client_id)
        assert result is True
        
        # Verify deleted
        deleted_client = client_crud.get_client(db=test_db, client_id=client_id)
        assert deleted_client is None


class TestContactCRUD:
    """Test contact CRUD operations."""
    
    @pytest.mark.db
    def test_create_contact(self, test_db: Session):
        """Test creating a contact."""
        contact_data = ContactCreate(
            name="CRUD Contact",
            email="crudcontact@test.com",
            phone="+1112223333",
            company="Contact Company",
            message="This is a test contact message"
        )
        
        contact = contact_crud.create_contact(db=test_db, contact=contact_data)
        
        assert contact.name == "CRUD Contact"
        assert contact.email == "crudcontact@test.com"
        assert contact.message == "This is a test contact message"
    
    @pytest.mark.db
    def test_get_contact_by_id(self, test_db: Session):
        """Test getting contact by ID."""
        # Create contact
        contact_data = ContactCreate(
            name="Get Contact",
            email="getcontact@test.com",
            message="Get contact test"
        )
        created_contact = contact_crud.create_contact(db=test_db, contact=contact_data)
        
        # Get contact
        fetched_contact = contact_crud.get_contact(
            db=test_db,
            contact_id=created_contact.id
        )
        
        assert fetched_contact is not None
        assert fetched_contact.id == created_contact.id
        assert fetched_contact.name == "Get Contact"
    
    @pytest.mark.db
    def test_get_contacts_list(self, test_db: Session):
        """Test getting list of contacts."""
        # Create multiple contacts
        for i in range(3):
            contact_data = ContactCreate(
                name=f"List Contact {i}",
                email=f"listcontact{i}@test.com",
                message=f"Message {i}"
            )
            contact_crud.create_contact(db=test_db, contact=contact_data)
        
        # Get all contacts
        contacts = contact_crud.get_contacts(db=test_db, skip=0, limit=100)
        
        assert len(contacts) >= 3
        names = [c.name for c in contacts]
        for i in range(3):
            assert f"List Contact {i}" in names 