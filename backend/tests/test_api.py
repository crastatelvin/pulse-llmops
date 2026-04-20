from fastapi.testclient import TestClient

import main


def test_health_ok():
    client = TestClient(main.app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_api_key_protection():
    client = TestClient(main.app)
    old_key = main.settings.api_key
    try:
        main.settings.api_key = "secret"
        unauthorized = client.get("/metrics/summary")
        assert unauthorized.status_code == 401
        authorized = client.get("/metrics/summary", headers={"x-api-key": "secret"})
        assert authorized.status_code == 200
    finally:
        main.settings.api_key = old_key
