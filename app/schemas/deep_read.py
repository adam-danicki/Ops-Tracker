from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict

# Pydantic schema for lesion measurement data
class LesionMeasurementBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lesion_id: int
    timepoint: str
    measured_at: datetime
    longest_diameter_mm: float
    short_axis_mm: float
    volume_mm3: float | None = None
    mean_hu: float | None = None
    suv_max: float | None = None
    reviewer: str | None = None
    confidence: float

# Pydantic schema for lesion data, including nested measurements
class LesionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subject_id: int
    lesion_label: str
    anatomic_site: str | None = None
    laterality: str | None = None
    modality: str | None = None
    created_at: datetime
    measurements: list[LesionMeasurementBase] = []

# Pydantic schema for subject data, including nested lesions and measurements
class SubjectBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    subject_code: str
    sex: str | None = None
    age_at_diagnosis: int | None = None
    cancer_type: str | None = None
    stage: str | None = None
    created_at: datetime
    lesions: list[LesionBase] = []

# Pydantic schema for project data, including nested subjects, lesions, and measurements
class ProjectBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    created_at: datetime
    subjects: list[SubjectBase] = []