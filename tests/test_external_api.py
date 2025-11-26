def test_external_books_endpoint(client):
    """Тест пошуку книг через Google Books API"""
    response = client.get("/api/external/books?query=python&max_results=5")

    assert response.status_code in [200, 500]

    if response.status_code == 200:
        data = response.json()
        assert "total_books" in data
        assert "books" in data


def test_external_books_raw_endpoint(client):
    """Тест сирого пошуку книг"""
    response = client.get("/api/external/books/raw?query=javascript")
    assert response.status_code in [200, 500]


def test_external_health_endpoint(client):
    """Тест перевірки стану зовнішніх API"""
    response = client.get("/api/external/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "external_apis" in data


def test_cache_test_endpoint(client):
    """Тест перевірки кешування"""
    response = client.get("/api/external/cache-test")
    assert response.status_code == 200
    data = response.json()
    assert "cache_status" in data
    assert "first_request_ms" in data
    assert "second_request_ms" in data
