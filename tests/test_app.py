"""Tests for the deployment demo service.

These run in the pipeline's `test` job. If any of them fail, the image is never
built and nothing reaches production — which is the whole point of having them.
"""

import os
import sys

import pytest

# Make src/ importable when pytest runs from the project root.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app import app as flask_app  # noqa: E402


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


def test_index_returns_ok(client):
    response = client.get("/")
    assert response.status_code == 200


def test_index_shows_manifest(client):
    response = client.get("/")
    body = response.get_data(as_text=True)
    assert "Deployment Manifest" in body
    assert "Serving commit" in body


def test_index_lists_all_five_pipeline_stages(client):
    body = client.get("/").get_data(as_text=True)
    for stage in ("Lint", "Test", "Build", "Deploy", "Verify"):
        assert stage in body


def test_health_reports_healthy(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_health_includes_commit_sha(client):
    """The verify job relies on this field to confirm the new build is live."""
    payload = client.get("/health").get_json()
    assert "commit_sha" in payload
    assert payload["commit_sha"]


def test_api_info_returns_expected_fields(client):
    payload = client.get("/api/info").get_json()
    for field in (
        "app_version",
        "commit_sha",
        "image_tag",
        "built_at",
        "environment",
        "container_host",
        "uptime_seconds",
    ):
        assert field in payload


def test_unknown_route_returns_404(client):
    assert client.get("/no-such-page").status_code == 404
