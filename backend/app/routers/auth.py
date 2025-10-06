from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import List

from app.models.auth import (
    User, UserCreate, Token, authenticate_user, create_access_token,
    get_current_user, create_user, ACCESS_TOKEN_EXPIRE_MINUTES, UserInDB,
    has_permission
)
from app.models.database import SessionLocal
from app.models.auth import UserDB

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

# Dependency to get the current user
async def get_current_active_user(token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

# Dependency to check if user has admin role
async def get_current_admin_user(current_user: UserInDB = Depends(get_current_active_user)):
    if not has_permission(current_user, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# Dependency to check if user has commander role
async def get_current_commander_user(current_user: UserInDB = Depends(get_current_active_user)):
    if not has_permission(current_user, "commander"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=User)
async def register_user(user: UserCreate, current_user: UserInDB = Depends(get_current_admin_user)):
    """
    Register a new user (admin only).
    """
    db_user = create_user(user)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    return db_user

@router.get("/users/me", response_model=User)
async def read_users_me(current_user: UserInDB = Depends(get_current_active_user)):
    """
    Get current user information.
    """
    return current_user

@router.get("/users", response_model=List[User])
async def read_users(current_user: UserInDB = Depends(get_current_admin_user)):
    """
    Get all users (admin only).
    """
    db = SessionLocal()
    try:
        users = db.query(UserDB).all()
        return users
    finally:
        db.close()

@router.post("/init-admin")
async def initialize_admin():
    """
    Initialize the admin user if no users exist.
    This endpoint should be disabled in production.
    """
    db = SessionLocal()
    try:
        # Check if any users exist
        user_count = db.query(UserDB).count()
        if user_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Users already exist"
            )

        # Create admin user
        admin_user = UserCreate(
            username="admin",
            email="admin@example.com",
            full_name="Administrator",
            password="adminpassword",
            role="admin"
        )

        # Create commander user
        commander_user = UserCreate(
            username="commander",
            email="commander@example.com",
            full_name="Station Commander",
            password="commanderpassword",
            role="commander"
        )

        # Create astronaut user
        astronaut_user = UserCreate(
            username="astronaut",
            email="astronaut@example.com",
            full_name="Space Astronaut",
            password="astronautpassword",
            role="astronaut"
        )

        # Create users
        create_user(admin_user)
        create_user(commander_user)
        create_user(astronaut_user)

        return {"message": "Admin, commander, and astronaut users created successfully"}
    finally:
        db.close()
