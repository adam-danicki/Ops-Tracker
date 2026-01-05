from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db import get_db
from app.models.project import Project
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

# Delete all projects. Returns 204 on success.
@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_all_projects(db: Session = Depends(get_db)):
    db.query(Project).delete()
    db.commit()
    return None

