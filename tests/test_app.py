import os
os.environ["DEMO_MODE"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///./test_fitbuddy.db"
os.environ["ADMIN_KEY"] = "test-key"

from fastapi.testclient import TestClient

from app.main import app
from app.database import init_db

init_db()
client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "FitBuddy" in response.text


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_generate_workout():
    response = client.post(
        "/generate-workout",
        data={
            "username": "Test User",
            "user_id": "TEST001",
            "age": "20",
            "weight": "60",
            "goal": "general wellness",
            "intensity": "low",
        },
    )
    assert response.status_code == 200
    assert "7-Day" in response.text
    assert "nutrition" in response.text.lower()


def test_feedback():
    response = client.post(
        "/submit-feedback",
        data={
            "user_id": "TEST001",
            "feedback": "Add more mobility and keep the sessions comfortable.",
        },
    )
    assert response.status_code == 200
    assert "Updated Plan" in response.text


def test_admin_requires_key():
    response = client.get("/view-all-users")
    assert response.status_code == 403


def test_admin_with_key():
    response = client.get("/view-all-users?key=test-key")
    assert response.status_code == 200
    assert "Test User" in response.text
