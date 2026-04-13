from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any
from datetime import datetime
from uuid import UUID

class LocationInfo(BaseModel):
    id: UUID
    name: str
    category: str
    address: Optional[str] = None
    primary_photo_url: Optional[str] = None
    screen_geometry: Optional[dict] = None
    aspect_ratio: float = 1.77
    
    model_config = ConfigDict(from_attributes=True)

class GenerationResponse(BaseModel):
    status: str
    mockup_url: Optional[str] = None
    processing_time: float
    error: Optional[str] = None

class MockupHistoryItem(BaseModel):
    id: UUID
    location_name: Optional[str] = None
    creative_url: str
    result_url: Optional[str] = None
    status: str
    created_at: datetime
    processing_time: float

    model_config = ConfigDict(from_attributes=True)
