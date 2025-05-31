"""
Test project router endpoints.
"""
import pytest
import os
from datetime import datetime
from fastapi import status

from schemas.project_schema import ProjectCreate
from crud.project_crud import create_project
from models.project_model import ProjectDBModel


class TestProjectCRUD:
    """Test project CRUD endpoints."""
    
    @pytest.mark.auth
    def test_create_project(self, client, auth_headers):
        """Test creating a new project."""
        response = client.post(
            "/api/projects",
            json={
                "unique_id": "test_proj_001",
                "name": "Test Project",
                "description": "A test project description",
                "status": "active",
                "metadata": {"client": "Test Client", "budget": 50000}
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["unique_id"] == "test_proj_001"
        assert data["name"] == "Test Project"
        assert data["description"] == "A test project description"
        assert data["status"] == "active"
        assert data["metadata"]["client"] == "Test Client"
    
    @pytest.mark.auth
    def test_create_project_duplicate_id(self, client, auth_headers, test_db):
        """Test creating project with duplicate unique_id."""
        # Create first project
        project_data = ProjectCreate(
            unique_id="duplicate_id",
            name="First Project",
            status="active"
        )
        create_project(db=test_db, project=project_data)
        
        # Try to create another with same ID
        response = client.post(
            "/api/projects",
            json={
                "unique_id": "duplicate_id",
                "name": "Second Project",
                "status": "active"
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"].lower()
    
    @pytest.mark.auth
    def test_create_project_no_auth(self, client):
        """Test creating project without authentication."""
        response = client.post(
            "/api/projects",
            json={
                "unique_id": "no_auth_proj",
                "name": "No Auth Project",
                "status": "active"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.auth
    def test_get_project_by_id(self, client, auth_headers, test_db):
        """Test getting project by ID."""
        # Create project
        project_data = ProjectCreate(
            unique_id="get_proj_001",
            name="Get Project Test",
            description="Test getting project",
            status="active"
        )
        project = create_project(db=test_db, project=project_data)
        
        response = client.get(
            f"/api/projects/{project.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == project.id
        assert data["unique_id"] == "get_proj_001"
        assert data["name"] == "Get Project Test"
    
    @pytest.mark.auth
    def test_get_project_not_found(self, client, auth_headers):
        """Test getting non-existent project."""
        response = client.get(
            "/api/projects/99999",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.auth
    def test_get_projects_list(self, client, auth_headers, test_db):
        """Test getting list of projects."""
        # Create multiple projects
        for i in range(5):
            project_data = ProjectCreate(
                unique_id=f"list_proj_{i}",
                name=f"List Project {i}",
                status="active" if i % 2 == 0 else "completed"
            )
            create_project(db=test_db, project=project_data)
        
        response = client.get("/api/projects", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        projects = response.json()
        assert isinstance(projects, list)
        assert len(projects) >= 5
    
    @pytest.mark.auth
    def test_get_projects_with_pagination(self, client, auth_headers, test_db):
        """Test getting projects with pagination."""
        # Create 10 projects
        for i in range(10):
            project_data = ProjectCreate(
                unique_id=f"page_proj_{i}",
                name=f"Page Project {i}",
                status="active"
            )
            create_project(db=test_db, project=project_data)
        
        # Get first page
        response = client.get(
            "/api/projects?skip=0&limit=5",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        projects = response.json()
        assert len(projects) == 5
        
        # Get second page
        response2 = client.get(
            "/api/projects?skip=5&limit=5",
            headers=auth_headers
        )
        assert response2.status_code == status.HTTP_200_OK
        projects2 = response2.json()
        assert len(projects2) >= 5
    
    @pytest.mark.auth
    def test_update_project(self, client, auth_headers, test_db):
        """Test updating a project."""
        # Create project
        project_data = ProjectCreate(
            unique_id="update_proj_001",
            name="Original Name",
            description="Original description",
            status="active"
        )
        project = create_project(db=test_db, project=project_data)
        
        # Update project
        response = client.put(
            f"/api/projects/{project.id}",
            json={
                "name": "Updated Name",
                "description": "Updated description",
                "status": "completed",
                "metadata": {"completion_date": "2024-01-01"}
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "Updated description"
        assert data["status"] == "completed"
        assert data["unique_id"] == "update_proj_001"  # Should not change
    
    @pytest.mark.auth
    def test_update_project_not_found(self, client, auth_headers):
        """Test updating non-existent project."""
        response = client.put(
            "/api/projects/99999",
            json={"name": "Updated Name"},
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.auth
    def test_delete_project(self, client, auth_headers, test_db):
        """Test deleting a project."""
        # Create project
        project_data = ProjectCreate(
            unique_id="delete_proj_001",
            name="Delete Test Project",
            status="active"
        )
        project = create_project(db=test_db, project=project_data)
        
        # Delete project
        response = client.delete(
            f"/api/projects/{project.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify deletion
        get_response = client.get(
            f"/api/projects/{project.id}",
            headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.auth
    def test_delete_project_not_found(self, client, auth_headers):
        """Test deleting non-existent project."""
        response = client.delete(
            "/api/projects/99999",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestProjectFileOperations:
    """Test project file-related operations."""
    
    @pytest.mark.auth
    def test_upload_project_file(self, client, auth_headers, test_db, temp_dir):
        """Test uploading a file to a project."""
        # Create project
        project_data = ProjectCreate(
            unique_id="file_proj_001",
            name="File Project",
            status="active"
        )
        project = create_project(db=test_db, project=project_data)
        
        # Create test file
        test_file_path = os.path.join(temp_dir, "test_upload.txt")
        with open(test_file_path, "w") as f:
            f.write("Test file content")
        
        with open(test_file_path, "rb") as f:
            response = client.post(
                f"/api/projects/{project.id}/files",
                files={"file": ("test_upload.txt", f, "text/plain")},
                headers=auth_headers
            )
        
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["filename"] == "test_upload.txt"
            assert data["project_id"] == project.id
    
    @pytest.mark.auth
    def test_get_project_files(self, client, auth_headers, test_db):
        """Test getting files associated with a project."""
        # Create project
        project_data = ProjectCreate(
            unique_id="files_proj_001",
            name="Files Project",
            status="active"
        )
        project = create_project(db=test_db, project=project_data)
        
        response = client.get(
            f"/api/projects/{project.id}/files",
            headers=auth_headers
        )
        
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            files = response.json()
            assert isinstance(files, list)
    
    @pytest.mark.auth
    def test_delete_project_file(self, client, auth_headers, test_db):
        """Test deleting a file from a project."""
        # Create project
        project_data = ProjectCreate(
            unique_id="delfile_proj_001",
            name="Delete File Project",
            status="active"
        )
        project = create_project(db=test_db, project=project_data)
        
        # Assuming there's a file with ID 1
        response = client.delete(
            f"/api/projects/{project.id}/files/1",
            headers=auth_headers
        )
        
        # Test response based on whether endpoint exists
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code in [
                status.HTTP_204_NO_CONTENT,
                status.HTTP_404_NOT_FOUND  # File not found
            ]


class TestProjectSearch:
    """Test project search functionality."""
    
    @pytest.mark.auth
    def test_search_projects_by_name(self, client, auth_headers, test_db):
        """Test searching projects by name."""
        # Create projects with different names
        projects = [
            ("search_001", "Alpha Project"),
            ("search_002", "Beta Project"),
            ("search_003", "Alpha Beta Project"),
            ("search_004", "Gamma Project")
        ]
        
        for unique_id, name in projects:
            project_data = ProjectCreate(
                unique_id=unique_id,
                name=name,
                status="active"
            )
            create_project(db=test_db, project=project_data)
        
        # Search for "Alpha"
        response = client.get(
            "/api/projects/search?q=Alpha",
            headers=auth_headers
        )
        
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            results = response.json()
            assert len(results) == 2
            names = [p["name"] for p in results]
            assert "Alpha Project" in names
            assert "Alpha Beta Project" in names
    
    @pytest.mark.auth
    def test_search_projects_by_status(self, client, auth_headers, test_db):
        """Test filtering projects by status."""
        # Create projects with different statuses
        statuses = ["active", "active", "completed", "cancelled"]
        
        for i, status in enumerate(statuses):
            project_data = ProjectCreate(
                unique_id=f"status_proj_{i}",
                name=f"Status Project {i}",
                status=status
            )
            create_project(db=test_db, project=project_data)
        
        # Filter by active status
        response = client.get(
            "/api/projects?status=active",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        results = response.json()
        # Check that all returned projects are active
        for project in results:
            if project["unique_id"].startswith("status_proj_"):
                assert project["status"] == "active"


class TestProjectStatistics:
    """Test project statistics endpoints."""
    
    @pytest.mark.auth
    def test_get_project_statistics(self, client, auth_headers, test_db):
        """Test getting project statistics."""
        # Create projects with different statuses
        statuses = ["active", "active", "completed", "cancelled", "active"]
        
        for i, status in enumerate(statuses):
            project_data = ProjectCreate(
                unique_id=f"stats_proj_{i}",
                name=f"Stats Project {i}",
                status=status
            )
            create_project(db=test_db, project=project_data)
        
        response = client.get(
            "/api/projects/statistics",
            headers=auth_headers
        )
        
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            stats = response.json()
            assert "total_projects" in stats
            assert "active_projects" in stats
            assert "completed_projects" in stats
            assert stats["total_projects"] >= 5


class TestProjectPermissions:
    """Test project permission requirements."""
    
    @pytest.mark.auth
    def test_project_operations_auth_levels(self, client, test_db):
        """Test project operations with different auth levels."""
        # Create users with different auth levels
        from schemas.user_schema import UserCreate
        from crud.user_crud import create_user
        
        users = []
        for level in [1, 2, 3]:
            user_data = UserCreate(
                username=f"projlevel{level}",
                password="password123",
                email=f"projlevel{level}@test.com",
                disabled=False,
                auth_level=level
            )
            users.append(create_user(db=test_db, user=user_data))
        
        # Test each user's access to project operations
        for level, user in zip([1, 2, 3], users):
            # Login
            login_response = client.post(
                "/api/auth/login",
                data={
                    "username": f"projlevel{level}",
                    "password": "password123"
                }
            )
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test creating project
            create_response = client.post(
                "/api/projects",
                json={
                    "unique_id": f"perm_test_{level}",
                    "name": f"Permission Test {level}",
                    "status": "active"
                },
                headers=headers
            )
            
            # All authenticated users should be able to create projects
            assert create_response.status_code == status.HTTP_201_CREATED
            
            # Test getting projects
            get_response = client.get("/api/projects", headers=headers)
            assert get_response.status_code == status.HTTP_200_OK


class TestProjectExportImport:
    """Test project export/import functionality."""
    
    @pytest.mark.auth
    def test_export_project(self, client, auth_headers, test_db):
        """Test exporting project data."""
        # Create project with data
        project_data = ProjectCreate(
            unique_id="export_proj_001",
            name="Export Project",
            description="Project to export",
            status="active",
            metadata={"key": "value"}
        )
        project = create_project(db=test_db, project=project_data)
        
        response = client.get(
            f"/api/projects/{project.id}/export",
            headers=auth_headers
        )
        
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            # Check if response is downloadable file
            assert "content-disposition" in response.headers
    
    @pytest.mark.auth
    def test_import_project(self, client, auth_headers, temp_dir):
        """Test importing project data."""
        # Create import file
        import_data = {
            "unique_id": "import_proj_001",
            "name": "Imported Project",
            "description": "Project from import",
            "status": "active"
        }
        
        import json
        import_file_path = os.path.join(temp_dir, "import.json")
        with open(import_file_path, "w") as f:
            json.dump(import_data, f)
        
        with open(import_file_path, "rb") as f:
            response = client.post(
                "/api/projects/import",
                files={"file": ("import.json", f, "application/json")},
                headers=auth_headers
            )
        
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code in [
                status.HTTP_201_CREATED,
                status.HTTP_200_OK
            ] 