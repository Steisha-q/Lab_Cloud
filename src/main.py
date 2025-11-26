import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from books.database import engine, get_db
from books.routes import router
from core.logging.logging_config import setup_logging
from core.logging.sentry import init_sentry
from core.router import router as core_router

try:
    from external_api.models import ProcessedBooksResponse
    from external_api.service import CACHE_AVAILABLE, books_service

    EXTERNAL_API_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ External API modules not available: {e}")
    EXTERNAL_API_AVAILABLE = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    print("Starting Bookstore API...")

    setup_logging()

    init_sentry()

    try:
        from sqlalchemy import inspect

        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"📋 Available tables: {tables}")

        if "books" in tables:
            print("Books table exists and ready to use!")
        else:
            print(" Books table not found, but other tables exist")

    except Exception as e:
        print(f" Database inspection failed: {e}")

    print(" Connected to Render.com PostgreSQL")
    print(" Database: hpk_db_nyor")

    if EXTERNAL_API_AVAILABLE:
        print(" External APIs: Google Books API")
        if CACHE_AVAILABLE:
            print(" Cache: Redis enabled")
        else:
            print(" Cache: Redis disabled")
    else:
        print(" External APIs: Google Books API not available")

    if os.getenv("SENTRY_DSN"):
        print(" Monitoring: Sentry enabled")
    else:
        print(" Monitoring: Sentry disabled")

    yield

    print(" Shutting down Bookstore API...")


app = FastAPI(
    title="Bookstore API",
    description="API для управління книгами з PostgreSQL на Render.com"
    + (" та інтеграцією з Google Books API" if EXTERNAL_API_AVAILABLE else ""),
    version="1.0.0",
    lifespan=lifespan,  # Додайте lifespan тут
)

# Підключаємо всі роути
app.include_router(router)
app.include_router(core_router)  # Додайте цей рядок


@app.get("/")
async def root():
    endpoints = {
        "docs": "/docs",
        "health": "/health",
        "database_info": "/db-info",
        "common_health": "/common/healthcheck",  # Додайте нові ендпоінти
        "common_time": "/common/time",
        "common_environment": "/common/environment",
        "common_services": "/common/services-status",
        "sentry_test": "/common/sentry-debug",  # Тестовий ендпоінт для Sentry
        "log_test": "/common/log-test",
    }

    if EXTERNAL_API_AVAILABLE:
        endpoints.update(
            {
                "search_books": "/api/external/books",
                "search_books_raw": "/api/external/books/raw",
                "external_health": "/api/external/health",
                "cache_test": "/api/external/cache-test",
            }
        )

    return {
        "message": "Bookstore API з PostgreSQL на Render.com"
        + (" та Google Books API" if EXTERNAL_API_AVAILABLE else ""),
        "database": "hpk_db_nyor",
        "cache": "Redis enabled" if EXTERNAL_API_AVAILABLE and CACHE_AVAILABLE else "Redis disabled",
        "monitoring": "Sentry enabled" if os.getenv("SENTRY_DSN") else "Sentry disabled",
        "external_apis": "Google Books API" if EXTERNAL_API_AVAILABLE else "Not available",
        "endpoints": endpoints,
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")

        from books.models import Book

        book_count = db.query(Book).count()

        health_info = {
            "status": "healthy",
            "database": "PostgreSQL connected",
            "service": "Render.com",
            "database_name": "hpk_db_nyor",
            "total_books": book_count,
            "tables": ["books", "alembic_version"],
            "monitoring": "Sentry enabled" if os.getenv("SENTRY_DSN") else "Sentry disabled",  # Додайте моніторинг
        }

        if EXTERNAL_API_AVAILABLE:
            health_info["external_apis"] = {
                "google_books": "available",
                "cache": "enabled" if CACHE_AVAILABLE else "disabled",
            }
        else:
            health_info["external_apis"] = {"google_books": "not configured"}

        return health_info
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")


# Видаліть старий startup_event, оскільки ми використовуємо lifespan


@app.get("/db-info")
def database_info(db: Session = Depends(get_db)):
    """Детальна інформація про базу даних"""
    try:
        result = db.execute(
            """
            SELECT
                current_database(),
                current_user,
                version()
        """
        )
        db_info = result.fetchone()

        result = db.execute(
            """
            SELECT
                table_name,
                table_type
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """
        )
        tables = result.fetchall()

        return {
            "database_name": db_info[0],
            "current_user": db_info[1],
            "postgres_version": db_info[2],
            "tables": [{"name": table[0], "type": table[1]} for table in tables],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if EXTERNAL_API_AVAILABLE:

    @app.get("/api/external/books", response_model=ProcessedBooksResponse)
    async def search_books(query: str = "python programming", max_results: int = 10):
        """
        Пошук книг через Google Books API з кешуванням
        """
        try:
            result = await books_service.process_books_data(query=query, max_results=max_results)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Помилка при пошуку книг: {str(e)}")

    @app.get("/api/external/books/raw")
    async def search_books_raw(query: str = "python programming", max_results: int = 10):
        """
        Сирий пошук книг через Google Books API (без обробки)
        """
        try:
            result = await books_service.search_books(query=query, max_results=max_results)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Помилка при пошуку книг: {str(e)}")

    @app.get("/api/external/health")
    async def external_apis_health():
        """
        Перевірка стану зовнішніх API
        """
        try:
            _ = await books_service.search_books(query="test", max_results=1)

            return {
                "status": "healthy",
                "external_apis": {"google_books": {"status": "available", "test_query": "successful"}},
                "cache": {
                    "redis": "enabled" if CACHE_AVAILABLE else "disabled",
                    "ttl": "60 seconds" if CACHE_AVAILABLE else "N/A",
                },
            }
        except Exception as e:
            return {
                "status": "degraded",
                "external_apis": {"google_books": {"status": "unavailable", "error": str(e)}},
                "cache": {
                    "redis": "enabled" if CACHE_AVAILABLE else "disabled",
                    "ttl": "60 seconds" if CACHE_AVAILABLE else "N/A",
                },
            }

    @app.get("/api/external/cache-test")
    async def cache_test():
        """Тест кешування"""
        import time

        start_time = time.time()
        result1 = await books_service.process_books_data(query="cache test", max_results=3)
        time1 = round((time.time() - start_time) * 1000, 2)

        start_time = time.time()
        time2 = round((time.time() - start_time) * 1000, 2)

        return {
            "cache_status": "enabled" if CACHE_AVAILABLE else "disabled",
            "first_request_ms": time1,
            "second_request_ms": time2,
            "speed_improvement": f"{round((time1 - time2) / time1 * 100, 1)}%" if time1 > time2 else "no improvement",
            "books_count": len(result1.books),
            "message": "Якщо кеш працює, другий запит має бути значно швидшим",
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
