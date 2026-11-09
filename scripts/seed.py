import argparse
from datetime import date, timedelta

from sqlalchemy import delete
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlmodel import Session, select

from release_tracker import crud
from release_tracker.database import get_engine
from release_tracker.models import (
    Project,
    ProjectCreate,
    Task,
    TaskPriority,
    TaskStatus,
    User,
)


def seed(*, reset: bool = False) -> None:
    try:
        with Session(get_engine()) as session:
            if reset:
                session.execute(delete(Task))
                session.execute(delete(Project))
                session.execute(delete(User))
                session.commit()
                print("Cleared existing project, task, and user data.")

            existing_project = session.exec(select(Project.id).limit(1)).first()
            if existing_project is not None:
                print("Sample project data already exists.")
                return

            crud.create_user(
                session, email="admin@example.com", password="password123"
            )
            crud.create_user(
                session, email="viewer@example.com", password="password123"
            )

            api_project = crud.create_project(
                session,
                ProjectCreate(
                    name="Release Tracker API",
                    description="Primary backend service for release planning.",
                ),
            )
            docs_project = crud.create_project(
                session,
                ProjectCreate(
                    name="Developer Docs",
                    description="Documentation updates for the launch week.",
                ),
            )
            ops_project = crud.create_project(
                session,
                ProjectCreate(
                    name="Operations Console",
                    description="Internal tooling for support workflows and incident follow-up.",
                ),
            )

            session.add_all(
                [
                    Task(
                        project_id=api_project.id,
                        title="Design the project schema",
                        details="Finalize projects and tasks tables before the first release.",
                        status=TaskStatus.done,
                        priority=TaskPriority.high,
                        due_date=date.today() - timedelta(days=2),
                    ),
                    Task(
                        project_id=api_project.id,
                        title="Add project CRUD endpoints",
                        details="Implement create, list, detail, and update routes.",
                        status=TaskStatus.in_progress,
                        priority=TaskPriority.urgent,
                        due_date=date.today() + timedelta(days=2),
                    ),
                    Task(
                        project_id=api_project.id,
                        title="Backfill integration tests",
                        details="Cover project creation and task filters.",
                        status=TaskStatus.planned,
                        priority=TaskPriority.high,
                        due_date=date.today() + timedelta(days=5),
                    ),
                    Task(
                        project_id=api_project.id,
                        title="Investigate stale migration warning",
                        details=(
                            "Review the startup logs and confirm Alembic head matches production."
                        ),
                        status=TaskStatus.blocked,
                        priority=TaskPriority.medium,
                        due_date=date.today() - timedelta(days=1),
                    ),
                    Task(
                        project_id=docs_project.id,
                        title="Publish deployment guide",
                        details="Document migration and startup commands for hosting.",
                        status=TaskStatus.planned,
                        priority=TaskPriority.medium,
                        due_date=date.today() + timedelta(days=4),
                    ),
                    Task(
                        project_id=docs_project.id,
                        title="Add API onboarding tutorial",
                        details="Walk new developers through local setup, seed data, and docs.",
                        status=TaskStatus.in_progress,
                        priority=TaskPriority.high,
                        due_date=date.today() + timedelta(days=3),
                    ),
                    Task(
                        project_id=docs_project.id,
                        title="Refresh screenshots for the dashboard",
                        details="Capture updated filtered task states.",
                        status=TaskStatus.done,
                        priority=TaskPriority.low,
                        due_date=date.today() - timedelta(days=3),
                    ),
                    Task(
                        project_id=ops_project.id,
                        title="Create incident triage queue",
                        details="Model the workflow support engineers use during release week.",
                        status=TaskStatus.in_progress,
                        priority=TaskPriority.urgent,
                        due_date=date.today() + timedelta(days=1),
                    ),
                    Task(
                        project_id=ops_project.id,
                        title="Archive completed rollout checklists",
                        details=(
                            "Move finished launch checklists out of the active operations view."
                        ),
                        status=TaskStatus.planned,
                        priority=TaskPriority.medium,
                        due_date=date.today() + timedelta(days=6),
                    ),
                    Task(
                        project_id=ops_project.id,
                        title="Review failed webhook retries",
                        details=(
                            "Validate that downstream notifications were replayed after "
                            "yesterday's outage."
                        ),
                        status=TaskStatus.blocked,
                        priority=TaskPriority.high,
                        due_date=date.today() - timedelta(days=2),
                    ),
                ]
            )

            session.commit()
            print("Loaded sample data for 3 projects.")
            print(
                "Created local demo users: admin@example.com and viewer@example.com."
            )
            print("Both demo users use the password: password123")
    except ProgrammingError as exc:
        raise SystemExit(
            "Database tables are missing. Run `uv run alembic upgrade head` first."
        ) from exc
    except OperationalError as exc:
        raise SystemExit(
            "Could not connect to the database. Is the Postgres container running?"
        ) from exc


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Load sample data for Release Tracker."
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing project, task, and user records before loading fresh sample data.",
    )
    arguments = parser.parse_args()
    seed(reset=arguments.reset)
