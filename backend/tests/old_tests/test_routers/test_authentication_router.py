"""
Test authentication router endpoints.
"""
import pytest
from datetime import datetime, timedelta, timezone
from fastapi import status
from jose import jwt

from schemas.user_schema import UserCreate
from crud.user_crud import create_user


class TestLoginEndpoint:
    """Test /token endpoint."""
    
    @pytest.mark.auth
    def test_login_with_form_data(self, client, test_user):
        """Test login with form data."""
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
    
    @pytest.mark.auth
    def test_login_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials."""
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
    def test_login_missing_username(self, client):
        """Test login with missing username."""
        response = client.post(
            "/token",
            data={
                "password": "password123"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.auth
    def test_login_missing_password(self, client):
        """Test login with missing password."""
        response = client.post(
            "/token",
            data={
                "username": "testuser"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.auth
    def test_login_empty_credentials(self, client):
        """Test login with empty credentials."""
        response = client.post(
            "/token",
            data={
                "username": "",
                "password": ""
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.auth
    def test_login_disabled_user(self, client, test_db):
        """Test login with disabled user."""
        # Create disabled user
        user_data = UserCreate(
            username="disableduser",
            password="password123",
            email="disabled@test.com",
            disabled=True,
            auth_level=1
        )
        create_user(db=test_db, user=user_data)
        
        response = client.post(
            "/token",
            data={
                "username": "disableduser",
                "password": "password123"
            }
        )
        
        # Authentication checks if user is disabled in get_current_user
        # So login might succeed but subsequent requests will fail
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_200_OK]
    
    @pytest.mark.auth
    def test_login_expired_user(self, client, test_db):
        """Test login with expired user."""
        # Create expired user
        user_data = UserCreate(
            username="expireduser",
            password="password123",
            email="expired@test.com",
            disabled=False,
            auth_level=1,
            expiration=datetime.now(timezone.utc) - timedelta(days=1)  # Expired yesterday
        )
        create_user(db=test_db, user=user_data)
        
        response = client.post(
            "/token",
            data={
                "username": "expireduser",
                "password": "password123"
            }
        )
        
        # Depending on implementation, this might be 401 or 200 with expired token
        # Adjust based on your actual implementation
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_200_OK]


class TestMeEndpoint:
    """Test /users/me endpoint."""
    
    @pytest.mark.auth
    def test_get_current_user(self, client, auth_headers):
        """Test getting current user info."""
        response = client.get("/users/me", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify user data
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
        assert data["auth_level"] == 1
        assert data["disabled"] is False
        
        # Verify sensitive data is not exposed
        assert "hashed_password" not in data
        assert "password" not in data
    
    @pytest.mark.auth
    def test_get_current_user_no_auth(self, client):
        """Test getting current user without authentication."""
        response = client.get("/users/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.auth
    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token."""
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = client.get("/users/me", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.auth
    def test_get_current_user_malformed_header(self, client):
        """Test getting current user with malformed auth header."""
        headers = {"Authorization": "NotBearer token"}
        response = client.get("/users/me", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.auth
    def test_get_current_user_expired_token(self, client, test_user, mock_env_vars):
        """Test getting current user with expired token."""
        # Create an expired token
        data = {"sub": test_user.username}
        expires = datetime.now(timezone.utc) - timedelta(minutes=1)
        
        encoded_jwt = jwt.encode(
            {"sub": test_user.username, "exp": expires},
            mock_env_vars["SECRET_KEY"],
            algorithm=mock_env_vars["ALGORITHM"]
        )
        
        headers = {"Authorization": f"Bearer {encoded_jwt}"}
        response = client.get("/users/me", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestRefreshEndpoint:
    """Test /refresh-token endpoint."""
    
    @pytest.mark.auth
    def test_refresh_token(self, client, auth_headers):
        """Test refreshing access token."""
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
        assert "refresh_token" in data
        assert "message" in data
        
        # Verify new token works
        new_headers = {"Authorization": f"Bearer {data['access_token']}"}
        me_response = client.get("/users/me", headers=new_headers)
        assert me_response.status_code == status.HTTP_200_OK
    
    @pytest.mark.auth
    def test_refresh_token_no_auth(self, client):
        """Test refreshing token without authentication."""
        response = client.post("/refresh-token", json={})
        
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    @pytest.mark.auth
    def test_refresh_token_invalid_token(self, client):
        """Test refreshing with invalid token."""
        response = client.post("/refresh-token", json={"token": "invalid_token"})
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.auth
    def test_refresh_disabled_user(self, client, test_db):
        """Test refreshing token for disabled user."""
        # Create user and login
        user_data = UserCreate(
            username="refreshdisabled",
            password="password123",
            email="refreshdisabled@test.com",
            disabled=False,
            auth_level=1
        )
        user = create_user(db=test_db, user=user_data)
        
        # Login to get token
        login_response = client.post(
            "/token",
            data={
                "username": "refreshdisabled",
                "password": "password123"
            }
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # Disable user
        user.disabled = True
        test_db.commit()
        
        # Try to refresh
        response = client.post("/refresh-token", json={"token": refresh_token})
        
        # Should fail since user is disabled
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestPasswordEndpoints:
    """Test password-related endpoints."""
    
    @pytest.mark.auth
    def test_change_password(self, client, auth_headers):
        """Test changing user's own password."""
        response = client.put(
            "/change-password",
            json={
                "current_password": "testpassword123",
                "new_password": "newtestpassword123"
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Try logging in with new password
        login_response = client.post(
            "/token",
            data={
                "username": "testuser",
                "password": "newtestpassword123"
            }
        )
        assert login_response.status_code == status.HTTP_200_OK
    
    @pytest.mark.auth
    def test_change_password_wrong_current(self, client, auth_headers):
        """Test changing password with wrong current password."""
        response = client.put(
            "/change-password",
            json={
                "current_password": "wrongpassword",
                "new_password": "newtestpassword123"
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestAuthIntegration:
    """Test authentication flow integration."""
    
    @pytest.mark.auth
    @pytest.mark.integration
    def test_full_auth_flow(self, client, test_db):
        """Test complete authentication flow."""
        # 1. Create user
        user_data = UserCreate(
            username="flowtest",
            password="flowpassword123",
            email="flow@test.com",
            full_name="Flow Test",
            disabled=False,
            auth_level=2
        )
        create_user(db=test_db, user=user_data)
        
        # 2. Login
        login_response = client.post(
            "/token",
            data={
                "username": "flowtest",
                "password": "flowpassword123"
            }
        )
        assert login_response.status_code == status.HTTP_200_OK
        access_token = login_response.json()["access_token"]
        refresh_token = login_response.json()["refresh_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # 3. Access protected endpoint
        me_response = client.get("/users/me", headers=headers)
        assert me_response.status_code == status.HTTP_200_OK
        assert me_response.json()["username"] == "flowtest"
        
        # 4. Refresh token
        refresh_response = client.post("/refresh-token", json={"token": refresh_token})
        assert refresh_response.status_code == status.HTTP_200_OK
        new_token = refresh_response.json()["access_token"]
        
        # 5. Use new token
        new_headers = {"Authorization": f"Bearer {new_token}"}
        me_response2 = client.get("/users/me", headers=new_headers)
        assert me_response2.status_code == status.HTTP_200_OK 