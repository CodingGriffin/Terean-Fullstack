"""
Test authentication functionality.
"""
import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt
from fastapi import status

from schemas.user_schema import UserCreate
from crud.user_crud import create_user
from utils.authentication import create_access_token, authenticate_user


class TestJWTTokens:
    """Test JWT token functionality."""
    
    def test_create_access_token(self, mock_env_vars):
        """Test access token creation."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        
        # Decode and verify token
        decoded = jwt.decode(
            token, 
            mock_env_vars["SECRET_KEY"], 
            algorithms=[mock_env_vars["ALGORITHM"]]
        )
        assert decoded["sub"] == "testuser"
        assert "exp" in decoded
    
    def test_access_token_expiration(self, mock_env_vars):
        """Test that access tokens have correct expiration."""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=15)
        token = create_access_token(data, expires_delta)
        
        decoded = jwt.decode(
            token, 
            mock_env_vars["SECRET_KEY"], 
            algorithms=[mock_env_vars["ALGORITHM"]]
        )
        
        exp_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        
        # Check that expiration is approximately 15 minutes from now
        assert 14 <= (exp_time - now).total_seconds() / 60 <= 16


class TestUserAuthentication:
    """Test user authentication functionality."""
    
    @pytest.mark.db
    def test_authenticate_user_success(self, test_db):
        """Test successful user authentication."""
        # Create user
        user_data = UserCreate(
            username="authtest",
            password="password123",
            email="auth@test.com",
            disabled=False,
            auth_level=1
        )
        create_user(db=test_db, user=user_data)
        
        # Authenticate
        authenticated_user = authenticate_user("authtest", "password123", test_db)
        
        assert authenticated_user is not False
        assert authenticated_user.username == "authtest"
        assert authenticated_user.email == "auth@test.com"
    
    @pytest.mark.db
    def test_authenticate_user_wrong_password(self, test_db):
        """Test authentication with wrong password."""
        # Create user
        user_data = UserCreate(
            username="authtest2",
            password="password123",
            email="auth2@test.com",
            disabled=False,
            auth_level=1
        )
        create_user(db=test_db, user=user_data)
        
        # Try to authenticate with wrong password
        result = authenticate_user("authtest2", "wrongpassword", test_db)
        
        assert result is False
    
    @pytest.mark.db
    def test_authenticate_nonexistent_user(self, test_db):
        """Test authentication of non-existent user."""
        result = authenticate_user("nonexistent", "password123", test_db)
        assert result is False
    
    @pytest.mark.db
    def test_authenticate_disabled_user(self, test_db):
        """Test authentication of disabled user."""
        # Create disabled user
        user_data = UserCreate(
            username="disableduser",
            password="password123",
            email="disabled@test.com",
            disabled=True,
            auth_level=1
        )
        create_user(db=test_db, user=user_data)
        
        # Try to authenticate
        result = authenticate_user("disableduser", "password123", test_db)
        
        # Should still return user object, disabled check happens elsewhere
        assert result is not False
        assert result.disabled is True


class TestAuthenticationEndpoints:
    """Test authentication API endpoints."""
    
    @pytest.mark.auth
    def test_login_success(self, client, test_user):
        """Test successful login."""
        response = client.post(
            "/token",
            data={
                "username": "testuser",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "message" in data
        assert data["message"] == "Login successful"
    
    @pytest.mark.auth
    def test_login_wrong_credentials(self, client, test_user):
        """Test login with wrong credentials."""
        response = client.post(
            "/token",
            data={
                "username": "testuser",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect username or password" in response.json()["detail"]
    
    @pytest.mark.auth
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = client.post(
            "/token",
            data={
                "username": "nonexistent",
                "password": "password123"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.auth
    def test_login_disabled_user(self, client, test_db):
        """Test login with disabled user."""
        # Create disabled user
        user_data = UserCreate(
            username="disabledlogin",
            password="password123",
            email="disabledlogin@test.com",
            disabled=True,
            auth_level=1
        )
        create_user(db=test_db, user=user_data)
        
        response = client.post(
            "/token",
            data={
                "username": "disabledlogin",
                "password": "password123"
            }
        )
        
        # The authenticate_user function returns the user even if disabled
        # The disabled check happens elsewhere, so login should succeed
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.auth
    def test_get_current_user(self, client, auth_headers):
        """Test getting current user information."""
        response = client.get("/users/me", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "hashed_password" not in data
    
    @pytest.mark.auth
    def test_get_current_user_no_token(self, client):
        """Test getting current user without token."""
        response = client.get("/users/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.auth
    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/users/me", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.auth
    def test_refresh_token(self, client, auth_headers):
        """Test token refresh functionality."""
        # First get the refresh token from login
        login_response = client.post(
            "/token",
            data={
                "username": "testuser",
                "password": "testpassword123"
            }
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # Now refresh the token
        response = client.post(
            "/refresh-token",
            json={"token": refresh_token}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "message" in data
        assert data["message"] == "Token refreshed successfully"


class TestPermissions:
    """Test permission and authorization functionality."""
    
    @pytest.mark.auth
    def test_admin_only_endpoint_with_admin(self, client, admin_auth_headers):
        """Test admin-only endpoint with admin user."""
        response = client.get("/admin/users", headers=admin_auth_headers)
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.auth
    def test_admin_only_endpoint_with_regular_user(self, client, auth_headers):
        """Test admin-only endpoint with regular user."""
        response = client.get("/admin/users", headers=auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.auth
    def test_auth_level_check(self, client, test_db):
        """Test different auth level requirements."""
        # Create users with different auth levels
        for level in [1, 2, 4]:
            user_data = UserCreate(
                username=f"level{level}user",
                password="password123",
                email=f"level{level}@test.com",
                disabled=False,
                auth_level=level
            )
            create_user(db=test_db, user=user_data)
        
        # Test access with different levels
        for level in [1, 2, 4]:
            response = client.post(
                "/token",
                data={
                    "username": f"level{level}user",
                    "password": "password123"
                }
            )
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # All users should access their own profile
            response = client.get("/users/me", headers=headers)
            assert response.status_code == status.HTTP_200_OK
            
            # Only level 4 should access admin endpoints
            response = client.get("/admin/users", headers=headers)
            if level == 4:
                assert response.status_code == status.HTTP_200_OK
            else:
                assert response.status_code == status.HTTP_403_FORBIDDEN 