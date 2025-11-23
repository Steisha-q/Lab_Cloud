from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import List, Optional
from src.external_api.config import books_config as cfg

class BookVolumeInfo(BaseModel):
    title: str = Field(
        ...,
        description="Book title",
        min_length=cfg.min_title_length,
        max_length=cfg.max_title_length
    )
    authors: Optional[List[str]] = Field(
        default=None,
        description="List of authors"
    )
    publisher: Optional[str] = Field(
        default=None,
        description="Publisher name"
    )
    publishedDate: Optional[str] = Field(
        default=None,
        description="Publication date"
    )
    description: Optional[str] = Field(
        default=None,
        description="Book description",
        min_length=cfg.min_description_length,
        max_length=cfg.max_description_length
    )
    pageCount: Optional[int] = Field(
        default=None,
        description="Number of pages",
        ge=0 
    )
    categories: Optional[List[str]] = Field(
        default=None,
        description="Book categories"
    )
    imageLinks: Optional[dict] = Field(
        default=None,
        description="Book cover images"
    )
    language: Optional[str] = Field(
        default=None,
        description="Book language"
    )
    previewLink: Optional[HttpUrl] = Field(
        default=None,
        description="Preview link"
    )
    infoLink: Optional[HttpUrl] = Field(
        default=None,
        description="Info link"
    )

class BookItem(BaseModel):
    id: str = Field(..., description="Book ID")
    volumeInfo: BookVolumeInfo = Field(..., description="Volume information")

class GoogleBooksResponse(BaseModel):
    kind: str = Field(..., description="API response kind")
    totalItems: int = Field(..., description="Total items found")
    items: List[BookItem] = Field(..., description="List of books")

class ProcessedBook(BaseModel):
    id: str = Field(..., description="Book ID")
    title: str = Field(..., description="Book title")
    authors: List[str] = Field(..., description="List of authors")
    published_year: Optional[int] = Field(default=None, description="Publication year")
    page_count: Optional[int] = Field(default=None, description="Number of pages", ge=0)
    categories: List[str] = Field(default=[], description="Book categories")
    thumbnail: Optional[str] = Field(default=None, description="Thumbnail URL")
    preview_link: Optional[str] = Field(default=None, description="Preview link")
    language: Optional[str] = Field(default=None, description="Book language")

    model_config: ConfigDict = ConfigDict(from_attributes=True)

class ProcessedBooksResponse(BaseModel):
    total_books: int = Field(..., description="Total books processed")
    books: List[ProcessedBook] = Field(..., description="Processed books list")