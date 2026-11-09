from fastapi.testclient import TestClient


def test_create_project(auth_client: TestClient):
    response = auth_client.post(
        "/projects/",
        json={
            "name": "New Project",
            "description": "A test project",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Project"
    assert data["slug"] == "new-project"
    assert "id" in data


def test_get_project(auth_client: TestClient, sample_project_id: int):
    response = auth_client.get(f"/projects/{sample_project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Release Platform"
    assert data["id"] == sample_project_id


def test_list_projects(auth_client: TestClient, sample_project_id: int):
    response = auth_client.get("/projects/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["id"] == sample_project_id


def test_update_project(auth_client: TestClient, sample_project_id: int):
    response = auth_client.patch(
        f"/projects/{sample_project_id}",
        json={"name": "Updated Platform Name"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Platform Name"
    assert data["slug"] == "updated-platform-name"


def test_delete_project(auth_client: TestClient, sample_project_id: int):
    response = auth_client.delete(f"/projects/{sample_project_id}")
    assert response.status_code == 204

    response = auth_client.get(f"/projects/{sample_project_id}")
    assert response.status_code == 404


def test_create_duplicate_project_fails(
    auth_client: TestClient, sample_project_id: int
):
    response = auth_client.post(
        "/projects/",
        json={
            "name": "Release Platform",  # Same name as sample_project_id
            "description": "Another description",
        },
    )
    assert response.status_code == 409
    assert response.json() == {
        "detail": "Data conflict occurred (e.g., duplicate entry)."
    }


def test_create_project_unauthenticated(client: TestClient):
    # No `auth_client` in this test: the bare `client`has no token, so
    # the request is rejected before the route handler runs.
    response = client.post(
        "/projects/",
        json={"name": "Sneaky Project", "description": "no auth here"},
    )
    assert response.status_code == 401
