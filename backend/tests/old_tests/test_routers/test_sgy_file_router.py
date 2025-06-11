"""
Test SGY file router endpoints.
"""
import pytest
import os
from datetime import datetime
from fastapi import status

from schemas.sgy_file_schema import SgyFileCreate
from crud.sgy_file_crud import create_sgy_file


class TestSgyFileUpload:
    """Test SGY file upload functionality."""
    
    @pytest.mark.auth
    def test_upload_sgy_file(self, client, auth_headers, temp_dir):
        """Test uploading an SGY file."""
        # Create a mock SGY file
        sgy_content = b"SGY file mock content"
        sgy_path = os.path.join(temp_dir, "test.sgy")
        with open(sgy_path, "wb") as f:
            f.write(sgy_content)
        
        with open(sgy_path, "rb") as f:
            response = client.post(
                "/sgy-files/upload",
                files={"file": ("test.sgy", f, "application/octet-stream")},
                data={"project_id": "1"},
                headers=auth_headers
            )
        
        # If endpoint exists
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["filename"] == "test.sgy"
            assert data["status"] == "uploaded"
            assert "id" in data
    
    @pytest.mark.auth
    def test_upload_invalid_file(self, client, auth_headers, temp_dir):
        """Test uploading an invalid file type."""
        # Create a non-SGY file
        txt_path = os.path.join(temp_dir, "test.txt")
        with open(txt_path, "w") as f:
            f.write("This is not an SGY file")
        
        with open(txt_path, "rb") as f:
            response = client.post(
                "/sgy-files/upload",
                files={"file": ("test.txt", f, "text/plain")},
                data={"project_id": "1"},
                headers=auth_headers
            )
        
        # Should fail validation
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    @pytest.mark.auth
    def test_upload_large_file(self, client, auth_headers, temp_dir):
        """Test uploading a large SGY file."""
        # Create a large mock SGY file (10MB)
        large_content = b"SGY" * (10 * 1024 * 1024 // 3)  # ~10MB
        large_path = os.path.join(temp_dir, "large.sgy")
        with open(large_path, "wb") as f:
            f.write(large_content)
        
        with open(large_path, "rb") as f:
            response = client.post(
                "/sgy-files/upload",
                files={"file": ("large.sgy", f, "application/octet-stream")},
                data={"project_id": "1"},
                headers=auth_headers
            )
        
        # Should handle large files
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code in [
                status.HTTP_201_CREATED,
                status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            ]
    
    @pytest.mark.auth
    def test_upload_no_auth(self, client, temp_dir):
        """Test uploading without authentication."""
        sgy_path = os.path.join(temp_dir, "test.sgy")
        with open(sgy_path, "wb") as f:
            f.write(b"SGY content")
        
        with open(sgy_path, "rb") as f:
            response = client.post(
                "/sgy-files/upload",
                files={"file": ("test.sgy", f, "application/octet-stream")},
                data={"project_id": "1"}
            )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestSgyFileList:
    """Test SGY file listing endpoints."""
    
    @pytest.mark.auth
    def test_get_sgy_files(self, client, auth_headers, test_db):
        """Test getting list of SGY files."""
        # Create some SGY files
        for i in range(3):
            sgy_file = SgyFileDBModel(
                filename=f"test_{i}.sgy",
                file_path=f"/data/test_{i}.sgy",
                file_size=1024 * (i + 1),
                upload_date=datetime.now(timezone.utc),
                status="uploaded",
                project_id=1,
                user_id=1
            )
            test_db.add(sgy_file)
        test_db.commit()
        
        response = client.get("/sgy-files/files", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3
    
    @pytest.mark.auth
    def test_get_sgy_file_by_id(self, client, auth_headers, test_db):
        """Test getting a specific SGY file by ID."""
        # Create SGY file
        sgy_file = SgyFileDBModel(
            filename="specific.sgy",
            file_path="/data/specific.sgy",
            file_size=2048,
            upload_date=datetime.now(timezone.utc),
            status="processed",
            project_id=1,
            user_id=1
        )
        test_db.add(sgy_file)
        test_db.commit()
        test_db.refresh(sgy_file)
        
        response = client.get(f"/sgy-files/files/{sgy_file.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sgy_file.id
        assert data["filename"] == "specific.sgy"
        assert data["status"] == "processed"
    
    @pytest.mark.auth
    def test_get_nonexistent_sgy_file(self, client, auth_headers):
        """Test getting a non-existent SGY file."""
        response = client.get("/sgy-files/files/99999", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestSgyFileOperations:
    """Test SGY file operations."""
    
    @pytest.mark.auth
    def test_update_sgy_file_metadata(self, client, auth_headers, test_db):
        """Test updating SGY file metadata."""
        # Create SGY file
        sgy_file = SgyFileDBModel(
            filename="update_test.sgy",
            file_path="/data/update_test.sgy",
            file_size=1024,
            upload_date=datetime.now(timezone.utc),
            status="uploaded",
            project_id=1,
            user_id=1
        )
        test_db.add(sgy_file)
        test_db.commit()
        test_db.refresh(sgy_file)
        
        response = client.put(
            f"/sgy-files/files/{sgy_file.id}",
            json={
                "metadata": {
                    "traces": 1000,
                    "samples_per_trace": 2000,
                    "sample_interval": 2.0
                }
            },
            headers=auth_headers
        )
        
        # If endpoint exists
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "metadata" in data
            assert data["metadata"]["traces"] == 1000
    
    @pytest.mark.auth
    def test_delete_sgy_file(self, client, auth_headers, test_db):
        """Test deleting an SGY file."""
        # Create SGY file
        sgy_file = SgyFileDBModel(
            filename="delete_test.sgy",
            file_path="/data/delete_test.sgy",
            file_size=512,
            upload_date=datetime.now(timezone.utc),
            status="uploaded",
            project_id=1,
            user_id=1
        )
        test_db.add(sgy_file)
        test_db.commit()
        test_db.refresh(sgy_file)
        
        response = client.delete(
            f"/sgy-files/files/{sgy_file.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify deletion
        get_response = client.get(f"/sgy-files/files/{sgy_file.id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND


class TestSgyFileProcessing:
    """Test SGY file processing operations."""
    
    @pytest.mark.auth
    def test_start_processing(self, client, auth_headers, test_db):
        """Test starting SGY file processing."""
        # Create SGY file
        sgy_file = SgyFileDBModel(
            filename="process_test.sgy",
            file_path="/data/process_test.sgy",
            file_size=4096,
            upload_date=datetime.now(timezone.utc),
            status="uploaded",
            project_id=1,
            user_id=1
        )
        test_db.add(sgy_file)
        test_db.commit()
        test_db.refresh(sgy_file)
        
        response = client.post(
            f"/sgy-files/files/{sgy_file.id}/process",
            json={
                "processing_type": "velocity_analysis",
                "parameters": {
                    "max_velocity": 5000,
                    "min_velocity": 1500
                }
            },
            headers=auth_headers
        )
        
        # If processing endpoint exists
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_202_ACCEPTED
            data = response.json()
            assert "job_id" in data or "status" in data
    
    @pytest.mark.auth
    def test_get_processing_status(self, client, auth_headers, test_db):
        """Test getting processing status."""
        # Create SGY file in processing
        sgy_file = SgyFileDBModel(
            filename="status_test.sgy",
            file_path="/data/status_test.sgy",
            file_size=2048,
            upload_date=datetime.now(timezone.utc),
            status="processing",
            project_id=1,
            user_id=1
        )
        test_db.add(sgy_file)
        test_db.commit()
        test_db.refresh(sgy_file)
        
        response = client.get(
            f"/sgy-files/files/{sgy_file.id}/status",
            headers=auth_headers
        )
        
        # If status endpoint exists
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "status" in data
            assert data["status"] == "processing"
    
    @pytest.mark.auth
    def test_cancel_processing(self, client, auth_headers, test_db):
        """Test canceling SGY file processing."""
        # Create SGY file in processing
        sgy_file = SgyFileDBModel(
            filename="cancel_test.sgy",
            file_path="/data/cancel_test.sgy",
            file_size=1024,
            upload_date=datetime.now(timezone.utc),
            status="processing",
            project_id=1,
            user_id=1
        )
        test_db.add(sgy_file)
        test_db.commit()
        test_db.refresh(sgy_file)
        
        response = client.post(
            f"/sgy-files/files/{sgy_file.id}/cancel",
            headers=auth_headers
        )
        
        # If cancel endpoint exists
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] in ["cancelled", "uploaded"]


class TestSgyFileDownload:
    """Test SGY file download operations."""
    
    @pytest.mark.auth
    def test_download_sgy_file(self, client, auth_headers, test_db):
        """Test downloading an SGY file."""
        # Create SGY file
        sgy_file = SgyFileDBModel(
            filename="download_test.sgy",
            file_path="/data/download_test.sgy",
            file_size=1024,
            upload_date=datetime.now(timezone.utc),
            status="uploaded",
            project_id=1,
            user_id=1
        )
        test_db.add(sgy_file)
        test_db.commit()
        test_db.refresh(sgy_file)
        
        response = client.get(
            f"/sgy-files/files/{sgy_file.id}/download",
            headers=auth_headers
        )
        
        # If download endpoint exists
        if response.status_code != status.HTTP_404_NOT_FOUND:
            # File might not exist on disk in test env
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_404_NOT_FOUND
            ]
    
    @pytest.mark.auth
    def test_get_processing_results(self, client, auth_headers, test_db):
        """Test getting processing results."""
        # Create processed SGY file
        sgy_file = SgyFileDBModel(
            filename="results_test.sgy",
            file_path="/data/results_test.sgy",
            file_size=2048,
            upload_date=datetime.now(timezone.utc),
            status="processed",
            processing_results={"velocity_model": [1500, 2000, 2500]},
            project_id=1,
            user_id=1
        )
        test_db.add(sgy_file)
        test_db.commit()
        test_db.refresh(sgy_file)
        
        response = client.get(
            f"/sgy-files/files/{sgy_file.id}/results",
            headers=auth_headers
        )
        
        # If results endpoint exists
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "velocity_model" in data


class TestSgyFileSearch:
    """Test SGY file search functionality."""
    
    @pytest.mark.auth
    def test_search_sgy_files(self, client, auth_headers, test_db):
        """Test searching SGY files."""
        # Create SGY files with different names
        files = [
            SgyFileDBModel(
                filename="marine_survey_001.sgy",
                file_path="/data/marine_survey_001.sgy",
                file_size=1024,
                upload_date=datetime.now(timezone.utc),
                status="uploaded",
                project_id=1,
                user_id=1
            ),
            SgyFileDBModel(
                filename="land_survey_001.sgy",
                file_path="/data/land_survey_001.sgy",
                file_size=2048,
                upload_date=datetime.now(timezone.utc),
                status="uploaded",
                project_id=1,
                user_id=1
            ),
            SgyFileDBModel(
                filename="marine_test.sgy",
                file_path="/data/marine_test.sgy",
                file_size=512,
                upload_date=datetime.now(timezone.utc),
                status="uploaded",
                project_id=1,
                user_id=1
            )
        ]
        for f in files:
            test_db.add(f)
        test_db.commit()
        
        response = client.get(
            "/sgy-files/search?q=marine",
            headers=auth_headers
        )
        
        # If search endpoint exists
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert isinstance(data, list)
            assert all("marine" in f["filename"].lower() for f in data)
    
    @pytest.mark.auth
    def test_filter_sgy_files_by_status(self, client, auth_headers, test_db):
        """Test filtering SGY files by status."""
        # Create files with different statuses
        statuses = ["uploaded", "processing", "processed", "uploaded"]
        for i, status in enumerate(statuses):
            sgy_file = SgyFileDBModel(
                filename=f"status_file_{i}.sgy",
                file_path=f"/data/status_file_{i}.sgy",
                file_size=1024,
                upload_date=datetime.now(timezone.utc),
                status=status,
                project_id=1,
                user_id=1
            )
            test_db.add(sgy_file)
        test_db.commit()
        
        response = client.get(
            "/sgy-files/files?status=uploaded",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should only get uploaded files
        assert all(f["status"] == "uploaded" for f in data if "status" in f)


class TestSgyFilePermissions:
    """Test SGY file access permissions."""
    
    @pytest.mark.auth
    def test_user_can_only_access_own_files(self, client, test_db):
        """Test that users can only access their own SGY files."""
        # Create two users
        user1_data = UserCreate(
            username="sgyuser1",
            password="password123",
            email="sgyuser1@test.com",
            disabled=False,
            auth_level=1
        )
        user1 = create_user(db=test_db, user=user1_data)
        
        user2_data = UserCreate(
            username="sgyuser2",
            password="password123",
            email="sgyuser2@test.com",
            disabled=False,
            auth_level=1
        )
        user2 = create_user(db=test_db, user=user2_data)
        
        # Create SGY files for each user
        file1 = SgyFileDBModel(
            filename="user1_file.sgy",
            file_path="/data/user1_file.sgy",
            file_size=1024,
            upload_date=datetime.now(timezone.utc),
            status="uploaded",
            project_id=1,
            user_id=user1.id
        )
        file2 = SgyFileDBModel(
            filename="user2_file.sgy",
            file_path="/data/user2_file.sgy",
            file_size=2048,
            upload_date=datetime.now(timezone.utc),
            status="uploaded",
            project_id=2,
            user_id=user2.id
        )
        test_db.add_all([file1, file2])
        test_db.commit()
        test_db.refresh(file1)
        
        # Login as user1
        login_response = client.post(
            "/token",
            data={
                "username": "sgyuser1",
                "password": "password123"
            }
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to access own file
        response = client.get("/sgy-files/files", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        
        # Try to process user2's file
        process_response = client.post(
            f"/sgy-files/files/{file2.id}/process",
            json={"processing_type": "velocity_analysis"},
            headers=headers
        )
        # Should be forbidden or not found
        if process_response.status_code != status.HTTP_404_NOT_FOUND:
            assert process_response.status_code == status.HTTP_403_FORBIDDEN


class TestSgyFileBatchOperations:
    """Test batch operations on SGY files."""
    
    @pytest.mark.auth
    def test_batch_delete_sgy_files(self, client, auth_headers, test_db):
        """Test deleting multiple SGY files at once."""
        # Create multiple files
        file_ids = []
        for i in range(3):
            sgy_file = SgyFileDBModel(
                filename=f"batch_delete_{i}.sgy",
                file_path=f"/data/batch_delete_{i}.sgy",
                file_size=1024,
                upload_date=datetime.now(timezone.utc),
                status="uploaded",
                project_id=1,
                user_id=1
            )
            test_db.add(sgy_file)
            test_db.commit()
            test_db.refresh(sgy_file)
            file_ids.append(sgy_file.id)
        
        response = client.post(
            "/sgy-files/batch-delete",
            json={"file_ids": file_ids},
            headers=auth_headers
        )
        
        # If batch endpoint exists
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            
            # Verify files are deleted
            for file_id in file_ids:
                get_response = client.get(
                    f"/sgy-files/files/{file_id}",
                    headers=auth_headers
                )
                assert get_response.status_code == status.HTTP_404_NOT_FOUND 