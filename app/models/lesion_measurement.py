from __future__ import annotations

from datetime import datetime
from sqlalchemy import (
    String, Float, DateTime, ForeignKey, UniqueConstraint, CheckConstraint, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

# Model for the "lesion_measurements" table
class LesionMeasurement(Base):
    __tablename__ = "lesion_measurements"
    __table_args__ = (
        UniqueConstraint("lesion_id", "timepoint", name="uq_measurement_lesion_timepoint"),
        CheckConstraint("longest_diameter_mm >= 0", name="ck_longest_diameter_nonneg"),
        CheckConstraint("short_axis_mm >= 0", name="ck_short_axis_nonneg"),
        CheckConstraint("confidence >= 0 AND confidence <= 1", name="ck_confidence_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lesion_id: Mapped[int] = mapped_column(
        ForeignKey("lesions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    timepoint: Mapped[str] = mapped_column(String(30), nullable=False)      # baseline, week_6, ...
    measured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    longest_diameter_mm: Mapped[float] = mapped_column(Float, nullable=False)
    short_axis_mm: Mapped[float] = mapped_column(Float, nullable=False)

    volume_mm3: Mapped[float | None] = mapped_column(Float, nullable=True)
    mean_hu: Mapped[float | None] = mapped_column(Float, nullable=True)     # CT density
    suv_max: Mapped[float | None] = mapped_column(Float, nullable=True)     # PET SUVmax

    reviewer: Mapped[str | None] = mapped_column(String(100), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    lesion = relationship("Lesion", back_populates="measurements")
