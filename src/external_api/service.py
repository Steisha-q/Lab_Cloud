import requests
import asyncio
from typing import List, Optional
from .models import GoogleBooksResponse, ProcessedBook, ProcessedBooksResponse
import os

print("🔄 Loading GoogleBooksService...")

# Спершу спробуємо імпортувати модулі кешу
try:
    from core.cache import cache_get, cache_set
    CACHE_AVAILABLE = True
    print("✅ Redis cache modules imported successfully")
except ImportError as e:
    print(f"❌ Cannot import cache modules: {e}")
    CACHE_AVAILABLE = False
except Exception as e:
    print(f"❌ Cache setup error: {e}")
    CACHE_AVAILABLE = False

print(f"🎯 Final cache status: {CACHE_AVAILABLE}")

class GoogleBooksService:
    """Service for interacting with Google Books API"""
    
    base_url: str = "https://www.googleapis.com/books/v1/volumes"
    
    async def search_books(self, query: str = "python programming", max_results: int = 10) -> GoogleBooksResponse:
        """
        Search books using Google Books API
        """
        print(f"🔍 Searching books: '{query}', max_results: {max_results}, cache: {CACHE_AVAILABLE}")
        
        # Ключ для кешу
        cache_key = f"books:raw:{query}:{max_results}"
        
        # Перевіряємо кеш
        if CACHE_AVAILABLE:
            try:
                cached = await cache_get(cache_key)
                if cached:
                    print("📚 Returning cached raw books data")
                    return GoogleBooksResponse(**cached)
                else:
                    print("💡 No cache found, fetching from API")
            except Exception as e:
                print(f"⚠️ Cache get error: {e}")
        
        params = {
            "q": query,
            "maxResults": max_results,
            "printType": "books"
        }
        
        response = requests.get(self.base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Зберігаємо в кеш
        if CACHE_AVAILABLE:
            try:
                await cache_set(cache_key, data, 60)
                print("💾 Cached raw books data")
            except Exception as e:
                print(f"⚠️ Cache set error: {e}")
        
        return GoogleBooksResponse(**data)
    
    async def process_books_data(self, query: str = "python programming", max_results: int = 10) -> ProcessedBooksResponse:
        """
        Process and transform books data
        """
        # Ключ для кешу оброблених даних
        cache_key = f"books:processed:{query}:{max_results}"
        
        # Перевіряємо кеш
        if CACHE_AVAILABLE:
            try:
                cached = await cache_get(cache_key)
                if cached:
                    print("📚 Returning cached processed books data")
                    return ProcessedBooksResponse(**cached)
            except Exception as e:
                print(f"⚠️ Cache get error: {e}")
        
        raw_data = await self.search_books(query, max_results)
        
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
        
        result = ProcessedBooksResponse(
            total_books=len(processed_books),
            books=processed_books
        )
        
        # Зберігаємо оброблені дані в кеш
        if CACHE_AVAILABLE:
            try:
                await cache_set(cache_key, result.dict(), 60)
                print("💾 Cached processed books data")
            except Exception as e:
                print(f"⚠️ Cache set error: {e}")
        
        return result

books_service = GoogleBooksService()