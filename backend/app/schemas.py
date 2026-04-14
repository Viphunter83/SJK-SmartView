from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any
from datetime import datetime
from uuid import UUID


class Point(BaseModel):
    x: float
    y: float


class LocationInfo(BaseModel):
    id: UUID
    name: str
    category: str
    address: Optional[str] = None
    coords_lat: Optional[float] = None
    coords_lng: Optional[float] = None
    primary_photo_url: Optional[str] = None
    # screen_geometry: унифицированный формат — всегда List[Point] или None
    screen_geometry: Optional[List[Point]] = None
    aspect_ratio: float = 1.77
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class LocationCreate(BaseModel):
    name: str
    category: str
    address: Optional[str] = None
    coords_lat: Optional[float] = None
    coords_lng: Optional[float] = None
    primary_photo_url: Optional[str] = None
    screen_geometry: Optional[List[Point]] = None
    aspect_ratio: float = 1.77


class GenerationResponse(BaseModel):
    status: str
    mockup_url: Optional[str] = None
    processing_time: float = 0.0
    error: Optional[str] = None
    mode: Optional[str] = "standard"


class MockupHistoryItem(BaseModel):
    id: UUID
    location_name: Optional[str] = None
    creative_url: str
    result_url: Optional[str] = None
    status: str
    created_at: datetime
    processing_time: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class CornerDetectionResponse(BaseModel):
    corners: List[Point]
    confidence: float
    message: Optional[str] = None
    method: str = "fallback"  # "yolo_obb" | "opencv" | "fallback"
