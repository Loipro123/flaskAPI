import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert b"healthy" in response.data


def test_api_endpoint(client):
    """Test main API endpoint"""
    response = client.get("/api")
    assert response.status_code == 200
