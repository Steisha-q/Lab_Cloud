from dataclasses import dataclass


@dataclass
class BooksConfig:
    """Configuration limits for Google Books API models."""

    min_title_length: int = 1
    max_title_length: int = 200

    min_author_length: int = 2
    max_author_length: int = 100

    min_description_length: int = 10
    max_description_length: int = 5000

    min_isbn_length: int = 10
    max_isbn_length: int = 13


books_config = BooksConfig()
