from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

# Pydantic model for LesionMeasurement creation
class LesionCreate(BaseModel):
    lesion_label: str = Field(min_length=1, max_length=50)
    anatomic_site: Optional[str] = Field(default=None, max_length=100)
    laterality: Optional[str] = Field(default=None, max_length=10)
    modality: Optional[str] = Field(default=None, max_length=20)

# Pydantic model for LesionMeasurement update (partial)
class LesionUpdate(BaseModel):
    anatomic_site: Optional[str] = Field(default=None, max_length=100)
    laterality: Optional[str] = Field(default=None, max_length=10)
    modality: Optional[str] = Field(default=None, max_length=20)

# Pydantic model for LesionMeasurement read (response)
class LesionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subject_id: int
    lesion_label: str
    anatomic_site: Optional[str] = None
    laterality: Optional[str] = None
    modality: Optional[str] = None
    created_at: datetime