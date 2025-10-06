import pytest
from fastapi.testclient import TestClient

def test_login(client):
    """Test user login."""
    # Create a test user first
    response = client.post(
        "/api/auth/init-admin"
    )
    assert response.status_code == 200
    
    # Test login with correct credentials
    response = client.post(
        "/api/auth/token",
        data={"username": "admin", "password": "adminpassword"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
    
    # Test login with incorrect credentials
    response = client.post(
        "/api/auth/token",
        data={"username": "admin", "password": "wrongpassword"}
    )
    assert response.status_code == 401

def test_get_current_user(client, admin_token):
    """Test getting current user information."""
    response = client.get(
        "/api/auth/users/me",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "admin_test"
    assert response.json()["role"] == "admin"

def test_register_user(client, admin_token):
    """Test registering a new user."""
    # Test with admin token
    response = client.post(
        "/api/auth/register",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "full_name": "New User",
            "password": "newpassword",
            "role": "astronaut"
        }
    )
    assert response.status_code == 200
    assert response.json()["username"] == "newuser"
    assert response.json()["role"] == "astronaut"
    
    # Test registering with existing username
    response = client.post(
        "/api/auth/register",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "username": "newuser",
            "email": "another@example.com",
            "full_name": "Another User",
            "password": "anotherpassword",
            "role": "astronaut"
        }
    )
    assert response.status_code == 400

def test_permission_levels(client, admin_token, commander_token, astronaut_token):
    """Test different permission levels."""
    # Admin can access admin-only endpoint
    response = client.get(
        "/api/auth/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    
    # Commander cannot access admin-only endpoint
    response = client.get(
        "/api/auth/users",
        headers={"Authorization": f"Bearer {commander_token}"}
    )
    assert response.status_code == 403
    
    # Astronaut cannot access admin-only endpoint
    response = client.get(
        "/api/auth/users",
        headers={"Authorization": f"Bearer {astronaut_token}"}
    )
    assert response.status_code == 403
