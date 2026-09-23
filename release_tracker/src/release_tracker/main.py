from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI(title="Release Tracker API")


class ProjectRead(BaseModel):
    id: int
    name: str
    slug: str


@app.get("/projects/{project_id}", response_model=ProjectRead)
def get_project(project_id: int):
    project = mock_database.get(project_id)
    # EXERCISE STEP 1:
    # If `not project`, raise an HTTPException with status code
    # status.HTTP_404_NOT_FOUND and detail "Project not found".

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project

@app.get("/projects", response_model=list[ProjectRead])
def list_projects(slug: str | None = None):
    projects = list(mock_database.values())
    # EXERCISE STEP 2:
    # If slug is None, return all projects.
    # Otherwise, return only the projects whose `slug` attribute equals the given slug.

    if slug is None:
        return projects
    return [p for p in projects if slug == p.slug]

mock_database: dict[int, ProjectRead] = {
    1: ProjectRead(id=1, name="Frontend Redesign", slug="frontend-redesign"),
    2: ProjectRead(id=2, name="API v2", slug="api-v2"),
    3: ProjectRead(id=3, name="Database Migration", slug="database-migration"),
}
