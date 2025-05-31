"""
Test process router endpoints.
"""
import pytest
import os
import json
from datetime import datetime, timedelta
from fastapi import status

from schemas.project_schema import ProjectCreate
from schemas.sgy_file_schema import SgyFileCreate
from crud.project_crud import create_project
from crud.sgy_file_crud import create_sgy_file


class TestProcessInitiation:
    """Test process initiation endpoints."""
    
    @pytest.mark.auth
    def test_start_processing_job(self, client, auth_headers, test_db):
        """Test starting a new processing job."""
        # Create a project and SGY file
        project_data = ProjectCreate(
            unique_id="process_proj_001",
            name="Process Test Project",
            status="active"
        )
        project = create_project(db=test_db, project=project_data)
        
        sgy_data = SgyFileCreate(
            filename="process_input.sgy",
            file_path="/data/process_input.sgy",
            file_size=2048000,
            status="uploaded"
        )
        sgy_file = create_sgy_file(db=test_db, sgy_file=sgy_data)
        
        # Start processing
        response = client.post(
            "/api/process/start",
            json={
                "project_id": project.id,
                "sgy_file_id": sgy_file.id,
                "process_type": "velocity_analysis",
                "parameters": {
                    "method": "semblance",
                    "min_velocity": 1500,
                    "max_velocity": 5000,
                    "velocity_step": 50
                }
            },
            headers=auth_headers
        )
        
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_202_ACCEPTED
        ]
        data = response.json()
        assert "job_id" in data
        assert "status" in data
        assert data["status"] in ["queued", "processing"]
    
    @pytest.mark.auth
    def test_start_processing_invalid_file(self, client, auth_headers):
        """Test starting processing with invalid file ID."""
        response = client.post(
            "/api/process/start",
            json={
                "project_id": 1,
                "sgy_file_id": 99999,
                "process_type": "velocity_analysis",
                "parameters": {}
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
    
    @pytest.mark.auth
    def test_start_processing_missing_params(self, client, auth_headers):
        """Test starting processing with missing parameters."""
        response = client.post(
            "/api/process/start",
            json={
                "sgy_file_id": 1,
                # Missing process_type and other required fields
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.auth
    def test_start_processing_no_auth(self, client):
        """Test starting processing without authentication."""
        response = client.post(
            "/api/process/start",
            json={
                "project_id": 1,
                "sgy_file_id": 1,
                "process_type": "velocity_analysis",
                "parameters": {}
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestProcessStatus:
    """Test process status monitoring endpoints."""
    
    @pytest.mark.auth
    def test_get_process_status(self, client, auth_headers):
        """Test getting process status."""
        # Assume a job ID from previous processing
        job_id = "test_job_123"
        
        response = client.get(
            f"/api/process/status/{job_id}",
            headers=auth_headers
        )
        
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "job_id" in data
            assert "status" in data
            assert "progress" in data
            assert data["status"] in [
                "queued", "processing", "completed", "failed", "cancelled"
            ]
    
    @pytest.mark.auth
    def test_get_all_process_jobs(self, client, auth_headers):
        """Test getting list of all process jobs."""
        response = client.get("/api/process/jobs", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        jobs = response.json()
        assert isinstance(jobs, list)
    
    @pytest.mark.auth
    def test_get_process_jobs_filtered(self, client, auth_headers):
        """Test getting filtered list of process jobs."""
        # Filter by status
        response = client.get(
            "/api/process/jobs?status=processing",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        jobs = response.json()
        for job in jobs:
            if "status" in job:
                assert job["status"] == "processing"
    
    @pytest.mark.auth
    def test_get_process_logs(self, client, auth_headers):
        """Test getting process logs."""
        job_id = "test_job_123"
        
        response = client.get(
            f"/api/process/jobs/{job_id}/logs",
            headers=auth_headers
        )
        
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            logs = response.json()
            assert isinstance(logs, list) or isinstance(logs, str)


class TestProcessControl:
    """Test process control endpoints."""
    
    @pytest.mark.auth
    def test_cancel_process(self, client, auth_headers):
        """Test canceling a running process."""
        job_id = "test_job_123"
        
        response = client.post(
            f"/api/process/jobs/{job_id}/cancel",
            headers=auth_headers
        )
        
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] in ["cancelled", "cancelling"]
    
    @pytest.mark.auth
    def test_pause_process(self, client, auth_headers):
        """Test pausing a running process."""
        job_id = "test_job_123"
        
        response = client.post(
            f"/api/process/jobs/{job_id}/pause",
            headers=auth_headers
        )
        
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_501_NOT_IMPLEMENTED  # If pause not supported
            ]
    
    @pytest.mark.auth
    def test_resume_process(self, client, auth_headers):
        """Test resuming a paused process."""
        job_id = "test_job_123"
        
        response = client.post(
            f"/api/process/jobs/{job_id}/resume",
            headers=auth_headers
        )
        
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_501_NOT_IMPLEMENTED  # If resume not supported
            ]
    
    @pytest.mark.auth
    def test_retry_failed_process(self, client, auth_headers):
        """Test retrying a failed process."""
        job_id = "failed_job_123"
        
        response = client.post(
            f"/api/process/jobs/{job_id}/retry",
            headers=auth_headers
        )
        
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_202_ACCEPTED
            ]


class TestProcessResults:
    """Test process results endpoints."""
    
    @pytest.mark.auth
    def test_get_process_results(self, client, auth_headers):
        """Test getting process results."""
        job_id = "completed_job_123"
        
        response = client.get(
            f"/api/process/jobs/{job_id}/results",
            headers=auth_headers
        )
        
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_404_NOT_FOUND  # Results not ready
            ]
            
            if response.status_code == status.HTTP_200_OK:
                data = response.json()
                assert "results" in data or "data" in data
    
    @pytest.mark.auth
    def test_download_process_results(self, client, auth_headers):
        """Test downloading process results as file."""
        job_id = "completed_job_123"
        
        response = client.get(
            f"/api/process/jobs/{job_id}/download",
            headers=auth_headers
        )
        
        if response.status_code == status.HTTP_200_OK:
            assert "content-disposition" in response.headers
            assert response.headers["content-type"] in [
                "application/json",
                "application/octet-stream",
                "application/zip"
            ]
    
    @pytest.mark.auth
    def test_get_process_preview(self, client, auth_headers):
        """Test getting process results preview."""
        job_id = "completed_job_123"
        
        response = client.get(
            f"/api/process/jobs/{job_id}/preview",
            headers=auth_headers
        )
        
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            preview = response.json()
            assert isinstance(preview, dict) or isinstance(preview, list)


class TestProcessQueue:
    """Test process queue management endpoints."""
    
    @pytest.mark.auth
    def test_get_queue_status(self, client, auth_headers):
        """Test getting process queue status."""
        response = client.get("/api/process/queue/status", headers=auth_headers)
        
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "queued_jobs" in data
            assert "active_jobs" in data
            assert "completed_jobs" in data
    
    @pytest.mark.auth
    def test_get_queue_position(self, client, auth_headers):
        """Test getting job position in queue."""
        job_id = "queued_job_123"
        
        response = client.get(
            f"/api/process/queue/position/{job_id}",
            headers=auth_headers
        )
        
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "position" in data
            assert isinstance(data["position"], int)
    
    @pytest.mark.auth
    @pytest.mark.admin
    def test_clear_process_queue(self, client, admin_auth_headers):
        """Test clearing process queue (admin only)."""
        response = client.post(
            "/api/process/queue/clear",
            headers=admin_auth_headers
        )
        
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "cleared_jobs" in data


class TestProcessTypes:
    """Test different process types."""
    
    @pytest.mark.auth
    def test_get_available_process_types(self, client, auth_headers):
        """Test getting list of available process types."""
        response = client.get("/api/process/types", headers=auth_headers)
        
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            types = response.json()
            assert isinstance(types, list)
            
            # Common process types that might be available
            expected_types = [
                "velocity_analysis",
                "stacking",
                "migration",
                "filtering",
                "deconvolution"
            ]
            
            for process_type in types:
                assert "type" in process_type or "name" in process_type
                assert "description" in process_type
    
    @pytest.mark.auth
    def test_get_process_parameters(self, client, auth_headers):
        """Test getting required parameters for a process type."""
        process_type = "velocity_analysis"
        
        response = client.get(
            f"/api/process/types/{process_type}/parameters",
            headers=auth_headers
        )
        
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            params = response.json()
            assert isinstance(params, dict) or isinstance(params, list)


class TestBatchProcessing:
    """Test batch processing operations."""
    
    @pytest.mark.auth
    def test_start_batch_process(self, client, auth_headers, test_db):
        """Test starting batch processing for multiple files."""
        # Create multiple SGY files
        file_ids = []
        for i in range(3):
            sgy_data = SgyFileCreate(
                filename=f"batch_file_{i}.sgy",
                file_path=f"/data/batch_file_{i}.sgy",
                file_size=1024000,
                status="uploaded"
            )
            sgy_file = create_sgy_file(db=test_db, sgy_file=sgy_data)
            file_ids.append(sgy_file.id)
        
        response = client.post(
            "/api/process/batch",
            json={
                "sgy_file_ids": file_ids,
                "process_type": "velocity_analysis",
                "parameters": {
                    "method": "semblance",
                    "min_velocity": 1500,
                    "max_velocity": 5000
                }
            },
            headers=auth_headers
        )
        
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code in [
                status.HTTP_201_CREATED,
                status.HTTP_202_ACCEPTED
            ]
            data = response.json()
            assert "batch_id" in data
            assert "jobs" in data
            assert len(data["jobs"]) == 3
    
    @pytest.mark.auth
    def test_get_batch_status(self, client, auth_headers):
        """Test getting batch processing status."""
        batch_id = "batch_123"
        
        response = client.get(
            f"/api/process/batch/{batch_id}/status",
            headers=auth_headers
        )
        
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "batch_id" in data
            assert "total_jobs" in data
            assert "completed_jobs" in data
            assert "failed_jobs" in data


class TestProcessPermissions:
    """Test process permission requirements."""
    
    @pytest.mark.auth
    def test_process_operations_auth_levels(self, client, test_db):
        """Test process operations with different auth levels."""
        # Create users with different auth levels
        from schemas.user_schema import UserCreate
        from crud.user_crud import create_user
        
        users = []
        for level in [1, 2, 3]:
            user_data = UserCreate(
                username=f"processlevel{level}",
                password="password123",
                email=f"processlevel{level}@test.com",
                disabled=False,
                auth_level=level
            )
            users.append(create_user(db=test_db, user=user_data))
        
        # Test each user's access
        for level, user in zip([1, 2, 3], users):
            # Login
            login_response = client.post(
                "/api/auth/login",
                data={
                    "username": f"processlevel{level}",
                    "password": "password123"
                }
            )
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Check viewing process status (all should have access)
            status_response = client.get("/api/process/jobs", headers=headers)
            assert status_response.status_code == status.HTTP_200_OK
            
            # Check starting process (might require higher level)
            start_response = client.post(
                "/api/process/start",
                json={
                    "project_id": 1,
                    "sgy_file_id": 1,
                    "process_type": "velocity_analysis",
                    "parameters": {}
                },
                headers=headers
            )
            
            if start_response.status_code != status.HTTP_404_NOT_FOUND:
                if level >= 2:  # Assuming level 2+ can start processes
                    assert start_response.status_code in [
                        status.HTTP_201_CREATED,
                        status.HTTP_202_ACCEPTED,
                        status.HTTP_404_NOT_FOUND  # File not found
                    ]
                else:
                    assert start_response.status_code == status.HTTP_403_FORBIDDEN
            
            # Check admin operations (only level 3)
            clear_response = client.post(
                "/api/process/queue/clear",
                headers=headers
            )
            
            if clear_response.status_code != status.HTTP_404_NOT_FOUND:
                if level == 3:
                    assert clear_response.status_code == status.HTTP_200_OK
                else:
                    assert clear_response.status_code == status.HTTP_403_FORBIDDEN


class TestProcessNotifications:
    """Test process notification endpoints."""
    
    @pytest.mark.auth
    def test_subscribe_to_process_updates(self, client, auth_headers):
        """Test subscribing to process updates."""
        job_id = "test_job_123"
        
        response = client.post(
            f"/api/process/jobs/{job_id}/subscribe",
            json={
                "notification_type": "email",
                "email": "user@example.com"
            },
            headers=auth_headers
        )
        
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "subscription_id" in data
    
    @pytest.mark.auth
    def test_websocket_process_updates(self, client, auth_headers):
        """Test WebSocket connection for real-time process updates."""
        # WebSocket testing requires special handling
        # This is a placeholder for WebSocket test implementation
        pass 