"""
Tests for Authentication API
"""
import pytest
from fastapi import status


class TestAuthRegister:
    """Tests for user registration endpoint"""
    
    def test_register_success(self, client):
        """Test successful user registration"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securepassword123",
                "full_name": "New User"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_register_duplicate_email(self, client, test_user):
        """Test registration with existing email fails"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",  # Same as test_user
                "password": "anotherpassword123",
                "full_name": "Another User"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"].lower()
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email format"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "invalid-email",
                "password": "securepassword123",
                "full_name": "Test User"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_missing_fields(self, client):
        """Test registration with missing required fields"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com"
                # Missing password and full_name
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAuthLogin:
    """Tests for user login endpoint"""
    
    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post(
            "/api/auth/login",
            data={
                "username": "test@example.com",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client, test_user):
        """Test login with incorrect password"""
        response = client.post(
            "/api/auth/login",
            data={
                "username": "test@example.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post(
            "/api/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "somepassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_missing_credentials(self, client):
        """Test login with missing credentials"""
        response = client.post(
            "/api/auth/login",
            data={}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAuthMe:
    """Tests for current user endpoint"""
    
    def test_get_current_user_success(self, client, auth_headers, test_user):
        """Test getting current user info with valid token"""
        response = client.get("/api/auth/me", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name
    
    def test_get_current_user_no_token(self, client):
        """Test getting current user without token"""
        response = client.get("/api/auth/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestJWTHandler:
    """Tests for JWT utility functions"""
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        from auth.jwt_handler import get_password_hash, verify_password
        
        password = "mysecretpassword"
        hashed = get_password_hash(password)
        
        # Hashed password should be different from plain
        assert hashed != password
        
        # Verification should work
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False
    
    def test_create_and_decode_token(self):
        """Test JWT token creation and decoding"""
        from auth.jwt_handler import create_access_token, decode_access_token
        
        data = {"sub": "test@example.com", "user_id": 1}
        token = create_access_token(data)
        
        # Token should be a string
        assert isinstance(token, str)
        
        # Decode should return the same data
        decoded = decode_access_token(token)
        assert decoded is not None
        assert decoded["sub"] == data["sub"]
        assert decoded["user_id"] == data["user_id"]
    
    def test_decode_invalid_token(self):
        """Test decoding invalid token returns None"""
        from auth.jwt_handler import decode_access_token
        
        result = decode_access_token("invalid_token")
        assert result is None
