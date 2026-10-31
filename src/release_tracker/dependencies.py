from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlmodel import Session

from . import crud
from .database import get_session
from .models import Project

SessionDep = Annotated[Session, Depends(get_session)]


def get_project_or_404(project_id: int, session: SessionDep) -> Project:
    project = crud.get_project(session, project_id)

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    return project


ProjectDep = Annotated[Project, Depends(get_project_or_404)]
