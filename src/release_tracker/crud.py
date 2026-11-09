from datetime import UTC, datetime

from pydantic import EmailStr
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from release_tracker.security import get_password_hash

from .models import (
    Project,
    ProjectCreate,
    ProjectUpdate,
    Task,
    TaskCreate,
    TaskPriority,
    TaskStatus,
    TaskUpdate,
    User,
)


def slugify(value: str) -> str:
    cleaned = "".join(c for c in value.lower() if c.isalnum() or c == " ")
    return "-".join(cleaned.split()) or "project"


def list_projects(session: Session) -> list[Project]:
    # TODO: Build a select statement ordered by Project.name and return the list of all projects.  # noqa: E501
    statement = select(Project).order_by(Project.name)
    return list(session.exec(statement).all())


def get_project(session: Session, project_id: int) -> Project | None:
    # TODO: Return the Project for `project_id`, or None if it doesn't exist.
    return session.get(Project, project_id)


def create_project(session: Session, payload: ProjectCreate) -> Project:
    # TODO: Build a Project from the payload, derive its slug, add/commit/refresh, return it.  # noqa: E501
    project = Project.model_validate(
        payload, update={"slug": slugify(payload.name)}
    )

    session.add(project)
    session.commit()
    session.refresh(project)
    return project


def update_project(
    session: Session, project: Project, payload: ProjectUpdate
) -> Project:
    # TODO: Apply payload to project (use exclude_unset=True so missing fields stay missing),  # noqa: E501
    # re-slugify if the name was set, then add/commit/refresh.

    updated_fields = payload.model_dump(exclude_unset=True)
    project.sqlmodel_update(updated_fields)

    if "name" in updated_fields and updated_fields["name"] is not None:
        project.slug = slugify(updated_fields["name"])

    session.add(project)
    session.commit()
    session.refresh(project)
    return project


def delete_project(session: Session, project: Project) -> None:
    # TODO: Delete the project and commit.
    session.delete(project)
    session.commit()


def list_tasks(
    session: Session,
    *,
    project_id: int | None = None,
    project_slug: str | None = None,
    task_status: TaskStatus | None = None,
    task_priority: TaskPriority | None = None,
    overdue_only: bool = False,
) -> list[Task]:
    statement = select(Task).options(selectinload(Task.project))  # type: ignore[arg-type]

    if project_id is not None:
        statement = statement.where(Task.project_id == project_id)
    if project_slug is not None:
        statement = statement.join(Project).where(Project.slug == project_slug)
    if task_status is not None:
        statement = statement.where(Task.status == task_status)
    if task_priority is not None:
        statement = statement.where(Task.priority == task_priority)
    if overdue_only:
        statement = statement.where(
            Task.due_date != None,  # noqa: E711
            Task.due_date < datetime.now(UTC).date(),  # type: ignore[operator]
            Task.status != TaskStatus.done,
        )

    return list(session.exec(statement).all())


def get_task(session: Session, task_id: int) -> Task | None:
    statement = (
        select(Task)
        .options(selectinload(Task.project))  # type: ignore[arg-type]
        .where(Task.id == task_id)
    )
    return session.exec(statement).first()


def create_task(session: Session, project_id: int, payload: TaskCreate) -> Task:
    task = Task.model_validate(payload, update={"project_id": project_id})
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def update_task(session: Session, task: Task, payload: TaskUpdate) -> Task:
    task.sqlmodel_update(payload.model_dump(exclude_unset=True))
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def delete_task(session: Session, task: Task) -> None:
    session.delete(task)
    session.commit()


def create_user(session: Session, *, email: str, password: str, is_active: bool = True) -> User:  # noqa: E501
    user = User(
        email=email.lower(),
        hashed_password=get_password_hash(password),
        is_active=is_active
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def get_user_by_email(session: Session, email: EmailStr) -> User | None:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()