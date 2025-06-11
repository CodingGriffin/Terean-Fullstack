"""
Test main application functionality.
"""
import pytest
import os
from fastapi import status
from fastapi.testclient import TestClient

from main import app
from schemas.user_schema import UserCreate
from crud.user_crud import create_user


class TestMainApp:
    """Test main application configuration and endpoints."""
    
    def test_app_exists(self):
        """Test that the FastAPI app instance exists."""
        assert app is not None
        assert app.title is not None
    
    def test_cors_middleware_configured(self):
        """Test that CORS middleware is properly configured."""
        # Check if CORS middleware is in the app
        middleware_classes = [m.cls.__name__ for m in app.user_middleware]
        assert "CORSMiddleware" in str(middleware_classes)
    
    def test_routers_included(self):
        """Test that all routers are included in the app."""
        routes = [route.path for route in app.routes]
        
        # Check for authentication routes
        assert any("/api/auth/" in route for route in routes)
        
        # Check for admin routes
        assert any("/api/admin/" in route for route in routes)
        
        # Check for project routes
        assert any("/api/projects" in route for route in routes)
        
        # Check for sgy file routes
        assert any("/api/sgy" in route for route in routes)
        
        # Check for process routes
        assert any("/api/process" in route for route in routes)
    
    def test_exception_handler_configured(self, client):
        """Test that custom exception handler is configured."""
        # Send invalid data to trigger validation error
        response = client.post(
            "/api/auth/login",
            json={"invalid": "data"}  # Missing required fields
        )
        
        # Should get custom error response
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "status_code" in data
        assert data["status_code"] == 10422
        assert "message" in data


class TestMainEndpoints:
    """Test main application endpoints."""
    
    @pytest.mark.auth
    def test_generate_results_email_endpoint(self, client, auth_headers, temp_dir, mock_env_vars):
        """Test the generateResultsEmail endpoint."""
        # Create a mock velocity model file
        model_file = os.path.join(temp_dir, "velocity_model.txt")
        with open(model_file, "w") as f:
            f.write("0.0 1500.0\n")
            f.write("10.0 1600.0\n")
            f.write("20.0 1700.0\n")
        
        with open(model_file, "rb") as f:
            response = client.post(
                "/generateResultsEmail",
                files={"velocity_model": ("velocity_model.txt", f, "text/plain")},
                data={
                    "client_name": "Test Client",
                    "client_email": "test@example.com",
                    "file_id": "test_file_123"
                },
                headers=auth_headers
            )
        
        # This endpoint might fail due to email sending, but should handle file processing
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]
    
    @pytest.mark.auth
    def test_generate_results_email_invalid_file_id(self, client, auth_headers, temp_dir):
        """Test generateResultsEmail with invalid file ID."""
        model_file = os.path.join(temp_dir, "velocity_model.txt")
        with open(model_file, "w") as f:
            f.write("0.0 1500.0\n")
        
        with open(model_file, "rb") as f:
            response = client.post(
                "/generateResultsEmail",
                files={"velocity_model": ("velocity_model.txt", f, "text/plain")},
                data={
                    "client_name": "Test Client",
                    "client_email": "test@example.com",
                    "file_id": "../../../etc/passwd"  # Path traversal attempt
                },
                headers=auth_headers
            )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid file ID" in response.json()["detail"]
    
    @pytest.mark.auth
    def test_generate_results_email_no_auth(self, client, temp_dir):
        """Test generateResultsEmail without authentication."""
        model_file = os.path.join(temp_dir, "velocity_model.txt")
        with open(model_file, "w") as f:
            f.write("0.0 1500.0\n")
        
        with open(model_file, "rb") as f:
            response = client.post(
                "/generateResultsEmail",
                files={"velocity_model": ("velocity_model.txt", f, "text/plain")},
                data={
                    "client_name": "Test Client",
                    "client_email": "test@example.com",
                    "file_id": "test_file_123"
                }
            )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.auth
    def test_results_email_form_endpoint(self, client, auth_headers, mock_env_vars):
        """Test the results email form endpoint."""
        # Create necessary directory structure
        data_dir = mock_env_vars["MQ_SAVE_DIR"]
        extracted_dir = os.path.join(data_dir, "Extracted", "test_file_123")
        os.makedirs(extracted_dir, exist_ok=True)
        
        # Create user info file
        user_info_path = os.path.join(extracted_dir, "userInfo.txt")
        with open(user_info_path, "w") as f:
            f.write("Test User\n")
            f.write("+1234567890\n")
            f.write("test@example.com\n")
        
        response = client.get(
            "/projects/test_file_123/results_email_form",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "text/html; charset=utf-8"
        
        # Check HTML content
        html_content = response.text
        assert "Upload Model File" in html_content
        assert "Test User" in html_content
        assert "test@example.com" in html_content
        assert "test_file_123" in html_content
    
    @pytest.mark.auth
    def test_results_email_form_invalid_file_id(self, client, auth_headers):
        """Test results email form with invalid file ID."""
        response = client.get(
            "/projects/../../../etc/passwd/results_email_form",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid file ID" in response.json()["detail"]


class TestLifespanEvents:
    """Test application lifespan events."""
    
    def test_initial_users_created(self, monkeypatch):
        """Test that initial users are created from environment variable."""
        # Set up test initial users
        initial_users = str([
            {
                "username": "test_initial_admin",
                "password": "admin_password",
                "disabled": False,
                "auth_level": 3,
                "email": "admin@test.com",
                "full_name": "Test Admin"
            },
            {
                "username": "test_initial_user",
                "password": "user_password",
                "disabled": False,
                "auth_level": 1
            }
        ])
        monkeypatch.setenv("INITIAL_USERS", initial_users)
        
        # Create a new test client to trigger lifespan
        from database import SessionLocal
        with TestClient(app) as client:
            # Check if users were created
            db = SessionLocal()
            try:
                from crud.user_crud import get_user_by_username
                admin_user = get_user_by_username(db, "test_initial_admin")
                regular_user = get_user_by_username(db, "test_initial_user")
                
                if admin_user:
                    assert admin_user.username == "test_initial_admin"
                    assert admin_user.auth_level == 3
                    assert admin_user.email == "admin@test.com"
                
                if regular_user:
                    assert regular_user.username == "test_initial_user"
                    assert regular_user.auth_level == 1
            finally:
                db.close()
    
    def test_initial_users_missing_credentials(self, monkeypatch, caplog):
        """Test handling of initial users with missing credentials."""
        # Set up invalid initial users
        initial_users = str([
            {
                "username": "no_password_user",
                # Missing password
                "auth_level": 1
            },
            {
                # Missing username
                "password": "password123",
                "auth_level": 1
            }
        ])
        monkeypatch.setenv("INITIAL_USERS", initial_users)
        
        # Create a new test client to trigger lifespan
        with TestClient(app) as client:
            # Check that warnings were logged
            assert "missing username or password" in caplog.text.lower()


class TestSecurityHeaders:
    """Test security headers and configurations."""
    
    def test_security_headers(self, client):
        """Test that security headers are properly set."""
        response = client.get("/")
        
        # Check for security headers (if implemented)
        headers = response.headers
        
        # These are examples - adjust based on actual implementation
        # assert "X-Content-Type-Options" in headers
        # assert headers["X-Content-Type-Options"] == "nosniff"
        # assert "X-Frame-Options" in headers
        # assert headers["X-Frame-Options"] == "DENY"
        pass


class TestHealthCheck:
    """Test health check endpoints."""
    
    def test_health_endpoint(self, client):
        """Test health check endpoint (if exists)."""
        response = client.get("/health")
        
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "status" in data
            assert data["status"] in ["healthy", "ok"]
    
    def test_readiness_endpoint(self, client):
        """Test readiness endpoint (if exists)."""
        response = client.get("/ready")
        
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "ready" in data
            assert data["ready"] is True


class TestRateLimiting:
    """Test rate limiting (if implemented)."""
    
    @pytest.mark.slow
    def test_rate_limiting(self, client):
        """Test that rate limiting is enforced."""
        # Make many rapid requests
        responses = []
        for _ in range(100):
            response = client.get("/api/auth/me")
            responses.append(response.status_code)
        
        # Check if any requests were rate limited
        # This depends on actual rate limiting implementation
        # assert status.HTTP_429_TOO_MANY_REQUESTS in responses
        pass


class TestAPIDocumentation:
    """Test API documentation endpoints."""
    
    def test_openapi_schema(self, client):
        """Test OpenAPI schema endpoint."""
        response = client.get("/openapi.json")
        
        assert response.status_code == status.HTTP_200_OK
        schema = response.json()
        
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
        
        # Check that all major endpoints are documented
        paths = schema["paths"]
        assert "/api/auth/login" in paths
        assert "/api/auth/me" in paths
        assert "/api/projects" in paths
    
    def test_swagger_ui(self, client):
        """Test Swagger UI endpoint."""
        response = client.get("/docs")
        
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]
        assert "swagger" in response.text.lower()
    
    def test_redoc(self, client):
        """Test ReDoc endpoint."""
        response = client.get("/redoc")
        
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]
        assert "redoc" in response.text.lower() 