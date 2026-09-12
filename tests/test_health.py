from fastapi.testclient import TestClient

from backend.main import app


def test_health_is_explicitly_non_clinical():
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json()["clinical_use"] is False

