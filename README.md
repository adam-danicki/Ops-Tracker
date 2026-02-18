How to start the app:
 - docker compose up
 - docker compose up --build (if not built before)

To open docs:
 - http://localhost:8000/docs

To run seeded file to fill backend database:
 - docker compose up -d --build
 - docker compose exec api python scripts/seed_db.py --clear --projects 2 --subjects 15 --lesions 3 --measurements 4

To inspect DB in docker:
 - docker exec -it ops_tracker_db psql -U ops -d ops_tracker
Then inside psql:
 - \dt          = list tables
 - \d projects  = describe a table
 - \q quit      = quit

# Ops-Tracker API

Ops-Tracker is a FastAPI + PostgreSQL backend for organizing and tracking longitudinal lesion data in a clean hierarchy:

**Project → Subject → Lesion → LesionMeasurement**

It’s built to support consistent data entry (unique IDs per scope), easy querying through REST endpoints, and fast local development through Docker + a seeding script.

----------------------------------------------------------------------------------------

## What this project does

- Stores projects (study / dataset / cohort containers)
- Stores subjects (patients/cases) under a project
- Stores lesions under a subject
- Stores lesion measurements over time (baseline, week_6, etc.)
- Enforces relational integrity and prevents common duplicates via constraints
- Provides OpenAPI docs (Swagger UI) for testing endpoints quickly

----------------------------------------------------------------------------------------

## Tech stack

- Python 3.12
- FastAPI (REST API + OpenAPI/Swagger UI)
- SQLAlchemy ORM
- PostgreSQL
- Docker / Docker Compose

----------------------------------------------------------------------------------------

## Data model

### Entities

- **Project**
  - `id`, `name`, `description`, `created_at`
- **Subject**
  - belongs to a Project
  - `subject_code` + optional clinical fields (sex, age_at_diagnosis, cancer_type, stage, etc.)
- **Lesion**
  - belongs to a Subject
  - `lesion_label`, optional metadata (anatomic_site, laterality, modality, etc.)
- **LesionMeasurement**
  - belongs to a Lesion
  - `timepoint`, `measured_at`, `longest_diameter_mm`, `short_axis_mm`, optional fields (volume, HU, SUV, reviewer, confidence, etc.)

### Relationships

- Project has many Subjects
- Subject has many Lesions
- Lesion has many Measurements

### Integrity rules

- Prevents duplicates with scoped uniqueness constraints:
  - subject code unique per project
  - lesion label unique per subject
  - timepoint unique per lesion
- Validates numeric ranges (e.g., non-negative measurements, confidence in `[0, 1]`)
- Cascading deletes: removing a parent removes its children (Project → Subject → Lesion → Measurement)

----------------------------------------------------------------------------------------

## API Overview

OpenAPI (Swagger UI):  
- `http://localhost:8000/docs`

Core endpoints you can use right away:

### Projects
- `POST /projects/` create a project
- `GET /projects/` list projects
- `GET /projects/{project_id}` get one project
- `PATCH /projects/{project_id}` update project
- `DELETE /projects/{project_id}` delete project (cascades)
- `DELETE /projects/` delete all projects (**use carefully**)

### Subjects
- `POST /projects/{project_id}/subjects` create subject under a project
- `GET /projects/{project_id}/subjects` list subjects in a project
- `GET /subjects/{subject_id}` get one subject
- `PATCH /subjects/{subject_id}` update subject
- `DELETE /subjects/{subject_id}` delete subject (cascades)

### Lesions
- `POST /subjects/{subject_id}/lesions` create lesion under a subject
- `GET /subjects/{subject_id}/lesions` list lesions in a subject
- `GET /lesions/{lesion_id}` get one lesion
- `PATCH /lesions/{lesion_id}` update lesion
- `DELETE /lesions/{lesion_id}` delete lesion (cascades)

### Measurements
- `POST /lesions/{lesion_id}/measurements` create measurement for a lesion
- `GET /lesions/{lesion_id}/measurements` list measurements for a lesion

----------------------------------------------------------------------------------------

## Running with Docker

### 1) Download dependencies (local)
- **Python 3.12+** installed and available
To install Python dependencies:
- pip install -r requirements.txt


### 2) Build + start services (Docker)
From the repo root:

```bash
docker compose up -d --build

