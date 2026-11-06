from datetime import UTC, date, datetime, timedelta

from sqlmodel import Session

from release_tracker.database import get_engine
from release_tracker.models import Project, Task, TaskPriority, TaskStatus


def seed() -> None:
    today = datetime.now(UTC).date()

    with Session(get_engine()) as session:
        frontend = Project(name="Frontend Redesign", slug="frontend-redesign")
        api = Project(name="API v2", slug="api-v2")
        db_migration = Project(
            name="Database Migration", slug="database-migration"
        )

        session.add_all([frontend, api, db_migration])
        session.commit()
        session.refresh(frontend)
        session.refresh(api)
        session.refresh(db_migration)

        tasks = [
            Task(
                title="Migrate auth flow to new design",
                project_id=frontend.id,
                status=TaskStatus.in_progress,
                priority=TaskPriority.high,
                due_date=today + timedelta(days=7),
            ),
            Task(
                title="Wire up the dashboard",
                project_id=frontend.id,
                status=TaskStatus.planned,
                priority=TaskPriority.medium,
            ),
            Task(
                title="Stabilize the v2 endpoints",
                project_id=api.id,
                status=TaskStatus.blocked,
                priority=TaskPriority.urgent,
                due_date=today - timedelta(days=2),
            ),
            Task(
                title="Backfill task data",
                project_id=db_migration.id,
                status=TaskStatus.done,
                priority=TaskPriority.low,
                due_date=date(2025, 12, 1),
            ),
        ]
        session.add_all(tasks)
        session.commit()

        print(f"Loaded sample data for 3 projects and {len(tasks)} tasks.")


if __name__ == "__main__":
    seed()