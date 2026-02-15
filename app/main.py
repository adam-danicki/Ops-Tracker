from fastapi import FastAPI

import app.models  # noqa: F401
from app.api.projects import router as projects_router
from app.api.subjects import router as subjects_router
from app.api.lesions import router as lesions_router
from app.api.lesion_measurements import router as lesion_measurements_router


app = FastAPI(title="Ops Tracker")

@app.get("/")
def health():
    return {"status": "OK", "service": "Ops Tracker"}

app.include_router(projects_router)
app.include_router(subjects_router)
app.include_router(lesions_router)
app.include_router(lesion_measurements_router)
