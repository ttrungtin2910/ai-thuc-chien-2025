"""
Security Module

Authentication and authorization utilities.
"""

import hashlib
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .config import Config

# Security instance
security = HTTPBearer()

# Demo user database - In production, this should be in a real database
fake_users = {
    "admin": {
        "username": "admin",
        "password": hashlib.sha256("password123".encode()).hexdigest(),
        "full_name": "Administrator",
        "role": "admin"
    }
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password


def hash_password(password: str) -> str:
    """Hash a password"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=Config.ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, Config.SECRET_KEY, algorithm=Config.ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(
            credentials.credentials, 
            Config.SECRET_KEY, 
            algorithms=[Config.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_user(username: str) -> Optional[Dict]:
    """Get user by username"""
    return fake_users.get(username)


def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """Authenticate user with username and password"""
    user = get_user(username)
    if not user or not verify_password(password, user["password"]):
        return None
    return user
