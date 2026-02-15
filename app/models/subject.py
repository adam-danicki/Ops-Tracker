from __future__ import annotations

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

# Model for the "subjects" table
class Subject(Base):
    __tablename__ = "subjects"
    __table_args__ = (
        UniqueConstraint("project_id", "subject_code", name="uq_subject_project_code"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    subject_code: Mapped[str] = mapped_column(String(50), nullable=False)
    sex: Mapped[str | None] = mapped_column(String(10), nullable=True)
    age_at_diagnosis: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cancer_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    stage: Mapped[str | None] = mapped_column(String(10), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )

    project = relationship("Project", back_populates="subjects")
    lesions = relationship("Lesion", back_populates="subject", cascade="all, delete-orphan")

    