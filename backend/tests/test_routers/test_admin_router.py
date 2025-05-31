"""
Test admin router endpoints.
"""
import pytest
from datetime import datetime, timedelta
from fastapi import status

from schemas.user_schema import UserCreate
from crud.user_crud import create_user


class TestAdminUserManagement:
    """Test admin user management endpoints."""
    
    @pytest.mark.auth
    def test_get_users_list_as_admin(self, client, admin_auth_headers, test_db):
        """Test getting users list as admin."""
        # Create some test users
        for i in range(3):
            user_data = UserCreate(
                username=f"admintest{i}",
                password="password123",
                email=f"admintest{i}@test.com",
                disabled=False,
                auth_level=1
            )
            create_user(db=test_db, user=user_data)
        
        response = client.get("/api/admin/users", headers=admin_auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        users = response.json()
        assert isinstance(users, list)
        assert len(users) >= 3
        
        # Verify user data structure
        for user in users:
            assert "id" in user
            assert "username" in user
            assert "email" in user
            assert "auth_level" in user
            assert "disabled" in user
            assert "hashed_password" not in user
    
    @pytest.mark.auth
    def test_get_users_list_as_regular_user(self, client, auth_headers):
        """Test getting users list as regular user (should fail)."""
        response = client.get("/api/admin/users", headers=auth_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Not enough permissions" in response.json()["detail"]
    
    @pytest.mark.auth
    def test_get_users_list_no_auth(self, client):
        """Test getting users list without authentication."""
        response = client.get("/api/admin/users")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.auth
    def test_get_users_with_pagination(self, client, admin_auth_headers, test_db):
        """Test getting users with pagination."""
        # Create 10 test users
        for i in range(10):
            user_data = UserCreate(
                username=f"pageuser{i}",
                password="password123",
                email=f"pageuser{i}@test.com",
                disabled=False,
                auth_level=1
            )
            create_user(db=test_db, user=user_data)
        
        # Get first page
        response = client.get(
            "/api/admin/users?skip=0&limit=5",
            headers=admin_auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        users = response.json()
        assert len(users) == 5
        
        # Get second page
        response2 = client.get(
            "/api/admin/users?skip=5&limit=5",
            headers=admin_auth_headers
        )
        assert response2.status_code == status.HTTP_200_OK
        users2 = response2.json()
        assert len(users2) >= 5


class TestAdminUserCRUD:
    """Test admin CRUD operations on users."""
    
    @pytest.mark.auth
    def test_create_user_as_admin(self, client, admin_auth_headers):
        """Test creating a new user as admin."""
        response = client.post(
            "/api/admin/users",
            json={
                "username": "newadminuser",
                "password": "newpassword123",
                "email": "newadmin@test.com",
                "full_name": "New Admin User",
                "disabled": False,
                "auth_level": 2
            },
            headers=admin_auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == "newadminuser"
        assert data["email"] == "newadmin@test.com"
        assert data["auth_level"] == 2
        assert "hashed_password" not in data
    
    @pytest.mark.auth
    def test_create_user_duplicate_username(self, client, admin_auth_headers, test_user):
        """Test creating user with duplicate username."""
        response = client.post(
            "/api/admin/users",
            json={
                "username": "testuser",  # Already exists
                "password": "password123",
                "email": "duplicate@test.com",
                "disabled": False,
                "auth_level": 1
            },
            headers=admin_auth_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"].lower()
    
    @pytest.mark.auth
    def test_update_user_as_admin(self, client, admin_auth_headers, test_db):
        """Test updating a user as admin."""
        # Create a user to update
        user_data = UserCreate(
            username="updateme",
            password="password123",
            email="updateme@test.com",
            disabled=False,
            auth_level=1
        )
        user = create_user(db=test_db, user=user_data)
        
        # Update the user
        response = client.put(
            f"/api/admin/users/{user.id}",
            json={
                "email": "updated@test.com",
                "full_name": "Updated User",
                "auth_level": 2,
                "disabled": True
            },
            headers=admin_auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "updated@test.com"
        assert data["full_name"] == "Updated User"
        assert data["auth_level"] == 2
        assert data["disabled"] is True
        assert data["username"] == "updateme"  # Username unchanged
    
    @pytest.mark.auth
    def test_update_nonexistent_user(self, client, admin_auth_headers):
        """Test updating a nonexistent user."""
        response = client.put(
            "/api/admin/users/99999",
            json={
                "email": "updated@test.com"
            },
            headers=admin_auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.auth
    def test_delete_user_as_admin(self, client, admin_auth_headers, test_db):
        """Test deleting a user as admin."""
        # Create a user to delete
        user_data = UserCreate(
            username="deleteme",
            password="password123",
            email="deleteme@test.com",
            disabled=False,
            auth_level=1
        )
        user = create_user(db=test_db, user=user_data)
        
        # Delete the user
        response = client.delete(
            f"/api/admin/users/{user.id}",
            headers=admin_auth_headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify user is deleted
        get_response = client.get(
            f"/api/admin/users/{user.id}",
            headers=admin_auth_headers
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.auth
    def test_delete_nonexistent_user(self, client, admin_auth_headers):
        """Test deleting a nonexistent user."""
        response = client.delete(
            "/api/admin/users/99999",
            headers=admin_auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestAdminPermissions:
    """Test admin permission requirements."""
    
    @pytest.mark.auth
    def test_admin_endpoints_auth_levels(self, client, test_db):
        """Test that different auth levels have appropriate access."""
        # Create users with different auth levels
        users = []
        for level in [1, 2, 3]:
            user_data = UserCreate(
                username=f"level{level}admin",
                password="password123",
                email=f"level{level}admin@test.com",
                disabled=False,
                auth_level=level
            )
            users.append(create_user(db=test_db, user=user_data))
        
        # Test each user's access to admin endpoints
        for level, user in zip([1, 2, 3], users):
            # Login
            login_response = client.post(
                "/api/auth/login",
                data={
                    "username": f"level{level}admin",
                    "password": "password123"
                }
            )
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Try to access admin endpoints
            response = client.get("/api/admin/users", headers=headers)
            
            if level == 3:  # Only level 3 should have admin access
                assert response.status_code == status.HTTP_200_OK
            else:
                assert response.status_code == status.HTTP_403_FORBIDDEN


class TestAdminStatistics:
    """Test admin statistics endpoints (if they exist)."""
    
    @pytest.mark.auth
    def test_get_user_statistics(self, client, admin_auth_headers, test_db):
        """Test getting user statistics."""
        # Create some test data
        for i in range(5):
            user_data = UserCreate(
                username=f"statsuser{i}",
                password="password123",
                email=f"stats{i}@test.com",
                disabled=i % 2 == 0,  # Half disabled
                auth_level=(i % 3) + 1  # Mix of levels
            )
            create_user(db=test_db, user=user_data)
        
        response = client.get("/api/admin/stats/users", headers=admin_auth_headers)
        
        # If endpoint exists
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            stats = response.json()
            assert "total_users" in stats
            assert "active_users" in stats
            assert "disabled_users" in stats
    
    @pytest.mark.auth
    def test_get_system_health(self, client, admin_auth_headers):
        """Test getting system health status."""
        response = client.get("/api/admin/health", headers=admin_auth_headers)
        
        # If endpoint exists
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            health = response.json()
            assert "status" in health
            assert health["status"] in ["healthy", "degraded", "unhealthy"]


class TestAdminAuditLog:
    """Test admin audit log endpoints (if they exist)."""
    
    @pytest.mark.auth
    def test_get_audit_logs(self, client, admin_auth_headers):
        """Test getting audit logs."""
        response = client.get("/api/admin/audit-logs", headers=admin_auth_headers)
        
        # If endpoint exists
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            logs = response.json()
            assert isinstance(logs, list)
    
    @pytest.mark.auth
    def test_get_user_activity(self, client, admin_auth_headers, test_user):
        """Test getting specific user activity."""
        response = client.get(
            f"/api/admin/users/{test_user.id}/activity",
            headers=admin_auth_headers
        )
        
        # If endpoint exists
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            activity = response.json()
            assert isinstance(activity, list)


class TestAdminBulkOperations:
    """Test admin bulk operations (if they exist)."""
    
    @pytest.mark.auth
    def test_bulk_disable_users(self, client, admin_auth_headers, test_db):
        """Test bulk disabling users."""
        # Create test users
        user_ids = []
        for i in range(3):
            user_data = UserCreate(
                username=f"bulkuser{i}",
                password="password123",
                email=f"bulk{i}@test.com",
                disabled=False,
                auth_level=1
            )
            user = create_user(db=test_db, user=user_data)
            user_ids.append(user.id)
        
        response = client.post(
            "/api/admin/users/bulk-disable",
            json={"user_ids": user_ids},
            headers=admin_auth_headers
        )
        
        # If endpoint exists
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            result = response.json()
            assert result["disabled_count"] == 3
    
    @pytest.mark.auth
    def test_bulk_delete_users(self, client, admin_auth_headers, test_db):
        """Test bulk deleting users."""
        # Create test users
        user_ids = []
        for i in range(3):
            user_data = UserCreate(
                username=f"bulkdeluser{i}",
                password="password123",
                email=f"bulkdel{i}@test.com",
                disabled=False,
                auth_level=1
            )
            user = create_user(db=test_db, user=user_data)
            user_ids.append(user.id)
        
        response = client.post(
            "/api/admin/users/bulk-delete",
            json={"user_ids": user_ids},
            headers=admin_auth_headers
        )
        
        # If endpoint exists
        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code == status.HTTP_200_OK
            result = response.json()
            assert result["deleted_count"] == 3 