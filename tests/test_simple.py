def test_healthcheck(client):
    """Простий тест healthcheck ендпоінту"""
    response = client.get("/common/healthcheck")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root_endpoint(client):
    """Тест головної сторінки"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "endpoints" in data


def test_time_endpoint(client):
    """Тест ендпоінту часу"""
    response = client.get("/common/time")
    assert response.status_code == 200
    data = response.json()
    assert "server_time" in data
