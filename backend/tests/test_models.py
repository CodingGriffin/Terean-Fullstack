"""
Test database models.
"""
import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.user_model import UserDBModel
from models.project_model import ProjectDBModel
from models.sgy_file_model import SgyFileDBModel
from models.file_model import FileDBModel
from models.client_model import ClientDBModel
from models.contact_model import ContactDBModel


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
        expiration = datetime(2025, 12, 31, 23, 59, 59)
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
        project = ProjectDBModel(
            unique_id="proj123",
            name="Test Project",
            description="A test project",
            status="active",
            created_date=datetime.utcnow(),
            modified_date=datetime.utcnow()
        )
        test_db.add(project)
        test_db.commit()
        test_db.refresh(project)
        
        assert project.id is not None
        assert project.unique_id == "proj123"
        assert project.name == "Test Project"
        assert project.status == "active"
    
    @pytest.mark.db
    def test_project_metadata(self, test_db: Session):
        """Test project with metadata."""
        metadata = {
            "client": "Test Client",
            "location": "Test Location",
            "budget": 100000
        }
        project = ProjectDBModel(
            unique_id="proj456",
            name="Metadata Project",
            status="planning",
            metadata=metadata
        )
        test_db.add(project)
        test_db.commit()
        test_db.refresh(project)
        
        assert project.metadata == metadata
        assert project.metadata["client"] == "Test Client"
    
    @pytest.mark.db
    def test_project_relationships(self, test_db: Session):
        """Test project relationships with files."""
        project = ProjectDBModel(
            unique_id="proj789",
            name="Related Project",
            status="active"
        )
        test_db.add(project)
        test_db.commit()
        
        # Add a file to the project
        file = FileDBModel(
            unique_id="file123",
            filename="test.sgy",
            project_id=project.id
        )
        test_db.add(file)
        test_db.commit()
        test_db.refresh(project)
        
        assert len(project.files) == 1
        assert project.files[0].filename == "test.sgy"


class TestSgyFileModel:
    """Test SgyFileDBModel."""
    
    @pytest.mark.db
    def test_create_sgy_file(self, test_db: Session):
        """Test creating an SGY file."""
        sgy_file = SgyFileDBModel(
            filename="seismic_data.sgy",
            file_path="/data/seismic_data.sgy",
            file_size=1024000,
            upload_date=datetime.utcnow(),
            status="uploaded"
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
            upload_date=datetime.utcnow(),
            status="processed",
            metadata=metadata
        )
        test_db.add(sgy_file)
        test_db.commit()
        test_db.refresh(sgy_file)
        
        assert sgy_file.metadata == metadata
        assert sgy_file.metadata["traces"] == 1000
    
    @pytest.mark.db
    def test_sgy_file_processing_dates(self, test_db: Session):
        """Test SGY file processing dates."""
        upload_date = datetime.utcnow()
        process_start = datetime.utcnow()
        process_end = datetime.utcnow()
        
        sgy_file = SgyFileDBModel(
            filename="processed.sgy",
            file_path="/data/processed.sgy",
            file_size=512000,
            upload_date=upload_date,
            process_start_date=process_start,
            process_end_date=process_end,
            status="completed"
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
        file = FileDBModel(
            unique_id="file001",
            filename="document.pdf",
            file_path="/files/document.pdf",
            file_size=512000,
            upload_date=datetime.utcnow()
        )
        test_db.add(file)
        test_db.commit()
        test_db.refresh(file)
        
        assert file.id is not None
        assert file.unique_id == "file001"
        assert file.filename == "document.pdf"
    
    @pytest.mark.db
    def test_file_with_project(self, test_db: Session):
        """Test file associated with project."""
        # Create project first
        project = ProjectDBModel(
            unique_id="proj_file",
            name="File Project",
            status="active"
        )
        test_db.add(project)
        test_db.commit()
        
        # Create file with project
        file = FileDBModel(
            unique_id="file002",
            filename="project_doc.pdf",
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
            created_date=datetime.utcnow()
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
            created_date=datetime.utcnow()
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
            created_date=datetime.utcnow()
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
            created_date=datetime.utcnow()
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
            created_date=datetime.utcnow()
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
            created_date=datetime.utcnow()
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
        # Create project
        project = ProjectDBModel(
            unique_id="cascade_proj",
            name="Cascade Project",
            status="active"
        )
        test_db.add(project)
        test_db.commit()
        
        # Create files
        file1 = FileDBModel(
            unique_id="cascade_file1",
            filename="file1.txt",
            project_id=project.id
        )
        file2 = FileDBModel(
            unique_id="cascade_file2",
            filename="file2.txt",
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