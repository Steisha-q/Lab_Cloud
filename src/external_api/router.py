import random

from fastapi import APIRouter, HTTPException, Query

from src.external_api.models import GoogleBooksResponse, ProcessedBooksResponse
from src.external_api.service import books_service

router = APIRouter(prefix="/external", tags=["External Books API"])


@router.get("/data", response_model=GoogleBooksResponse)
def get_raw_books_data(
    query: str = Query("python programming", description="Search query for books"),
    max_results: int = Query(5, ge=1, le=20, description="Number of results (1-20)"),
) -> GoogleBooksResponse:
    """
    Get raw data from Google Books API
    """
    try:
        return books_service.search_books(query, max_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching books data: {str(e)}")


@router.get("/processed", response_model=ProcessedBooksResponse)
def get_processed_books_data(
    query: str = Query("python programming", description="Search query for books"),
    max_results: int = Query(5, ge=1, le=20, description="Number of results (1-20)"),
) -> ProcessedBooksResponse:
    """
    Get processed and transformed books data
    """
    try:
        return books_service.process_books_data(query, max_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing books data: {str(e)}")


@router.get("/books/random")
def get_random_book():
    """
    Get a random book from popular programming topics.
    """
    try:
        topics = ["python", "javascript", "java", "programming", "computer science"]
        topic = random.choice(topics)

        result = books_service.process_books_data(topic, max_results=5)
        if result.books:
            random_book = random.choice(result.books)
            return {
                "random_topic": topic,
                "book": {
                    "title": random_book.title,
                    "authors": random_book.authors,
                    "year": random_book.published_year,
                    "preview_link": random_book.preview_link,
                },
            }
        return {"message": "No books found"}

    except Exception as e:
        return {"error": str(e)}
