from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

# Відносні імпорти всередині папки books
from . import crud, schemas
from .database import get_db

router = APIRouter(prefix="/books", tags=["books"])

@router.post("/", response_model=schemas.BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_book(db=db, book=book)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[schemas.BookResponse])
def read_books(
    skip: int = Query(0, ge=0, description="Skip records"),
    limit: int = Query(100, ge=1, le=1000, description="Limit records"),
    db: Session = Depends(get_db)
):
    books = crud.get_books(db, skip=skip, limit=limit)
    return books

@router.get("/{book_id}", response_model=schemas.BookResponse)
def read_book(book_id: int, db: Session = Depends(get_db)):
    db_book = crud.get_book(db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@router.get("/author/{author}", response_model=List[schemas.BookResponse])
def read_books_by_author(author: str, db: Session = Depends(get_db)):
    books = crud.get_books_by_author(db, author=author)
    return books

@router.get("/isbn/{isbn}", response_model=schemas.BookResponse)
def read_book_by_isbn(isbn: str, db: Session = Depends(get_db)):
    db_book = crud.get_book_by_isbn(db, isbn=isbn)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@router.put("/{book_id}", response_model=schemas.BookResponse)
def update_book(book_id: int, book_update: schemas.BookUpdate, db: Session = Depends(get_db)):
    try:
        db_book = crud.update_book(db, book_id=book_id, book_update=book_update)
        if db_book is None:
            raise HTTPException(status_code=404, detail="Book not found")
        return db_book
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    success = crud.delete_book(db, book_id=book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted successfully"}

@router.get("/search/{query}", response_model=List[schemas.BookResponse])
def search_books(query: str, db: Session = Depends(get_db)):
    books = crud.search_books(db, query=query)
    return books