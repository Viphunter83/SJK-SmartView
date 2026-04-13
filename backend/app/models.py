from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base
import uuid


# ─────────────────────────────────────────────────────────────
# UUID-совместимый тип (работает с PostgreSQL и SQLite)
# ─────────────────────────────────────────────────────────────
class GUID(TypeDecorator):
    """Platform-independent GUID type: UUID для PG, CHAR(36) для SQLite."""
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return str(value) if not isinstance(value, uuid.UUID) else value
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            return uuid.UUID(value)
        return value


# ─────────────────────────────────────────────────────────────
# Models
# ─────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    firebase_uid = Column(String, unique=True, nullable=True, index=True)  # Firebase Auth UID
    full_name = Column(String)
    role = Column(String, default="manager")  # 'manager', 'admin'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    mockups = relationship("Mockup", back_populates="user", cascade="all, delete-orphan")


class Location(Base):
    __tablename__ = "locations"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)
    category = Column(String)
    description = Column(String)
    address = Column(String)
    coords_lat = Column(Float)
    coords_lng = Column(Float)
    primary_photo_url = Column(String)
    # screen_geometry хранит массив 4-х точек: [{"x": 0, "y": 0}, ...]
    screen_geometry = Column(JSON)
    aspect_ratio = Column(Float, default=1.77)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    mockups = relationship("Mockup", back_populates="location")


class Mockup(Base):
    __tablename__ = "mockups"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    location_id = Column(GUID(), ForeignKey("locations.id", ondelete="SET NULL"), nullable=True)
    creative_url = Column(String, nullable=False)
    result_url = Column(String)
    metadata_json = Column("metadata", JSON)
    status = Column(String, default="pending")  # pending | processing | completed | failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="mockups")
    location = relationship("Location", back_populates="mockups")
