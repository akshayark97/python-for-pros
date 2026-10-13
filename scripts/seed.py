from sqlmodel import Session

from release_tracker.database import get_engine
from release_tracker.models import Project


def seed() -> None:
    # 1. Create a Session using the engine
    with Session(get_engine()) as session:
        # 2. Instantiate three Project objects
        frontend = Project(name="Frontend Redesign", slug="frontend-redesign")
        # TODO: Create two more projects
        frontend1 = Project(name="Frontend Redesign 2", slug="frontend-redesign-2")
        # 3. Add them to the session
        frontend2 = Project(name="Frontend Redesign 3", slug="frontend-redesign-3")
        session.add(frontend)
        # TODO: Add the other two projects
        session.add(frontend1)
        session.add(frontend2)
        # 4. Commit the transaction to save them to the database
        session.commit()

        print("Loaded sample data for 3 projects.")


if __name__ == "__main__":
    seed()