from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from . import crud
from .database import get_session
from .dependencies import ProjectDep
from .models import ProjectCreate, ProjectRead, ProjectUpdate

app = FastAPI(
    title="Release Tracker API",
    description="An API for tracking project milestones and developer tasks.",
)

SessionDep = Annotated[Session, Depends(get_session)]


def slugify(value: str) -> str:
    cleaned = "".join(c for c in value.lower() if c.isalnum() or c == " ")
    return "-".join(cleaned.split()) or "project"

@app.exception_handler(IntegrityError)
def handle_integrity_error(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "detail": "Data conflict occured (e.g., duplicate entry)."
        }
    )

@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "app": "Release Tracker API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/projects", response_model=list[ProjectRead])
def list_projects(session: SessionDep):
    return crud.list_projects(session)


@app.get("/projects/{project_id}", response_model=ProjectRead)
def get_project(project: ProjectDep):
    return project


@app.post(
    "/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED
)
def create_project(payload: ProjectCreate, session: SessionDep):
    return crud.create_project(session, payload)


@app.patch("/projects/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int, payload: ProjectUpdate, session: SessionDep
):
    project = crud.get_project(session, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    return crud.update_project(session, project, payload)


@app.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, session: SessionDep):
    project = crud.get_project(session, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    crud.delete_project(session, project)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
