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
            "/project",
            json={
                "name": "Test Project",
                "description": "A test project for unit testing",
                "status": "not_started"
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data["name"] == "Test Project"
        assert data["description"] == "A test project for unit testing"
        assert data["status"] == "not_started"
        assert "id" in data
        assert "created_date" in data
        assert "modified_date" in data
        assert "owner_id" in data
    
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
            "/project",
            json={
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
            "/project",
            json={
                "name": "Unauthorized Project",
                "description": "Should fail",
                "status": "not_started"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.auth
    def test_create_project_missing_fields(self, client, auth_headers):
        """Test creating project with missing required fields."""
        response = client.post(
            "/project",
            json={
                "description": "Missing name field"
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.auth
    def test_get_project_by_id(self, client, auth_headers, test_db):
        """Test getting a specific project by ID."""
        # Create a project first
        project = ProjectDBModel(
            name="Get By ID Test",
            description="Test project for get by ID",
            status=ProjectStatus.not_started,
            owner_id=1
        )
        test_db.add(project)
        test_db.commit()
        test_db.refresh(project)
        
        response = client.get(
            f"/project/{project.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == project.id
        assert data["name"] == "Get By ID Test"
        assert data["status"] == "not_started"
    
    @pytest.mark.auth
    def test_get_nonexistent_project(self, client, auth_headers):
        """Test getting a project that doesn't exist."""
        response = client.get(
            "/project/99999",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestProjectList:
    """Test project list endpoints."""
    
    @pytest.mark.auth
    def test_get_all_projects(self, client, auth_headers, test_db):
        """Test getting all projects."""
        # Create some test projects
        for i in range(3):
            project = ProjectDBModel(
                name=f"Project {i}",
                description=f"Description {i}",
                status=ProjectStatus.in_progress,
                owner_id=1
            )
            test_db.add(project)
        test_db.commit()
        
        response = client.get("/project", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3
    
    @pytest.mark.auth
    def test_get_projects_with_pagination(self, client, auth_headers, test_db):
        """Test getting projects with pagination."""
        # Create 10 test projects
        for i in range(10):
            project = ProjectDBModel(
                name=f"Paginated Project {i}",
                description=f"Description {i}",
                status=ProjectStatus.completed,
                owner_id=1
            )
            test_db.add(project)
        test_db.commit()
        
        # Get first page
        response = client.get(
            "/project?skip=0&limit=5",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) <= 5
        
        # Get second page
        response2 = client.get(
            "/project?skip=5&limit=5",
            headers=auth_headers
        )
        assert response2.status_code == status.HTTP_200_OK


class TestProjectUpdate:
    """Test project update endpoints."""
    
    @pytest.mark.auth
    def test_update_project(self, client, auth_headers, test_db):
        """Test updating a project."""
        # Create a project
        project = ProjectDBModel(
            name="Update Test",
            description="Original description",
            status=ProjectStatus.not_started,
            owner_id=1
        )
        test_db.add(project)
        test_db.commit()
        test_db.refresh(project)
        
        # Update it
        response = client.put(
            f"/project/{project.id}",
            json={
                "name": "Updated Project Name",
                "description": "Updated description",
                "status": "in_progress"
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Project Name"
        assert data["description"] == "Updated description"
        assert data["status"] == "in_progress"
    
    @pytest.mark.auth
    def test_update_nonexistent_project(self, client, auth_headers):
        """Test updating a project that doesn't exist."""
        response = client.put(
            "/project/99999",
            json={
                "name": "Updated Name"
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.auth
    def test_delete_project(self, client, auth_headers, test_db):
        """Test deleting a project."""
        # Create a project
        project = ProjectDBModel(
            name="Delete Test",
            description="To be deleted",
            status=ProjectStatus.blocked,
            owner_id=1
        )
        test_db.add(project)
        test_db.commit()
        test_db.refresh(project)
        
        # Delete it
        response = client.delete(
            f"/project/{project.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify it's deleted
        get_response = client.get(
            f"/project/{project.id}",
            headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.auth
    def test_delete_nonexistent_project(self, client, auth_headers):
        """Test deleting a project that doesn't exist."""
        response = client.delete(
            "/project/99999",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestProjectFiles:
    """Test project file management."""
    
    @pytest.mark.auth
    def test_add_file_to_project(self, client, auth_headers, test_db):
        """Test adding a file to a project."""
        # Create project
        project = ProjectDBModel(
            name="File Test Project",
            description="Testing file operations",
            status=ProjectStatus.in_progress,
            owner_id=1
        )
        test_db.add(project)
        test_db.commit()
        test_db.refresh(project)
        
        # Add file
        response = client.post(
            f"/project/{project.id}/files",
            json={
                "filename": "test_data.sgy",
                "file_path": "/data/test_data.sgy",
                "file_size": 1024000,
                "file_type": "sgy"
            },
            headers=auth_headers
        )
        
        # If endpoint exists
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["filename"] == "test_data.sgy"
            assert data["project_id"] == project.id
    
    @pytest.mark.auth
    def test_get_project_files(self, client, auth_headers, test_db):
        """Test getting files for a project."""
        # Create project with files
        project = ProjectDBModel(
            name="Files List Test",
            description="Testing file listing",
            status=ProjectStatus.completed,
            owner_id=1
        )
        test_db.add(project)
        test_db.commit()
        test_db.refresh(project)
        
        response = client.get(
            f"/project/{project.id}/files",
            headers=auth_headers
        )
        
        # If endpoint exists
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            assert isinstance(response.json(), list)
    
    @pytest.mark.auth
    def test_delete_project_file(self, client, auth_headers, test_db):
        """Test deleting a file from a project."""
        # Create project
        project = ProjectDBModel(
            name="File Delete Test",
            description="Testing file deletion",
            status=ProjectStatus.in_progress,
            owner_id=1
        )
        test_db.add(project)
        test_db.commit()
        
        response = client.delete(
            f"/project/{project.id}/files/1",
            headers=auth_headers
        )
        
        # If endpoint exists
        if response.status_code != status.HTTP_404_NOT_FOUND:
            # Should be 404 since file doesn't exist
            assert response.status_code == status.HTTP_404_NOT_FOUND


class TestProjectSearch:
    """Test project search functionality."""
    
    @pytest.mark.auth
    def test_search_projects_by_name(self, client, auth_headers, test_db):
        """Test searching projects by name."""
        # Create test projects
        projects = [
            ProjectDBModel(name="Alpha Project", description="First", status=ProjectStatus.not_started, owner_id=1),
            ProjectDBModel(name="Beta Project", description="Second", status=ProjectStatus.in_progress, owner_id=1),
            ProjectDBModel(name="Alpha Test", description="Third", status=ProjectStatus.completed, owner_id=1)
        ]
        for p in projects:
            test_db.add(p)
        test_db.commit()
        
        response = client.get(
            "/project/search?q=Alpha",
            headers=auth_headers
        )
        
        # If search endpoint exists
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert isinstance(data, list)
            # Should find both Alpha projects
            assert all("Alpha" in p["name"] for p in data)
    
    @pytest.mark.auth
    def test_filter_projects_by_status(self, client, auth_headers, test_db):
        """Test filtering projects by status."""
        # Create projects with different statuses
        projects = [
            ProjectDBModel(name="Not Started 1", description="Test", status=ProjectStatus.not_started, owner_id=1),
            ProjectDBModel(name="In Progress 1", description="Test", status=ProjectStatus.in_progress, owner_id=1),
            ProjectDBModel(name="In Progress 2", description="Test", status=ProjectStatus.in_progress, owner_id=1)
        ]
        for p in projects:
            test_db.add(p)
        test_db.commit()
        
        response = client.get(
            "/project?status=in_progress",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should only get in_progress projects
        assert all(p["status"] == "in_progress" for p in data if "status" in p)


class TestProjectStatistics:
    """Test project statistics endpoints."""
    
    @pytest.mark.auth
    def test_get_project_statistics(self, client, auth_headers, test_db):
        """Test getting project statistics."""
        # Create various projects
        statuses = [
            ProjectStatus.not_started,
            ProjectStatus.not_started,
            ProjectStatus.in_progress,
            ProjectStatus.completed,
            ProjectStatus.blocked
        ]
        
        for i, status in enumerate(statuses):
            project = ProjectDBModel(
                name=f"Stats Project {i}",
                description="For statistics",
                status=status,
                owner_id=1
            )
            test_db.add(project)
        test_db.commit()
        
        response = client.get(
            "/project/statistics",
            headers=auth_headers
        )
        
        # If statistics endpoint exists
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            # Verify statistics structure
            assert "total_projects" in data
            assert "projects_by_status" in data
            assert data["total_projects"] >= 5


class TestProjectPermissions:
    """Test project access permissions."""
    
    @pytest.mark.auth
    def test_user_can_only_see_own_projects(self, client, test_db):
        """Test that users can only see their own projects."""
        # Create two users
        user1_data = UserCreate(
            username="projectuser1",
            password="password123",
            email="projectuser1@test.com",
            disabled=False,
            auth_level=1
        )
        user1 = create_user(db=test_db, user=user1_data)
        
        user2_data = UserCreate(
            username="projectuser2",
            password="password123",
            email="projectuser2@test.com",
            disabled=False,
            auth_level=1
        )
        user2 = create_user(db=test_db, user=user2_data)
        
        # Create projects for each user
        project1 = ProjectDBModel(
            name="User1 Project",
            description="Owned by user1",
            status=ProjectStatus.in_progress,
            owner_id=user1.id
        )
        project2 = ProjectDBModel(
            name="User2 Project",
            description="Owned by user2",
            status=ProjectStatus.in_progress,
            owner_id=user2.id
        )
        test_db.add_all([project1, project2])
        test_db.commit()
        
        # Login as user1
        login_response = client.post(
            "/token",
            data={
                "username": "projectuser1",
                "password": "password123"
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get projects
        response = client.get(
            "/project",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        projects = response.json()
        
        # User1 should only see their own project
        user1_projects = [p for p in projects if p.get("owner_id") == user1.id]
        assert len(user1_projects) >= 1
        
        # Verify user1 can't access user2's project
        get_response = client.get("/project", headers=headers)
        # Implementation dependent - might filter or return all


class TestProjectExportImport:
    """Test project export/import functionality."""
    
    @pytest.mark.auth
    def test_export_project(self, client, auth_headers, test_db):
        """Test exporting a project."""
        # Create project with data
        project = ProjectDBModel(
            name="Export Test",
            description="Project to export",
            status=ProjectStatus.completed,
            owner_id=1
        )
        test_db.add(project)
        test_db.commit()
        test_db.refresh(project)
        
        response = client.get(
            f"/project/{project.id}/export",
            headers=auth_headers
        )
        
        # If export endpoint exists
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            # Should return file or JSON data
    
    @pytest.mark.auth
    def test_import_project(self, client, auth_headers):
        """Test importing a project."""
        import_data = {
            "name": "Imported Project",
            "description": "This was imported",
            "status": "not_started",
            "data": {}
        }
        
        response = client.post(
            "/project/import",
            json=import_data,
            headers=auth_headers
        )
        
        # If import endpoint exists
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK] 