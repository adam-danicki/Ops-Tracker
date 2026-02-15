from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db import get_db
from app.models.lesion import Lesion
from app.models.lesion_measurement import LesionMeasurement
from app.schemas.lesion_measurement import LesionMeasurementCreate, LesionMeasurementRead

router = APIRouter(tags=["lesion_measurements"])

# Create a new measurement for a specific lesion. Returns 201 on success; 404 if the lesion does not exist; 409 if a measurement for the same lesion + timepoint already exists.
@router.post("/lesions/{lesion_id}/measurements", response_model=LesionMeasurementRead, status_code=status.HTTP_201_CREATED)
def create_measurement(lesion_id: int, payload: LesionMeasurementCreate, db: Session = Depends(get_db)):
    if not db.get(Lesion, lesion_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesion not found")

    m = LesionMeasurement(lesion_id=lesion_id, **payload.model_dump())
    db.add(m)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="measurement already exists for this lesion + timepoint")

    db.refresh(m)
    return m

# List all measurements for a specific lesion, ordered by measurement time (oldest first). Returns 404 if the lesion does not exist.
@router.get("/lesions/{lesion_id}/measurements", response_model=list[LesionMeasurementRead])
def list_measurements(lesion_id: int, db: Session = Depends(get_db)):
    if not db.get(Lesion, lesion_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesion not found")

    stmt = select(LesionMeasurement).where(LesionMeasurement.lesion_id == lesion_id).order_by(LesionMeasurement.measured_at.asc())
    return db.execute(stmt).scalars().all()
