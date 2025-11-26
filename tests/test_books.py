def test_root_endpoint(client):
    """Тест головної сторінки"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "endpoints" in data
