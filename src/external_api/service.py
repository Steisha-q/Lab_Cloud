import requests
from typing import List, Optional
from src.external_api.models import GoogleBooksResponse, ProcessedBook, ProcessedBooksResponse

class GoogleBooksService:
    """Service for interacting with Google Books API"""
    
    base_url: str = "https://www.googleapis.com/books/v1/volumes"
    
    def search_books(self, query: str = "python programming", max_results: int = 10) -> GoogleBooksResponse:
        """
        Search books using Google Books API
        :param query: Search query
        :param max_results: Maximum number of results
        :return: GoogleBooksResponse with raw data
        """
        params = {
            "q": query,
            "maxResults": max_results,
            "printType": "books"
        }
        
        response = requests.get(self.base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return GoogleBooksResponse(**data)
    
    def process_books_data(self, query: str = "python programming", max_results: int = 10) -> ProcessedBooksResponse:
        """
        Process and transform books data
        :param query: Search query
        :param max_results: Maximum number of results
        :return: ProcessedBooksResponse with transformed data
        """
        raw_data = self.search_books(query, max_results)
        
        processed_books = []
        
        for book in raw_data.items:
            volume_info = book.volumeInfo
            
            # Extract publication year
            published_year = None
            if volume_info.publishedDate:
                try:
                    published_year = int(volume_info.publishedDate[:4])
                except (ValueError, TypeError):
                    published_year = None
            
            thumbnail = None
            if volume_info.imageLinks and volume_info.imageLinks.get('thumbnail'):
                thumbnail = volume_info.imageLinks['thumbnail']
            
            categories = volume_info.categories or []
            
            authors = volume_info.authors or ["Unknown Author"]
            
            processed_book = ProcessedBook(
                id=book.id,
                title=volume_info.title,
                authors=authors,
                published_year=published_year,
                page_count=volume_info.pageCount,
                categories=categories,
                thumbnail=thumbnail,
                preview_link=str(volume_info.previewLink) if volume_info.previewLink else None,
                language=volume_info.language
            )
            processed_books.append(processed_book)
        
        return ProcessedBooksResponse(
            total_books=len(processed_books),
            books=processed_books
        )

books_service = GoogleBooksService()