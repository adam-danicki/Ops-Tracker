from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func, select

from app.db import get_db
from app.models.lesion import Lesion
from app.models.lesion_measurement import LesionMeasurement
from app.models.project import Project
from app.models.subject import Subject
from app.schemas.analytics import CountByValue, DateRange, ProjectAnalytics
from app.schemas.deep_read import ProjectBase
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])

# Create a new project. Returns 201 on success; 400 if a project with the same name exists.
@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    exists = db.execute(select(Project).where(Project.name == payload.name)).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project already exists")

    project = Project(name=payload.name, description=payload.description)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

# List all projects ordered by creation time (newest first).
@router.get("/", response_model=list[ProjectRead])
def list_projects(db: Session = Depends(get_db)):
    projects = db.execute(select(Project).order_by(Project.created_at.desc())).scalars().all()
    return projects

# Retrieve a single project by ID. Returns 404 if not found.
@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project

# Partially update a project's name and/or description. Returns 404 if the project does not exist.
@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if payload.name is not None:
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description

    db.commit()
    db.refresh(project)
    return project

# Delete a project by ID. Returns 204 on success; 404 if not found.
@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    db.delete(project)
    db.commit()
    return None

# Retrieve a project along with all its nested subjects, lesions, and measurements. Returns 404 if not found.
@router.get("/{project_id}/deep", response_model=ProjectBase)
def get_project_deep(project_id: int, db: Session = Depends(get_db)):
    stmt = (
        select(Project)
        .where(Project.id == project_id)
        .options(
            selectinload(Project.subjects)
            .selectinload(Subject.lesions)
            .selectinload(Lesion.measurements)
        )
    )
    project = db.execute(stmt).scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project

# Retrieve analytics overview for a project, including counts and distributions. Returns 404 if the project does not exist.
@router.get("/{project_id}/analytics/overview", response_model=ProjectAnalytics)
def project_analytics(project_id: int, db: Session = Depends(get_db)):
    if not db.get(Project, project_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    subjects_ct = db.execute(
        select(func.count()).select_from(Subject).where(Subject.project_id == project_id)
    ).scalar_one()

    lesions_ct = db.execute(
        select(func.count())
        .select_from(Lesion)
        .join(Subject, Subject.id == Lesion.subject_id)
        .where(Subject.project_id == project_id)
    ).scalar_one()

    measurements_ct = db.execute(
        select(func.count())
        .select_from(LesionMeasurement)
        .join(Lesion, Lesion.id == LesionMeasurement.lesion_id)
        .join(Subject, Subject.id == Lesion.subject_id)
        .where(Subject.project_id == project_id)
    ).scalar_one()

    modality_rows = db.execute(
        select(Lesion.modality, func.count())
        .select_from(Lesion)
        .join(Subject, Subject.id == Lesion.subject_id)
        .where(Subject.project_id == project_id)
        .group_by(Lesion.modality)
        .order_by(func.count().desc())
    ).all()

    timepoint_rows = db.execute(
        select(LesionMeasurement.timepoint, func.count())
        .select_from(LesionMeasurement)
        .join(Lesion, Lesion.id == LesionMeasurement.lesion_id)
        .join(Subject, Subject.id == Lesion.subject_id)
        .where(Subject.project_id == project_id)
        .group_by(LesionMeasurement.timepoint)
        .order_by(func.count().desc())
    ).all()

    min_max = db.execute(
        select(func.min(LesionMeasurement.measured_at), func.max(LesionMeasurement.measured_at))
        .select_from(LesionMeasurement)
        .join(Lesion, Lesion.id == LesionMeasurement.lesion_id)
        .join(Subject, Subject.id == Lesion.subject_id)
        .where(Subject.project_id == project_id)
    ).one()

    avg_conf = db.execute(
        select(func.avg(LesionMeasurement.confidence))
        .select_from(LesionMeasurement)
        .join(Lesion, Lesion.id == LesionMeasurement.lesion_id)
        .join(Subject, Subject.id == Lesion.subject_id)
        .where(Subject.project_id == project_id)
    ).scalar_one()

    return ProjectAnalytics(
        project_id=project_id,
        subjects=int(subjects_ct),
        lesions=int(lesions_ct),
        measurements=int(measurements_ct),
        modalities=[CountByValue(value=v, count=int(c)) for v, c in modality_rows],
        timepoints=[CountByValue(value=v, count=int(c)) for v, c in timepoint_rows],
        measured_at_range=DateRange(start=min_max[0], end=min_max[1]),
        avg_confidence=float(avg_conf) if avg_conf is not None else None,
    )

# Delete all projects. Returns 204 on success.
@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_all_projects(db: Session = Depends(get_db)):
    db.query(Project).delete()
    db.commit()
    return None

