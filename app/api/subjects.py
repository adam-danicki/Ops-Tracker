from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db import get_db
from app.models.project import Project
from app.models.subject import Subject
from app.schemas.subject import SubjectCreate, SubjectRead, SubjectUpdate

router = APIRouter(tags=["subjects"])

# Create a new subject under a specific project. Returns 201 on success; 400 if subject code already exists within the project.
@router.post("/projects/{project_id}/subjects", response_model=SubjectRead, status_code=status.HTTP_201_CREATED)
def create_subject(project_id: int, payload: SubjectCreate, db: Session = Depends(get_db)):
    if not db.get(Project, project_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    subject = Subject(project_id=project_id, **payload.model_dump())
    db.add(subject)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="subject_code already exists for this project")

    db.refresh(subject)
    return subject

# List all subjects for a specific project, ordered by creation time (newest first). Returns 404 if the project does not exist.
@router.get("/projects/{project_id}/subjects", response_model=list[SubjectRead])
def list_subjects(project_id: int, db: Session = Depends(get_db)):
    if not db.get(Project, project_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    stmt = select(Subject).where(Subject.project_id == project_id).order_by(Subject.created_at.desc())
    return db.execute(stmt).scalars().all()

# Retrieve a single subject by ID. Returns 404 if not found.
@router.get("/subjects/{subject_id}", response_model=SubjectRead)
def get_subject(subject_id: int, db: Session = Depends(get_db)):
    subject = db.get(Subject, subject_id)
    if not subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
    return subject

# Partially update a subject's details. Returns 404 if the subject does not exist.
@router.patch("/subjects/{subject_id}", response_model=SubjectRead)
def update_subject(subject_id: int, payload: SubjectUpdate, db: Session = Depends(get_db)):
    subject = db.get(Subject, subject_id)
    if not subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(subject, k, v)

    db.commit()
    db.refresh(subject)
    return subject

# Delete a subject by ID. Returns 204 on success; 404 if not found.
@router.delete("/subjects/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    subject = db.get(Subject, subject_id)
    if not subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
    db.delete(subject)
    db.commit()
    return None