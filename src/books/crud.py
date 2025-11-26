from sqlalchemy.orm import Session
from sqlalchemy import or_
from . import models
from . import schemas
from typing import List, Optional

def get_book(db: Session, book_id: int) -> Optional[models.Book]:
    return db.query(models.Book).filter(models.Book.id == book_id).first()

def get_books(db: Session, skip: int = 0, limit: int = 100) -> List[models.Book]:
    return db.query(models.Book).offset(skip).limit(limit).all()

def get_books_by_author(db: Session, author: str) -> List[models.Book]:
    return db.query(models.Book).filter(models.Book.author.ilike(f"%{author}%")).all()

def get_book_by_isbn(db: Session, isbn: str) -> Optional[models.Book]:
    return db.query(models.Book).filter(models.Book.isbn == isbn).first()

def create_book(db: Session, book: schemas.BookCreate) -> models.Book:
    # Перевіряємо, чи книга з таким ISBN вже існує
    existing_book = get_book_by_isbn(db, book.isbn)
    if existing_book:
        raise ValueError(f"Book with ISBN {book.isbn} already exists")
    
    # Створюємо книгу без зайвих полів
    db_book = models.Book(
        title=book.title,
        author=book.author,
        year=book.year,
        isbn=book.isbn
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def update_book(db: Session, book_id: int, book_update: schemas.BookUpdate) -> Optional[models.Book]:
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        return None
    
    update_data = book_update.model_dump(exclude_unset=True)
    
    # Перевіряємо унікальність ISBN при оновленні
    if 'isbn' in update_data and update_data['isbn'] != db_book.isbn:
        existing_book = get_book_by_isbn(db, update_data['isbn'])
        if existing_book:
            raise ValueError(f"Book with ISBN {update_data['isbn']} already exists")
    
    # Оновлюємо тільки ті поля, які є в моделі
    for field, value in update_data.items():
        if hasattr(db_book, field):
            setattr(db_book, field, value)
    
    db.commit()
    db.refresh(db_book)
    return db_book

def delete_book(db: Session, book_id: int) -> bool:
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        return False
    
    db.delete(db_book)
    db.commit()
    return True

def search_books(db: Session, query: str) -> List[models.Book]:
    return db.query(models.Book).filter(
        or_(
            models.Book.title.ilike(f"%{query}%"),
            models.Book.author.ilike(f"%{query}%")
        )
    ).all()