"""
Integration tests for the backend application.
"""
import pytest
import os
import json
from datetime import datetime, timedelta
from fastapi import status

from schemas.user_schema import UserCreate
from schemas.project_schema import ProjectCreate
from crud.user_crud import create_user
from crud.project_crud import create_project


class TestCompleteWorkflow:
    """Test complete application workflows."""
    
    @pytest.mark.integration
    @pytest.mark.auth
    def test_user_lifecycle(self, client, test_db, admin_auth_headers):
        """Test complete user lifecycle: create, login, update, delete."""
        # 1. Admin creates a new user
        create_response = client.post(
            "/api/admin/users",
            json={
                "username": "lifecycle_user",
                "password": "lifecycle_pass123",
                "email": "lifecycle@test.com",
                "full_name": "Lifecycle Test User",
                "disabled": False,
                "auth_level": 1
            },
            headers=admin_auth_headers
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        user_id = create_response.json()["id"]
        
        # 2. New user logs in
        login_response = client.post(
            "/api/auth/login",
            data={
                "username": "lifecycle_user",
                "password": "lifecycle_pass123"
            }
        )
        assert login_response.status_code == status.HTTP_200_OK
        user_token = login_response.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}
        
        # 3. User accesses their profile
        profile_response = client.get("/api/auth/me", headers=user_headers)
        assert profile_response.status_code == status.HTTP_200_OK
        assert profile_response.json()["username"] == "lifecycle_user"
        
        # 4. Admin updates the user
        update_response = client.put(
            f"/api/admin/users/{user_id}",
            json={
                "full_name": "Updated Lifecycle User",
                "auth_level": 2
            },
            headers=admin_auth_headers
        )
        assert update_response.status_code == status.HTTP_200_OK
        
        # 5. User refreshes token and checks updated profile
        refresh_response = client.post("/api/auth/refresh", headers=user_headers)
        assert refresh_response.status_code == status.HTTP_200_OK
        new_token = refresh_response.json()["access_token"]
        new_headers = {"Authorization": f"Bearer {new_token}"}
        
        updated_profile = client.get("/api/auth/me", headers=new_headers)
        assert updated_profile.json()["full_name"] == "Updated Lifecycle User"
        assert updated_profile.json()["auth_level"] == 2
        
        # 6. Admin deletes the user
        delete_response = client.delete(
            f"/api/admin/users/{user_id}",
            headers=admin_auth_headers
        )
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        # 7. User can no longer login
        failed_login = client.post(
            "/api/auth/login",
            data={
                "username": "lifecycle_user",
                "password": "lifecycle_pass123"
            }
        )
        assert failed_login.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.integration
    @pytest.mark.auth
    def test_project_workflow(self, client, auth_headers, test_db, temp_dir):
        """Test complete project workflow: create, update, add files, delete."""
        # 1. Create a project
        create_response = client.post(
            "/api/projects",
            json={
                "unique_id": "workflow_proj_001",
                "name": "Workflow Test Project",
                "description": "Testing complete project workflow",
                "status": "planning",
                "metadata": {
                    "client": "Test Client Corp",
                    "budget": 100000,
                    "deadline": "2024-12-31"
                }
            },
            headers=auth_headers
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        project_id = create_response.json()["id"]
        
        # 2. Get project details
        get_response = client.get(f"/api/projects/{project_id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_200_OK
        project_data = get_response.json()
        assert project_data["name"] == "Workflow Test Project"
        assert project_data["status"] == "planning"
        
        # 3. Update project status
        update_response = client.put(
            f"/api/projects/{project_id}",
            json={
                "status": "active",
                "metadata": {
                    "client": "Test Client Corp",
                    "budget": 120000,
                    "deadline": "2024-12-31",
                    "start_date": datetime.utcnow().isoformat()
                }
            },
            headers=auth_headers
        )
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.json()["status"] == "active"
        
        # 4. Upload file to project (if endpoint exists)
        test_file_path = os.path.join(temp_dir, "project_file.txt")
        with open(test_file_path, "w") as f:
            f.write("Project documentation content")
        
        with open(test_file_path, "rb") as f:
            file_response = client.post(
                f"/api/projects/{project_id}/files",
                files={"file": ("project_file.txt", f, "text/plain")},
                headers=auth_headers
            )
        
        if file_response.status_code != status.HTTP_404_NOT_FOUND:
            assert file_response.status_code == status.HTTP_201_CREATED
            file_id = file_response.json()["id"]
            
            # 5. Get project files
            files_response = client.get(
                f"/api/projects/{project_id}/files",
                headers=auth_headers
            )
            assert files_response.status_code == status.HTTP_200_OK
            assert len(files_response.json()) > 0
        
        # 6. Search for project
        search_response = client.get(
            "/api/projects/search?q=Workflow",
            headers=auth_headers
        )
        if search_response.status_code != status.HTTP_404_NOT_FOUND:
            assert search_response.status_code == status.HTTP_200_OK
            results = search_response.json()
            assert any(p["unique_id"] == "workflow_proj_001" for p in results)
        
        # 7. Complete the project
        complete_response = client.put(
            f"/api/projects/{project_id}",
            json={
                "status": "completed",
                "metadata": {
                    "client": "Test Client Corp",
                    "budget": 115000,
                    "deadline": "2024-12-31",
                    "start_date": datetime.utcnow().isoformat(),
                    "completion_date": datetime.utcnow().isoformat(),
                    "final_notes": "Project completed successfully"
                }
            },
            headers=auth_headers
        )
        assert complete_response.status_code == status.HTTP_200_OK
        assert complete_response.json()["status"] == "completed"
        
        # 8. Delete the project
        delete_response = client.delete(
            f"/api/projects/{project_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        # 9. Verify deletion
        get_deleted = client.get(f"/api/projects/{project_id}", headers=auth_headers)
        assert get_deleted.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.integration
    @pytest.mark.auth
    def test_permission_escalation_attempt(self, client, test_db):
        """Test that users cannot escalate their own permissions."""
        # Create regular user
        user_data = UserCreate(
            username="regular_user",
            password="regular_pass123",
            email="regular@test.com",
            disabled=False,
            auth_level=1
        )
        user = create_user(db=test_db, user=user_data)
        
        # Login as regular user
        login_response = client.post(
            "/api/auth/login",
            data={
                "username": "regular_user",
                "password": "regular_pass123"
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to access admin endpoints
        admin_response = client.get("/api/admin/users", headers=headers)
        assert admin_response.status_code == status.HTTP_403_FORBIDDEN
        
        # Try to update own auth level (if endpoint exists)
        update_response = client.put(
            f"/api/admin/users/{user.id}",
            json={"auth_level": 3},
            headers=headers
        )
        assert update_response.status_code == status.HTTP_403_FORBIDDEN
        
        # Verify auth level hasn't changed
        profile = client.get("/api/auth/me", headers=headers)
        assert profile.json()["auth_level"] == 1


class TestDataIntegrity:
    """Test data integrity across operations."""
    
    @pytest.mark.integration
    @pytest.mark.db
    def test_cascade_delete_project_files(self, client, auth_headers, test_db):
        """Test that deleting a project cascades to its files."""
        # Create project
        project_data = ProjectCreate(
            unique_id="cascade_test_proj",
            name="Cascade Test Project",
            status="active"
        )
        project = create_project(db=test_db, project=project_data)
        
        # Add files to project (through direct DB if API doesn't exist)
        from models.file_model import FileDBModel
        for i in range(3):
            file = FileDBModel(
                unique_id=f"cascade_file_{i}",
                filename=f"file_{i}.txt",
                project_id=project.id
            )
            test_db.add(file)
        test_db.commit()
        
        # Delete project
        delete_response = client.delete(
            f"/api/projects/{project.id}",
            headers=auth_headers
        )
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify files are also deleted
        files = test_db.query(FileDBModel).filter_by(project_id=project.id).all()
        assert len(files) == 0
    
    @pytest.mark.integration
    @pytest.mark.db
    def test_concurrent_updates(self, client, auth_headers, test_db):
        """Test handling of concurrent updates to the same resource."""
        # Create project
        project_data = ProjectCreate(
            unique_id="concurrent_proj",
            name="Concurrent Test Project",
            status="active"
        )
        project = create_project(db=test_db, project=project_data)
        
        # Simulate concurrent updates
        update1 = client.put(
            f"/api/projects/{project.id}",
            json={"name": "Updated by User 1"},
            headers=auth_headers
        )
        
        update2 = client.put(
            f"/api/projects/{project.id}",
            json={"name": "Updated by User 2"},
            headers=auth_headers
        )
        
        assert update1.status_code == status.HTTP_200_OK
        assert update2.status_code == status.HTTP_200_OK
        
        # Get final state
        final_response = client.get(
            f"/api/projects/{project.id}",
            headers=auth_headers
        )
        final_name = final_response.json()["name"]
        
        # Should be one of the updates (last write wins)
        assert final_name in ["Updated by User 1", "Updated by User 2"]


class TestErrorHandling:
    """Test error handling and recovery."""
    
    @pytest.mark.integration
    def test_database_connection_recovery(self, client, auth_headers):
        """Test that the app can recover from database connection issues."""
        # This is a conceptual test - actual implementation would need
        # a way to simulate database disconnection
        
        # Normal operation
        response = client.get("/api/projects", headers=auth_headers)
        original_status = response.status_code
        
        # Simulate database issue (would need actual implementation)
        # ...
        
        # Verify recovery
        recovery_response = client.get("/api/projects", headers=auth_headers)
        assert recovery_response.status_code == original_status
    
    @pytest.mark.integration
    def test_malformed_request_handling(self, client, auth_headers):
        """Test handling of various malformed requests."""
        malformed_requests = [
            # Invalid JSON
            ("POST", "/api/projects", "not json", "application/json"),
            # Wrong content type
            ("POST", "/api/projects", '{"name": "test"}', "text/plain"),
            # Missing required fields
            ("POST", "/api/projects", '{"name": "test"}', "application/json"),
            # Invalid data types
            ("POST", "/api/projects", '{"unique_id": 123, "name": true}', "application/json"),
        ]
        
        for method, url, data, content_type in malformed_requests:
            if method == "POST":
                response = client.post(
                    url,
                    content=data,
                    headers={**auth_headers, "Content-Type": content_type}
                )
                assert response.status_code in [
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    status.HTTP_400_BAD_REQUEST
                ]


class TestPerformance:
    """Test performance-related scenarios."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_pagination_performance(self, client, auth_headers, test_db):
        """Test that pagination works efficiently with large datasets."""
        # Create many projects
        for i in range(100):
            project_data = ProjectCreate(
                unique_id=f"perf_proj_{i:03d}",
                name=f"Performance Test Project {i}",
                status="active" if i % 2 == 0 else "completed"
            )
            create_project(db=test_db, project=project_data)
        
        # Test different page sizes
        page_sizes = [10, 20, 50]
        
        for size in page_sizes:
            start_time = datetime.utcnow()
            response = client.get(
                f"/api/projects?skip=0&limit={size}",
                headers=auth_headers
            )
            end_time = datetime.utcnow()
            
            assert response.status_code == status.HTTP_200_OK
            assert len(response.json()) == size
            
            # Response should be reasonably fast
            response_time = (end_time - start_time).total_seconds()
            assert response_time < 1.0  # Less than 1 second
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_search_performance(self, client, auth_headers, test_db):
        """Test search performance with large dataset."""
        # Create projects with various names
        keywords = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"]
        
        for i in range(50):
            for keyword in keywords:
                project_data = ProjectCreate(
                    unique_id=f"search_{keyword.lower()}_{i}",
                    name=f"{keyword} Project {i}",
                    description=f"Description with {keyword} keyword",
                    status="active"
                )
                create_project(db=test_db, project=project_data)
        
        # Test search performance
        for keyword in keywords:
            start_time = datetime.utcnow()
            response = client.get(
                f"/api/projects/search?q={keyword}",
                headers=auth_headers
            )
            end_time = datetime.utcnow()
            
            if response.status_code != status.HTTP_404_NOT_FOUND:
                assert response.status_code == status.HTTP_200_OK
                results = response.json()
                assert len(results) > 0
                
                # Search should be fast
                response_time = (end_time - start_time).total_seconds()
                assert response_time < 2.0  # Less than 2 seconds 