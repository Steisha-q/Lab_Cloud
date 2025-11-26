def test_healthcheck(client):
    response = client.get("/common/healthcheck")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_time(client):
    response = client.get("/common/time")
    assert response.status_code == 200
    assert "server_time" in response.json()


def test_environment(client):
    response = client.get("/common/environment")
    assert response.status_code == 200
    data = response.json()
    assert "environment" in data
    assert "sentry_enabled" in data


def test_services_status(client):
    response = client.get("/common/services-status")
    assert response.status_code == 200
    data = response.json()
    assert "services" in data
    assert "status" in data


def test_healthcheck_wrong_method(client):
    response = client.post("/common/healthcheck")
    assert response.status_code == 405


def test_log_test(client):
    response = client.get("/common/log-test")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "levels_tested" in data
