from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

# Pydantic model for LesionMeasurement creation
class LesionMeasurementCreate(BaseModel):
    timepoint: str = Field(min_length=1, max_length=30)
    longest_diameter_mm: float = Field(ge=0)
    short_axis_mm: float = Field(ge=0)

    volume_mm3: Optional[float] = Field(default=None, ge=0)
    mean_hu: Optional[float] = None
    suv_max: Optional[float] = Field(default=None, ge=0)

    reviewer: Optional[str] = Field(default=None, max_length=100)
    confidence: float = Field(default=1.0, ge=0, le=1)

# Pydantic model for LesionMeasurement read (response)
class LesionMeasurementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lesion_id: int
    timepoint: str
    measured_at: datetime
    longest_diameter_mm: float
    short_axis_mm: float
    volume_mm3: Optional[float] = None
    mean_hu: Optional[float] = None
    suv_max: Optional[float] = None
    reviewer: Optional[str] = None
    confidence: float
