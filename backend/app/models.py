from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from .database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String, default="manager")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Location(Base):
    __tablename__ = "locations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    category = Column(String)
    description = Column(String)
    address = Column(String)
    coords_lat = Column(Float)
    coords_lng = Column(Float)
    primary_photo_url = Column(String)
    screen_geometry = Column(JSON) # { "corners": [[x,y],...] }
    aspect_ratio = Column(Float, default=1.77)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Mockup(Base):
    __tablename__ = "mockups"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id", ondelete="SET NULL"))
    creative_url = Column(String, nullable=False)
    result_url = Column(String)
    metadata_json = Column("metadata", JSON) # Renamed to metadata_json to avoid conflict with SQLAlchemy metadata
    status = Column(String, default="pending") # 'pending', 'processing', 'completed', 'failed'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
