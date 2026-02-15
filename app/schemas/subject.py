from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

# Pydantic model for Subject creation
class SubjectCreate(BaseModel):
    subject_code: str = Field(min_length=1, max_length=50)
    sex: Optional[str] = Field(default=None, max_length=10)
    age_at_diagnosis: Optional[int] = Field(default=None, ge=0, le=120)
    cancer_type: Optional[str] = Field(default=None, max_length=50)
    stage: Optional[str] = Field(default=None, max_length=10)

# Pydantic model for Subject update (partial)
class SubjectUpdate(BaseModel):
    sex: Optional[str] = Field(default=None, max_length=10)
    age_at_diagnosis: Optional[int] = Field(default=None, ge=0, le=120)
    cancer_type: Optional[str] = Field(default=None, max_length=50)
    stage: Optional[str] = Field(default=None, max_length=10)

# Pydantic model for Subject read (response)
class SubjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    subject_code: str
    sex: Optional[str] = None
    age_at_diagnosis: Optional[int] = None
    cancer_type: Optional[str] = None
    stage: Optional[str] = None
    created_at: datetime