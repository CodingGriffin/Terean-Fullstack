"""
Test database models.
"""
import pytest
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.user_model import UserDBModel
from models.project_model import ProjectDBModel
from models.sgy_file_model import SgyFileDBModel
from models.file_model import FileDBModel
from models.client_model import ClientDBModel
from models.contact_model import ContactDBModel
from utils.custom_types.ProjectStatus import ProjectStatus


class TestUserModel:
    """Test UserDBModel."""
    
    @pytest.mark.db
    def test_create_user(self, test_db: Session):
        """Test creating a user."""
        user = UserDBModel(
            username="modeltest",
            hashed_password="hashedpassword123",
            disabled=False,
            auth_level=1,
            email="model@test.com",
            full_name="Model Test User"
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        assert user.id is not None
        assert user.username == "modeltest"
        assert user.email == "model@test.com"
        assert user.auth_level == 1
        assert user.disabled is False
    
    @pytest.mark.db
    def test_user_unique_username(self, test_db: Session):
        """Test that usernames must be unique."""
        user1 = UserDBModel(
            username="duplicate",
            hashed_password="hash1",
            disabled=False,
            auth_level=1
        )
        user2 = UserDBModel(
            username="duplicate",
            hashed_password="hash2",
            disabled=False,
            auth_level=1
        )
        
        test_db.add(user1)
        test_db.commit()
        
        test_db.add(user2)
        with pytest.raises(IntegrityError):
            test_db.commit()
    
    @pytest.mark.db
    def test_user_optional_fields(self, test_db: Session):
        """Test user with optional fields."""
        user = UserDBModel(
            username="minimal",
            hashed_password="hash",
            disabled=False,
            auth_level=1
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        assert user.email is None
        assert user.full_name is None
        assert user.expiration is None
    
    @pytest.mark.db
    def test_user_with_expiration(self, test_db: Session):
        """Test user with expiration date."""
        expiration = datetime(2025, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        user = UserDBModel(
            username="expiring",
            hashed_password="hash",
            disabled=False,
            auth_level=2,
            expiration=expiration
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        assert user.expiration == expiration


class TestProjectModel:
    """Test ProjectDBModel."""
    
    @pytest.mark.db
    def test_create_project(self, test_db: Session):
        """Test creating a project."""
        # First create a user to be the owner
        user = UserDBModel(
            username="projectowner",
            hashed_password="hash",
            disabled=False,
            auth_level=1
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        project = ProjectDBModel(
            name="Test Project",
            description="A test project",
            status=ProjectStatus.not_started,
            created_date=datetime.now(timezone.utc),
            modified_date=datetime.now(timezone.utc),
            owner_id=user.id
        )
        test_db.add(project)
        test_db.commit()
        test_db.refresh(project)
        
        assert project.id is not None
        assert project.name == "Test Project"
        assert project.status == ProjectStatus.not_started
        assert project.owner_id == user.id
    
    @pytest.mark.db
    def test_project_different_statuses(self, test_db: Session):
        """Test project with different status values."""
        # Create owner
        user = UserDBModel(
            username="statusowner",
            hashed_password="hash",
            disabled=False,
            auth_level=1
        )
        test_db.add(user)
        test_db.commit()
        
        # Test each valid status
        for status in [ProjectStatus.not_started, ProjectStatus.in_progress, 
                      ProjectStatus.completed, ProjectStatus.blocked]:
            project = ProjectDBModel(
                name=f"Project {status.value}",
                status=status,
                owner_id=user.id
            )
            test_db.add(project)
            test_db.commit()
            test_db.refresh(project)
            
            assert project.status == status
    
    @pytest.mark.db
    def test_project_relationships(self, test_db: Session):
        """Test project relationships with files."""
        # Create owner
        user = UserDBModel(
            username="relowner",
            hashed_password="hash",
            disabled=False,
            auth_level=1
        )
        test_db.add(user)
        test_db.commit()
        
        project = ProjectDBModel(
            name="Related Project",
            status=ProjectStatus.in_progress,
            owner_id=user.id
        )
        test_db.add(project)
        test_db.commit()
        
        # Add a file to the project
        file = FileDBModel(
            id="file123",
            original_name="test.sgy",
            path="/data/test.sgy",
            size=1024,
            mime_type="application/octet-stream",
            file_extension=".sgy",
            project_id=project.id
        )
        test_db.add(file)
        test_db.commit()
        test_db.refresh(project)
        
        assert len(project.additional_files) == 1
        assert project.additional_files[0].original_name == "test.sgy"


class TestSgyFileModel:
    """Test SgyFileDBModel."""
    
    @pytest.mark.db
    def test_create_sgy_file(self, test_db: Session):
        """Test creating an SGY file."""
        # Create user and project first
        user = UserDBModel(
            username="sgyowner",
            hashed_password="hash",
            disabled=False,
            auth_level=1
        )
        test_db.add(user)
        test_db.commit()
        
        project = ProjectDBModel(
            name="SGY Project",
            status=ProjectStatus.in_progress,
            owner_id=user.id
        )
        test_db.add(project)
        test_db.commit()
        
        sgy_file = SgyFileDBModel(
            filename="seismic_data.sgy",
            file_path="/data/seismic_data.sgy",
            file_size=1024000,
            upload_date=datetime.now(timezone.utc),
            status="uploaded",
            project_id=project.id,
            user_id=user.id
        )
        test_db.add(sgy_file)
        test_db.commit()
        test_db.refresh(sgy_file)
        
        assert sgy_file.id is not None
        assert sgy_file.filename == "seismic_data.sgy"
        assert sgy_file.file_size == 1024000
        assert sgy_file.status == "uploaded"
    
    @pytest.mark.db
    def test_sgy_file_with_metadata(self, test_db: Session):
        """Test SGY file with metadata."""
        # Create user and project
        user = UserDBModel(
            username="metaowner",
            hashed_password="hash",
            disabled=False,
            auth_level=1
        )
        test_db.add(user)
        test_db.commit()
        
        project = ProjectDBModel(
            name="Meta Project",
            status=ProjectStatus.in_progress,
            owner_id=user.id
        )
        test_db.add(project)
        test_db.commit()
        
        metadata = {
            "traces": 1000,
            "samples": 2000,
            "sample_rate": 0.002,
            "format": "IEEE"
        }
        sgy_file = SgyFileDBModel(
            filename="metadata.sgy",
            file_path="/data/metadata.sgy",
            file_size=2048000,
            upload_date=datetime.now(timezone.utc),
            status="processed",
            metadata=metadata,
            project_id=project.id,
            user_id=user.id
        )
        test_db.add(sgy_file)
        test_db.commit()
        test_db.refresh(sgy_file)
        
        assert sgy_file.metadata == metadata
        assert sgy_file.metadata["traces"] == 1000
    
    @pytest.mark.db
    def test_sgy_file_processing_dates(self, test_db: Session):
        """Test SGY file processing dates."""
        # Create user and project
        user = UserDBModel(
            username="procowner",
            hashed_password="hash",
            disabled=False,
            auth_level=1
        )
        test_db.add(user)
        test_db.commit()
        
        project = ProjectDBModel(
            name="Process Project",
            status=ProjectStatus.in_progress,
            owner_id=user.id
        )
        test_db.add(project)
        test_db.commit()
        
        upload_date = datetime.now(timezone.utc)
        process_start = datetime.now(timezone.utc)
        process_end = datetime.now(timezone.utc)
        
        sgy_file = SgyFileDBModel(
            filename="processed.sgy",
            file_path="/data/processed.sgy",
            file_size=512000,
            upload_date=upload_date,
            process_start_date=process_start,
            process_end_date=process_end,
            status="completed",
            project_id=project.id,
            user_id=user.id
        )
        test_db.add(sgy_file)
        test_db.commit()
        test_db.refresh(sgy_file)
        
        assert sgy_file.process_start_date == process_start
        assert sgy_file.process_end_date == process_end


class TestFileModel:
    """Test FileDBModel."""
    
    @pytest.mark.db
    def test_create_file(self, test_db: Session):
        """Test creating a file."""
        # Create owner and project
        user = UserDBModel(
            username="fileowner",
            hashed_password="hash",
            disabled=False,
            auth_level=1
        )
        test_db.add(user)
        test_db.commit()
        
        project = ProjectDBModel(
            name="File Project",
            status=ProjectStatus.in_progress,
            owner_id=user.id
        )
        test_db.add(project)
        test_db.commit()
        
        file = FileDBModel(
            id="file001",
            original_name="document.pdf",
            path="/files/document.pdf",
            size=512000,
            upload_date=datetime.now(timezone.utc),
            mime_type="application/pdf",
            file_extension=".pdf",
            project_id=project.id
        )
        test_db.add(file)
        test_db.commit()
        test_db.refresh(file)
        
        assert file.id == "file001"
        assert file.original_name == "document.pdf"
        assert file.size == 512000
    
    @pytest.mark.db
    def test_file_with_project(self, test_db: Session):
        """Test file associated with project."""
        # Create user and project first
        user = UserDBModel(
            username="projfileowner",
            hashed_password="hash",
            disabled=False,
            auth_level=1
        )
        test_db.add(user)
        test_db.commit()
        
        project = ProjectDBModel(
            name="File Project",
            status=ProjectStatus.completed,
            owner_id=user.id
        )
        test_db.add(project)
        test_db.commit()
        
        # Create file with project
        file = FileDBModel(
            id="file002",
            original_name="project_doc.pdf",
            path="/files/project_doc.pdf",
            size=256000,
            mime_type="application/pdf",
            file_extension=".pdf",
            project_id=project.id
        )
        test_db.add(file)
        test_db.commit()
        test_db.refresh(file)
        
        assert file.project_id == project.id
        assert file.project.name == "File Project"


class TestClientModel:
    """Test ClientDBModel."""
    
    @pytest.mark.db
    def test_create_client(self, test_db: Session):
        """Test creating a client."""
        client = ClientDBModel(
            name="Test Client Inc.",
            email="client@test.com",
            phone="+1234567890",
            created_date=datetime.now(timezone.utc)
        )
        test_db.add(client)
        test_db.commit()
        test_db.refresh(client)
        
        assert client.id is not None
        assert client.name == "Test Client Inc."
        assert client.email == "client@test.com"
    
    @pytest.mark.db
    def test_client_optional_fields(self, test_db: Session):
        """Test client with optional fields."""
        client = ClientDBModel(
            name="Minimal Client",
            created_date=datetime.now(timezone.utc)
        )
        test_db.add(client)
        test_db.commit()
        test_db.refresh(client)
        
        assert client.email is None
        assert client.phone is None
        assert client.company is None
        assert client.address is None
    
    @pytest.mark.db
    def test_client_full_details(self, test_db: Session):
        """Test client with all details."""
        client = ClientDBModel(
            name="Full Detail Client",
            email="full@client.com",
            phone="+9876543210",
            company="Full Company Ltd.",
            address="123 Main St, City, Country",
            created_date=datetime.now(timezone.utc)
        )
        test_db.add(client)
        test_db.commit()
        test_db.refresh(client)
        
        assert client.company == "Full Company Ltd."
        assert client.address == "123 Main St, City, Country"


class TestContactModel:
    """Test ContactDBModel."""
    
    @pytest.mark.db
    def test_create_contact(self, test_db: Session):
        """Test creating a contact."""
        contact = ContactDBModel(
            name="John Doe",
            email="john@example.com",
            message="Test inquiry message",
            created_date=datetime.now(timezone.utc)
        )
        test_db.add(contact)
        test_db.commit()
        test_db.refresh(contact)
        
        assert contact.id is not None
        assert contact.name == "John Doe"
        assert contact.message == "Test inquiry message"
    
    @pytest.mark.db
    def test_contact_optional_fields(self, test_db: Session):
        """Test contact with optional fields."""
        contact = ContactDBModel(
            name="Jane Doe",
            email="jane@example.com",
            created_date=datetime.now(timezone.utc)
        )
        test_db.add(contact)
        test_db.commit()
        test_db.refresh(contact)
        
        assert contact.phone is None
        assert contact.company is None
        assert contact.message is None
    
    @pytest.mark.db
    def test_contact_with_company(self, test_db: Session):
        """Test contact with company information."""
        contact = ContactDBModel(
            name="Corporate Contact",
            email="corp@company.com",
            phone="+1112223333",
            company="Big Corp Inc.",
            message="Business inquiry",
            created_date=datetime.now(timezone.utc)
        )
        test_db.add(contact)
        test_db.commit()
        test_db.refresh(contact)
        
        assert contact.company == "Big Corp Inc."
        assert contact.phone == "+1112223333"


class TestModelRelationships:
    """Test relationships between models."""
    
    @pytest.mark.db
    def test_project_file_cascade_delete(self, test_db: Session):
        """Test cascade delete of files when project is deleted."""
        # Create user and project
        user = UserDBModel(
            username="cascadeowner",
            hashed_password="hash",
            disabled=False,
            auth_level=1
        )
        test_db.add(user)
        test_db.commit()
        
        project = ProjectDBModel(
            name="Cascade Project",
            status=ProjectStatus.not_started,
            owner_id=user.id
        )
        test_db.add(project)
        test_db.commit()
        
        # Create files
        file1 = FileDBModel(
            id="cascade_file1",
            original_name="file1.txt",
            path="/files/file1.txt",
            size=1024,
            mime_type="text/plain",
            file_extension=".txt",
            project_id=project.id
        )
        file2 = FileDBModel(
            id="cascade_file2",
            original_name="file2.txt",
            path="/files/file2.txt",
            size=2048,
            mime_type="text/plain",
            file_extension=".txt",
            project_id=project.id
        )
        test_db.add_all([file1, file2])
        test_db.commit()
        
        # Delete project
        test_db.delete(project)
        test_db.commit()
        
        # Check files are deleted
        files = test_db.query(FileDBModel).filter_by(
            project_id=project.id
        ).all()
        assert len(files) == 0 