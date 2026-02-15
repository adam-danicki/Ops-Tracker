from __future__ import annotations

from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

# Model for the "lesions" table
class Lesion(Base):
    __tablename__ = "lesions"
    __table_args__ = (
        UniqueConstraint("subject_id", "lesion_label", name="uq_lesion_subject_label"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    lesion_label: Mapped[str] = mapped_column(String(50), nullable=False)          # e.g. T1, Target-2
    anatomic_site: Mapped[str | None] = mapped_column(String(100), nullable=True)  # lung, liver
    laterality: Mapped[str | None] = mapped_column(String(10), nullable=True)      # left/right/none
    modality: Mapped[str | None] = mapped_column(String(20), nullable=True)        # CT/MRI/PET

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    subject = relationship("Subject", back_populates="lesions")
    measurements = relationship("LesionMeasurement", back_populates="lesion", cascade="all, delete-orphan")
