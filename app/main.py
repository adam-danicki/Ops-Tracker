from fastapi import FastAPI
from app.api.projects import router as projects_router


app = FastAPI(title="Ops Tracker")

@app.get("/")
def health():
    return {"status": "OK", "service": "Ops Tracker"}

app.include_router(projects_router)
