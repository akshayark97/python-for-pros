from fastapi import FastAPI

app = FastAPI(title="Release Tracker API")

@app.get("/projects")
def list_projects() -> list[dict]:
    return [{"id": 1, "name": "Example"}]
