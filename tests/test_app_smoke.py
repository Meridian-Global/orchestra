import orchestra.backend.api.integrations_routes as integrations_routes
import orchestra.backend.api.routes as core_routes
from fastapi.testclient import TestClient

from orchestra.backend.main import app


def test_app_starts():
    client = TestClient(app)

    response = client.get("/docs")

    assert response.status_code == 200


def test_core_route_exists(monkeypatch):
    def fake_run_pipeline_stream(idea: str, voice_profile: str = "default"):
        assert idea == "hello"
        assert voice_profile == "default"
        yield {"event": "planner_started", "data": {}}

    monkeypatch.setattr(core_routes, "run_pipeline_stream", fake_run_pipeline_stream)

    client = TestClient(app)
    response = client.post("/api/run", json={"idea": "hello"})

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]


def test_linkedin_publish_route_exists(monkeypatch):
    def fake_publish_to_linkedin(content: str, access_token: str, person_urn: str):
        assert content == "test post"
        assert access_token == "token"
        assert person_urn == "urn:li:person:test"
        return {"success": True, "post_id": "abc123", "error": None}

    monkeypatch.setattr(integrations_routes, "publish_to_linkedin", fake_publish_to_linkedin)

    client = TestClient(app)
    response = client.post(
        "/api/publish/linkedin",
        json={
            "content": "test post",
            "access_token": "token",
            "person_urn": "urn:li:person:test",
        },
    )

    assert response.status_code not in {404, 405}
    assert response.status_code == 200
    assert response.json() == {"post_id": "abc123", "error": None}


def test_gmail_scan_route_exists(monkeypatch):
    def fake_scan_inbox(max_results: int = 20):
        assert max_results == 20
        return [{"id": "1", "subject": "Hello", "snippet": "World"}]

    monkeypatch.setattr(integrations_routes, "scan_inbox", fake_scan_inbox)

    client = TestClient(app)
    response = client.get("/api/ideas/scan")

    assert response.status_code not in {404, 405}
    assert response.status_code == 200
    assert response.json() == [{"id": "1", "subject": "Hello", "snippet": "World"}]


def test_openapi_contains_expected_routes():
    client = TestClient(app)

    response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/api/run" in paths
    assert "/api/publish/linkedin" in paths
    assert "/api/ideas/scan" in paths
