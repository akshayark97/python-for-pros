from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import EmailStr, StringConstraints
from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel


def utc_now() -> datetime:
    return datetime.now(UTC)


class TaskStatus(StrEnum):
    planned = "planned"
    in_progress = "in_progress"
    blocked = "blocked"
    done = "done"


class TaskPriority(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


ProjectName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=2),
]

TaskTitle = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=2),
]


# --- Project ---


class ProjectBase(SQLModel):
    name: ProjectName = Field(unique=True)
    description: str | None = None


class Project(ProjectBase, table=True):
    __tablename__ = "projects"

    id: int | None = Field(default=None, primary_key=True)
    slug: str = Field(unique=True)

    tasks: list[Task] = Relationship(back_populates="project")

    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(SQLModel):
    name: ProjectName | None = None
    description: str | None = None


class ProjectRead(ProjectBase):
    id: int
    slug: str
    created_at: datetime


# --- Task ---


class TaskBase(SQLModel):
    title: TaskTitle
    details: str | None = None
    status: TaskStatus = TaskStatus.planned
    priority: TaskPriority = TaskPriority.medium
    due_date: date | None = None


class Task(TaskBase, table=True):
    __tablename__ = "tasks"

    id: int | None = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id", index=True)

    project: Project = Relationship(back_populates="tasks")

    @property
    def project_name(self) -> str:
        return self.project.name

    @property
    def project_slug(self) -> str:
        return self.project.slug

class TaskCreate(TaskBase):
    pass


class TaskUpdate(SQLModel):
    title: TaskTitle | None = None
    details: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: date | None = None


class TaskRead(TaskBase):
    id: int
    project_id: int
    project_name: str
    project_slug: str


# --- User ---

class UserBase(SQLModel):
    email: EmailStr = Field(unique=True)
    is_active: bool = True


class UserCreate(SQLModel):
    email: EmailStr
    password: str


class User(UserBase, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str


class UserRead(UserBase):
    id: int


# --- Auth ---

class AccessToken(SQLModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"