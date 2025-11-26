from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Book(Base):
    __tablename__ = "books"
    
    # Тільки ті колонки, які реально існують в базі даних
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=False, index=True)
    year = Column(Integer)  # Назва 'year' в базі
    isbn = Column(String(20), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}', author='{self.author}')>"