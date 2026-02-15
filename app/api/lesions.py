from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db import get_db
from app.models.subject import Subject
from app.models.lesion import Lesion
from app.schemas.lesion import LesionCreate, LesionRead, LesionUpdate

router = APIRouter(tags=["lesions"])

# Create a new lesion under a specific subject. Returns 201 on success; 400 if lesion label already exists within the subject.
@router.post("/subjects/{subject_id}/lesions", response_model=LesionRead, status_code=status.HTTP_201_CREATED)
def create_lesion(subject_id: int, payload: LesionCreate, db: Session = Depends(get_db)):
    if not db.get(Subject, subject_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")

    lesion = Lesion(subject_id=subject_id, **payload.model_dump())
    db.add(lesion)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="lesion_label already exists for this subject")

    db.refresh(lesion)
    return lesion

# List all lesions for a specific subject, ordered by creation time (newest first). Returns 404 if the subject does not exist.
@router.get("/subjects/{subject_id}/lesions", response_model=list[LesionRead])
def list_lesions(subject_id: int, db: Session = Depends(get_db)):
    if not db.get(Subject, subject_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")

    stmt = select(Lesion).where(Lesion.subject_id == subject_id).order_by(Lesion.created_at.desc())
    return db.execute(stmt).scalars().all()

# Retrieve a single lesion by ID. Returns 404 if not found.
@router.get("/lesions/{lesion_id}", response_model=LesionRead)
def get_lesion(lesion_id: int, db: Session = Depends(get_db)):
    lesion = db.get(Lesion, lesion_id)
    if not lesion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesion not found")
    return lesion

# Partially update a lesion's details. Returns 404 if the lesion does not exist.
@router.patch("/lesions/{lesion_id}", response_model=LesionRead)
def update_lesion(lesion_id: int, payload: LesionUpdate, db: Session = Depends(get_db)):
    lesion = db.get(Lesion, lesion_id)
    if not lesion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesion not found")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(lesion, k, v)

    db.commit()
    db.refresh(lesion)
    return lesion

# Delete a lesion by ID. Returns 204 on success; 404 if not found.
@router.delete("/lesions/{lesion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesion(lesion_id: int, db: Session = Depends(get_db)):
    lesion = db.get(Lesion, lesion_id)
    if not lesion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesion not found")
    db.delete(lesion)
    db.commit()
    return None
