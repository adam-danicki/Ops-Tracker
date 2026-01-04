from fastapi import FastAPI

app = FastAPI(title="Ops Tracker")

@app.get("/")
def health():
    return {"status": "OK", "service": "Ops Tracker"}