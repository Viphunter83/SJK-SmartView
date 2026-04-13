from pydantic import BaseModel
from typing import Optional, List

class GenerationResponse(BaseModel):
    status: str
    mockup_url: Optional[str] = None
    error: Optional[str] = None
    processing_time: float

class LocationInfo(BaseModel):
    id: str
    name: str
    category: str
