from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
import datetime

# Create database engine
DATABASE_URL = "sqlite:///./space_station_cargo.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Models
class Container(Base):
    __tablename__ = "containers"

    id = Column(String, primary_key=True)
    zone = Column(String, nullable=False)
    width = Column(Float, nullable=False)
    depth = Column(Float, nullable=False)
    height = Column(Float, nullable=False)

    items = relationship("Item", back_populates="container")

class Item(Base):
    __tablename__ = "items"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    width = Column(Float, nullable=False)
    depth = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    mass = Column(Float, nullable=False)
    priority = Column(Integer, nullable=False)
    expiry_date = Column(DateTime, nullable=True)
    usage_limit = Column(Integer, nullable=False)
    remaining_uses = Column(Integer, nullable=False)
    preferred_zone = Column(String, nullable=False)
    is_waste = Column(Boolean, default=False)

    # Position in container
    container_id = Column(String, ForeignKey("containers.id"), nullable=True)
    container = relationship("Container", back_populates="items")
    position_width = Column(Float, nullable=True)
    position_depth = Column(Float, nullable=True)
    position_height = Column(Float, nullable=True)

    # Orientation (0: original, 1: rotated width-depth, 2: rotated width-height, 3: rotated depth-height)
    orientation = Column(Integer, default=0)

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(String, nullable=True)
    action_type = Column(String, nullable=False)  # placement, retrieval, rearrangement, disposal
    item_id = Column(String, nullable=False)
    from_container = Column(String, nullable=True)
    to_container = Column(String, nullable=True)
    reason = Column(String, nullable=True)
    details = Column(String, nullable=True)  # JSON string for additional details

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String)
    role = Column(String, default="astronaut")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)
