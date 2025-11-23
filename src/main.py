from fastapi import FastAPI
from src.external_api.router import router as external_router

app = FastAPI(
    title="Books API Integration",
    description="FastAPI application with Google Books API integration",
    version="1.0.0"
)

app.include_router(external_router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Books API Integration",
        "endpoints": {
            "raw_data": "/external/data",
            "processed_data": "/external/processed", 
            "html_view": "/external/books/html"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "books-api"}