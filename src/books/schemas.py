from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class BookBase(BaseModel):
    title: str
    author: str
    year: Optional[int] = None
    isbn: str

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    year: Optional[int] = None
    isbn: Optional[str] = None

class BookResponse(BookBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime