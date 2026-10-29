from sqlmodel import Session, select
from fastapi import HTTPException, status

from .models import Project, ProjectCreate, ProjectUpdate


def slugify(value: str) -> str:
    cleaned = "".join(c for c in value.lower() if c.isalnum() or c == " ")
    return "-".join(cleaned.split()) or "project"


def list_projects(session: Session) -> list[Project]:
    # TODO: Build a select statement ordered by Project.name and return the list of all projects.
    statement = select(Project).order_by(Project.name)
    return list(session.exec(statement).all())


def get_project(session: Session, project_id: int) -> Project | None:
    # TODO: Return the Project for `project_id`, or None if it doesn't exist.
    return session.get(Project, project_id)


def create_project(session: Session, payload: ProjectCreate) -> Project:
    # TODO: Build a Project from the payload, derive its slug, add/commit/refresh, return it.
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
    # TODO: Apply payload to project (use exclude_unset=True so missing fields stay missing),
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
