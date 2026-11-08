from typing import Any

from fastapi import APIRouter, Response, status

from release_tracker import crud
from release_tracker.dependencies import CurrentUserDep, ProjectDep, SessionDep
from release_tracker.models import ProjectCreate, ProjectRead, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=list[ProjectRead])
def list_projects(session: SessionDep) -> Any:
    return crud.list_projects(session)


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project: ProjectDep) -> Any:
    return project


@router.post(
    "/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED
)
def create_project(
    payload: ProjectCreate, session: SessionDep, current_user: CurrentUserDep
) -> Any:
    return crud.create_project(session, payload)


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project: ProjectDep, payload: ProjectUpdate, session: SessionDep
) -> Any:
    return crud.update_project(session, project, payload)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project: ProjectDep, session: SessionDep) -> Response:
    crud.delete_project(session, project)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
