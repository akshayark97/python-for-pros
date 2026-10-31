from typing import Any

from fastapi import APIRouter, HTTPException, Response, status

from .. import crud
from ..dependencies import ProjectDep, SessionDep
from ..models import ProjectCreate, ProjectRead, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=list[ProjectRead])
def list_projects(session: SessionDep):
    return crud.list_projects(session)


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project: ProjectDep):
    return project


@router.post(
    "/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED
)
def create_project(payload: ProjectCreate, session: SessionDep):
    return crud.create_project(session, payload)


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int, payload: ProjectUpdate, session: SessionDep
):
    project = crud.get_project(session, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    return crud.update_project(session, project, payload)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, session: SessionDep):
    project = crud.get_project(session, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    crud.delete_project(session, project)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
