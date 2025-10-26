"""Test health check endpoint"""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test health check endpoint returns 200 or 503 (degraded)"""
    response = client.get("/health")
    # May return 503 if Firestore is not configured (acceptable in test environment)
    assert response.status_code in [200, 503]
    data = response.json()
    assert data["status"] in ["ok", "degraded"]
    assert "version" in data
    assert "environment" in data
    assert "checks" in data


def test_root_endpoint(client: TestClient):
    """Test root endpoint returns application info"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["message"] == "AreaYield OS API"
