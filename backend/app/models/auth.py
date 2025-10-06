from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.models.database import SessionLocal, UserDB

# JWT Configuration
SECRET_KEY = "8f9e2a7b1d6c5e3f8a9d2b7c4e5f8a9d2b7c4e5f8a9d2b7c4e5f8a9d2b7c4e5f"  # Generated secure key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

# User models
class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: str = "astronaut"  # Default role

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: int
    hashed_password: str
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Database model is defined in database.py

# Password functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# User functions
def get_user(username: str):
    db = SessionLocal()
    try:
        user = db.query(UserDB).filter(UserDB.username == username).first()
        if user:
            return UserInDB(
                id=user.id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                role=user.role,
                hashed_password=user.hashed_password,
                is_active=user.is_active,
                created_at=user.created_at
            )
    finally:
        db.close()
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# Token functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        token_data = TokenData(username=username, role=payload.get("role"))
    except JWTError:
        return None

    user = get_user(username=token_data.username)
    if user is None:
        return None

    return user

def create_user(user: UserCreate):
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(UserDB).filter(UserDB.username == user.username).first()
        if existing_user:
            return None

        # Create new user
        hashed_password = get_password_hash(user.password)
        db_user = UserDB(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_password,
            role=user.role
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return User(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            full_name=db_user.full_name,
            role=db_user.role,
            is_active=db_user.is_active,
            created_at=db_user.created_at
        )
    finally:
        db.close()

# Role-based permissions
def has_permission(user: UserInDB, required_role: str) -> bool:
    """Check if user has the required role or higher."""
    role_hierarchy = {
        "admin": 3,
        "commander": 2,
        "astronaut": 1
    }

    user_role_level = role_hierarchy.get(user.role, 0)
    required_role_level = role_hierarchy.get(required_role, 0)

    return user_role_level >= required_role_level
