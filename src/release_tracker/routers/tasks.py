from typing import Annotated, Any

from fastapi import APIRouter, Query, Response, status

from release_tracker import crud
from release_tracker.dependencies import ProjectDep, SessionDep, TaskDep
from release_tracker.models import (
    TaskCreate,
    TaskPriority,
    TaskRead,
    TaskStatus,
    TaskUpdate,
)

router = APIRouter(tags=["tasks"])


@router.get("/tasks", response_model=list[TaskRead])
def list_tasks(
    session: SessionDep,
    project_id: int | None = None,
    project_slug: str | None = None,
    task_status: Annotated[TaskStatus | None, Query(alias="status")] = None,
    task_priority: Annotated[
        TaskPriority | None, Query(alias="priority")
    ] = None,
    overdue_only: bool = False,
) -> Any:
    return crud.list_tasks(
        session,
        project_id=project_id,
        project_slug=project_slug,
        task_status=task_status,
        task_priority=task_priority,
        overdue_only=overdue_only,
    )


@router.post(
    "/projects/{project_id}/tasks",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    project: ProjectDep, payload: TaskCreate, session: SessionDep
) -> Any:
    return crud.create_task(session, project.id, payload)


@router.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(task: TaskDep) -> Any:
    return task


@router.patch("/tasks/{task_id}", response_model=TaskRead)
def update_task(task: TaskDep, payload: TaskUpdate, session: SessionDep) -> Any:
    return crud.update_task(session, task, payload)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task: TaskDep, session: SessionDep) -> Response:
    crud.delete_task(session, task)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
