import datetime
import logging
import os

from fastapi import APIRouter

router = APIRouter(prefix="/common", tags=["common"])


@router.get("/healthcheck")
def healthcheck():
    return {"status": "ok", "message": "Service is running"}


@router.get("/time")
def get_time():
    return {"server_time": datetime.datetime.now().isoformat()}


@router.get("/sentry-debug")
async def trigger_error():
    """
    Trigger an error to test Sentry integration
    This will cause a division by zero error that should be captured by Sentry
    """
    # This will cause a division by zero error
    division_by_zero = 1 / 0
    return {"division_by_zero": division_by_zero}


@router.get("/environment")
def get_environment():
    """
    Get information about environment variables (without sensitive data)
    """
    # Безпечні змінні середовища для показу
    safe_env_vars = {
        "PYTHON_VERSION": os.getenv("PYTHON_VERSION"),
        "ENVIRONMENT": os.getenv("ENVIRONMENT", "development"),
        "DATABASE_URL": "***" if os.getenv("DATABASE_URL") else None,
        "REDIS_URL": "***" if os.getenv("REDIS_URL") else None,
        "SENTRY_DSN": "***" if os.getenv("SENTRY_DSN") else None,
        "REDIS_TTL": os.getenv("REDIS_TTL"),
    }

    return {
        "environment": safe_env_vars,
        "sentry_enabled": bool(os.getenv("SENTRY_DSN")),
        "redis_enabled": bool(os.getenv("REDIS_URL")),
    }


@router.get("/log-test")
async def log_test():
    """
    Test logging at different levels
    """
    # Using Python standard logging
    logging.debug("This is a DEBUG message - detailed information for debugging")
    logging.info("This is an INFO message - general information")
    logging.warning("This is a WARNING message - something unexpected happened")
    logging.error("This is an ERROR message - serious problem occurred")

    # Also test with print for console output
    print("🖨️ This is a print statement - visible in console")

    return {
        "message": "Log test completed",
        "levels_tested": ["DEBUG", "INFO", "WARNING", "ERROR", "PRINT"],
        "timestamp": datetime.datetime.now().isoformat(),
    }


@router.get("/memory")
def memory_info():
    """
    Get basic memory usage information
    """
    import os

    import psutil

    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()

    return {
        "memory_usage_mb": round(memory_info.rss / 1024 / 1024, 2),
        "memory_percent": round(process.memory_percent(), 2),
        "cpu_percent": round(process.cpu_percent(), 2),
    }


@router.get("/services-status")
def services_status():
    """
    Check status of all integrated services
    """
    services = {
        "postgresql": "enabled",  # Always enabled in your app
        "redis": "enabled" if os.getenv("REDIS_URL") else "disabled",
        "sentry": "enabled" if os.getenv("SENTRY_DSN") else "disabled",
        "google_books_api": "enabled",  # Always enabled if module exists
    }

    return {"services": services, "timestamp": datetime.datetime.now().isoformat(), "status": "operational"}


@router.get("/error-test/{error_type}")
def error_test(error_type: str):
    """
    Test different types of errors for Sentry
    """
    error_type = error_type.lower()

    if error_type == "zero_division":
        result = 1 / 0
    elif error_type == "index_error":
        arr = []
        result = arr[10]
    elif error_type == "key_error":
        dct = {}
        result = dct["nonexistent_key"]
    elif error_type == "type_error":
        result = "string" + 123
    elif error_type == "value_error":
        result = int("not_a_number")
    elif error_type == "attribute_error":
        result = None.attribute
    else:
        return {
            "error": "unknown_error_type",
            "message": f"Unknown error type: {error_type}",
            "available_types": [
                "zero_division",
                "index_error",
                "key_error",
                "type_error",
                "value_error",
                "attribute_error",
            ],
        }

    return {"error_type": error_type, "result": result}
