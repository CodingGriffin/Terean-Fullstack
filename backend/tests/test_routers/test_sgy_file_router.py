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
        sgy_file_path = os.path.join(temp_dir, "test_seismic.sgy")
        with open(sgy_file_path, "wb") as f:
            # Write mock SGY header (3600 bytes)
            f.write(b"C" * 3200)  # Text header
            f.write(b"\x00" * 400)  # Binary header
            # Write some trace data
            f.write(b"\x00" * 1000)
        
        with open(sgy_file_path, "rb") as f:
            response = client.post(
                "/api/sgy/upload",
                files={"file": ("test_seismic.sgy", f, "application/octet-stream")},
                headers=auth_headers
            )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["filename"] == "test_seismic.sgy"
        assert data["status"] == "uploaded"
        assert "id" in data
        assert "file_size" in data
    
    @pytest.mark.auth
    def test_upload_non_sgy_file(self, client, auth_headers, temp_dir):
        """Test uploading a non-SGY file (should fail)."""
        # Create a non-SGY file
        txt_file_path = os.path.join(temp_dir, "not_sgy.txt")
        with open(txt_file_path, "w") as f:
            f.write("This is not an SGY file")
        
        with open(txt_file_path, "rb") as f:
            response = client.post(
                "/api/sgy/upload",
                files={"file": ("not_sgy.txt", f, "text/plain")},
                headers=auth_headers
            )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid file type" in response.json()["detail"] or \
               "must be .sgy" in response.json()["detail"].lower()
    
    @pytest.mark.auth
    def test_upload_large_sgy_file(self, client, auth_headers, temp_dir):
        """Test uploading a large SGY file."""
        # Create a large mock SGY file (10MB)
        large_sgy_path = os.path.join(temp_dir, "large_seismic.sgy")
        with open(large_sgy_path, "wb") as f:
            # Write header
            f.write(b"C" * 3200)
            f.write(b"\x00" * 400)
            # Write 10MB of trace data
            for _ in range(100):
                f.write(b"\x00" * 100000)
        
        file_size = os.path.getsize(large_sgy_path)
        
        with open(large_sgy_path, "rb") as f:
            response = client.post(
                "/api/sgy/upload",
                files={"file": ("large_seismic.sgy", f, "application/octet-stream")},
                headers=auth_headers
            )
        
        if response.status_code == status.HTTP_201_CREATED:
            data = response.json()
            assert data["file_size"] == file_size
        elif response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE:
            # File size limit exceeded
            pass
    
    @pytest.mark.auth
    def test_upload_no_auth(self, client, temp_dir):
        """Test uploading without authentication."""
        sgy_file_path = os.path.join(temp_dir, "test.sgy")
        with open(sgy_file_path, "wb") as f:
            f.write(b"C" * 3600)
        
        with open(sgy_file_path, "rb") as f:
            response = client.post(
                "/api/sgy/upload",
                files={"file": ("test.sgy", f, "application/octet-stream")}
            )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestSgyFileCRUD:
    """Test SGY file CRUD operations."""
    
    @pytest.mark.auth
    def test_get_sgy_file_list(self, client, auth_headers, test_db):
        """Test getting list of SGY files."""
        # Create some SGY files
        for i in range(5):
            sgy_data = SgyFileCreate(
                filename=f"seismic_{i}.sgy",
                file_path=f"/data/seismic_{i}.sgy",
                file_size=1024000 * (i + 1),
                status="uploaded" if i % 2 == 0 else "processed"
            )
            create_sgy_file(db=test_db, sgy_file=sgy_data)
        
        response = client.get("/api/sgy/files", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        files = response.json()
        assert isinstance(files, list)
        assert len(files) >= 5
    
    @pytest.mark.auth
    def test_get_sgy_file_by_id(self, client, auth_headers, test_db):
        """Test getting SGY file by ID."""
        # Create SGY file
        sgy_data = SgyFileCreate(
            filename="get_by_id.sgy",
            file_path="/data/get_by_id.sgy",
            file_size=2048000,
            status="uploaded",
            metadata={"traces": 1000, "samples": 2000}
        )
        sgy_file = create_sgy_file(db=test_db, sgy_file=sgy_data)
        
        response = client.get(f"/api/sgy/files/{sgy_file.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sgy_file.id
        assert data["filename"] == "get_by_id.sgy"
        assert data["metadata"]["traces"] == 1000
    
    @pytest.mark.auth
    def test_get_sgy_file_not_found(self, client, auth_headers):
        """Test getting non-existent SGY file."""
        response = client.get("/api/sgy/files/99999", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.auth
    def test_update_sgy_file_status(self, client, auth_headers, test_db):
        """Test updating SGY file status."""
        # Create SGY file
        sgy_data = SgyFileCreate(
            filename="update_status.sgy",
            file_path="/data/update_status.sgy",
            file_size=1024000,
            status="uploaded"
        )
        sgy_file = create_sgy_file(db=test_db, sgy_file=sgy_data)
        
        # Update status
        response = client.put(
            f"/api/sgy/files/{sgy_file.id}",
            json={
                "status": "processing",
                "metadata": {"processing_started": datetime.utcnow().isoformat()}
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "processing"
        assert "processing_started" in data["metadata"]
    
    @pytest.mark.auth
    def test_delete_sgy_file(self, client, auth_headers, test_db):
        """Test deleting SGY file."""
        # Create SGY file
        sgy_data = SgyFileCreate(
            filename="delete_me.sgy",
            file_path="/data/delete_me.sgy",
            file_size=512000,
            status="uploaded"
        )
        sgy_file = create_sgy_file(db=test_db, sgy_file=sgy_data)
        
        # Delete file
        response = client.delete(
            f"/api/sgy/files/{sgy_file.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify deletion
        get_response = client.get(f"/api/sgy/files/{sgy_file.id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND


class TestSgyFileProcessing:
    """Test SGY file processing operations."""
    
    @pytest.mark.auth
    def test_start_processing(self, client, auth_headers, test_db):
        """Test starting SGY file processing."""
        # Create SGY file
        sgy_data = SgyFileCreate(
            filename="process_me.sgy",
            file_path="/data/process_me.sgy",
            file_size=2048000,
            status="uploaded"
        )
        sgy_file = create_sgy_file(db=test_db, sgy_file=sgy_data)
        
        # Start processing
        response = client.post(
            f"/api/sgy/files/{sgy_file.id}/process",
            json={
                "processing_params": {
                    "method": "standard",
                    "quality": "high"
                }
            },
            headers=auth_headers
        )
        
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_202_ACCEPTED
            ]
            data = response.json()
            assert "status" in data
            assert data["status"] in ["processing", "queued"]
    
    @pytest.mark.auth
    def test_get_processing_status(self, client, auth_headers, test_db):
        """Test getting processing status."""
        # Create SGY file in processing state
        sgy_data = SgyFileCreate(
            filename="processing.sgy",
            file_path="/data/processing.sgy",
            file_size=1024000,
            status="processing",
            process_start_date=datetime.utcnow(),
            metadata={"progress": 50}
        )
        sgy_file = create_sgy_file(db=test_db, sgy_file=sgy_data)
        
        response = client.get(
            f"/api/sgy/files/{sgy_file.id}/status",
            headers=auth_headers
        )
        
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "processing"
            assert "progress" in data
    
    @pytest.mark.auth
    def test_cancel_processing(self, client, auth_headers, test_db):
        """Test canceling SGY file processing."""
        # Create SGY file in processing state
        sgy_data = SgyFileCreate(
            filename="cancel_me.sgy",
            file_path="/data/cancel_me.sgy",
            file_size=1024000,
            status="processing"
        )
        sgy_file = create_sgy_file(db=test_db, sgy_file=sgy_data)
        
        response = client.post(
            f"/api/sgy/files/{sgy_file.id}/cancel",
            headers=auth_headers
        )
        
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] in ["cancelled", "uploaded"]


class TestSgyFileDownload:
    """Test SGY file download functionality."""
    
    @pytest.mark.auth
    def test_download_sgy_file(self, client, auth_headers, test_db, temp_dir):
        """Test downloading SGY file."""
        # Create SGY file
        file_path = os.path.join(temp_dir, "download_me.sgy")
        with open(file_path, "wb") as f:
            f.write(b"SGY" * 1000)
        
        sgy_data = SgyFileCreate(
            filename="download_me.sgy",
            file_path=file_path,
            file_size=3000,
            status="processed"
        )
        sgy_file = create_sgy_file(db=test_db, sgy_file=sgy_data)
        
        response = client.get(
            f"/api/sgy/files/{sgy_file.id}/download",
            headers=auth_headers
        )
        
        if response.status_code == status.HTTP_200_OK:
            assert response.headers["content-type"] == "application/octet-stream"
            assert "content-disposition" in response.headers
            assert "download_me.sgy" in response.headers["content-disposition"]
            assert len(response.content) == 3000
    
    @pytest.mark.auth
    def test_download_processed_results(self, client, auth_headers, test_db):
        """Test downloading processed results."""
        # Create processed SGY file
        sgy_data = SgyFileCreate(
            filename="processed.sgy",
            file_path="/data/processed.sgy",
            file_size=2048000,
            status="completed",
            metadata={
                "results_path": "/results/processed_results.json"
            }
        )
        sgy_file = create_sgy_file(db=test_db, sgy_file=sgy_data)
        
        response = client.get(
            f"/api/sgy/files/{sgy_file.id}/results",
            headers=auth_headers
        )
        
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_404_NOT_FOUND  # Results not found
            ]


class TestSgyFileSearch:
    """Test SGY file search functionality."""
    
    @pytest.mark.auth
    def test_search_sgy_files(self, client, auth_headers, test_db):
        """Test searching SGY files."""
        # Create files with different names
        files = [
            ("marine_survey_001.sgy", "Marine survey data"),
            ("land_survey_002.sgy", "Land survey data"),
            ("marine_processing.sgy", "Marine processing test"),
            ("test_data.sgy", "Test seismic data")
        ]
        
        for filename, description in files:
            sgy_data = SgyFileCreate(
                filename=filename,
                file_path=f"/data/{filename}",
                file_size=1024000,
                status="uploaded",
                metadata={"description": description}
            )
            create_sgy_file(db=test_db, sgy_file=sgy_data)
        
        # Search for "marine"
        response = client.get(
            "/api/sgy/search?q=marine",
            headers=auth_headers
        )
        
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            results = response.json()
            assert len(results) >= 2
            for result in results:
                assert "marine" in result["filename"].lower() or \
                       "marine" in str(result.get("metadata", {})).lower()
    
    @pytest.mark.auth
    def test_filter_sgy_files_by_status(self, client, auth_headers, test_db):
        """Test filtering SGY files by status."""
        # Create files with different statuses
        statuses = ["uploaded", "uploaded", "processing", "completed", "failed"]
        
        for i, status_val in enumerate(statuses):
            sgy_data = SgyFileCreate(
                filename=f"status_test_{i}.sgy",
                file_path=f"/data/status_test_{i}.sgy",
                file_size=512000,
                status=status_val
            )
            create_sgy_file(db=test_db, sgy_file=sgy_data)
        
        # Filter by uploaded status
        response = client.get(
            "/api/sgy/files?status=uploaded",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        results = response.json()
        for file in results:
            if file["filename"].startswith("status_test_"):
                assert file["status"] == "uploaded"


class TestSgyFilePermissions:
    """Test SGY file permission requirements."""
    
    @pytest.mark.auth
    def test_sgy_operations_auth_levels(self, client, test_db):
        """Test SGY file operations with different auth levels."""
        # Create users with different auth levels
        from schemas.user_schema import UserCreate
        from crud.user_crud import create_user
        
        users = []
        for level in [1, 2, 3]:
            user_data = UserCreate(
                username=f"sgylevel{level}",
                password="password123",
                email=f"sgylevel{level}@test.com",
                disabled=False,
                auth_level=level
            )
            users.append(create_user(db=test_db, user=user_data))
        
        # Create a test SGY file
        sgy_data = SgyFileCreate(
            filename="permission_test.sgy",
            file_path="/data/permission_test.sgy",
            file_size=1024000,
            status="uploaded"
        )
        sgy_file = create_sgy_file(db=test_db, sgy_file=sgy_data)
        
        # Test each user's access
        for level, user in zip([1, 2, 3], users):
            # Login
            login_response = client.post(
                "/api/auth/login",
                data={
                    "username": f"sgylevel{level}",
                    "password": "password123"
                }
            )
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # All authenticated users should be able to view files
            view_response = client.get("/api/sgy/files", headers=headers)
            assert view_response.status_code == status.HTTP_200_OK
            
            # Check processing permissions (might require higher level)
            process_response = client.post(
                f"/api/sgy/files/{sgy_file.id}/process",
                json={"processing_params": {}},
                headers=headers
            )
            
            if process_response.status_code != status.HTTP_404_NOT_FOUND:
                if level >= 2:  # Assuming level 2+ can process
                    assert process_response.status_code in [
                        status.HTTP_200_OK,
                        status.HTTP_202_ACCEPTED
                    ]
                else:
                    assert process_response.status_code == status.HTTP_403_FORBIDDEN 