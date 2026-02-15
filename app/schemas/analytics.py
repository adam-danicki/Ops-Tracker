from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel

# Pydantic schemas for analytics results
class CountByValue(BaseModel):
    value: str | None
    count: int

# Date range for measurements
class DateRange(BaseModel):
    start: datetime | None
    end: datetime | None

# Pydantic schema for project analytics results
class ProjectAnalytics(BaseModel):
    project_id: int
    subjects: int
    lesions: int
    measurements: int
    modalities: list[CountByValue]
    timepoints: list[CountByValue]
    measured_at_range: DateRange
    avg_confidence: float | None

# Pydantic schema for lesion change analytics results
class LesionChange(BaseModel):
    lesion_id: int
    baseline_measured_at: datetime | None
    baseline_longest_mm: float | None
    latest_measured_at: datetime | None
    latest_longest_mm: float | None
    pct_change_longest: float | None