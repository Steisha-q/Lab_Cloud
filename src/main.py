from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

# Додайте src до шляху пошуку модулів
import sys
import os

# Додаємо теку src до Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Тепер імпортуємо з books
from books.database import get_db, engine
from books.models import Base
from books.routes import router

app = FastAPI(
    title="Bookstore API",
    description="API для управління книгами з PostgreSQL на Render.com",
    version="1.0.0"
)

# Підключаємо роути
app.include_router(router)

@app.get("/")
async def root():
    return {
        "message": "Bookstore API з PostgreSQL на Render.com",
        "database": "hpk_db_nyor",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Перевіряємо підключення до бази
        db.execute("SELECT 1")
        
        # Перевіряємо кількість книг у базі
        from books.models import Book
        book_count = db.query(Book).count()
        
        return {
            "status": "healthy",
            "database": "PostgreSQL connected",
            "service": "Render.com",
            "database_name": "hpk_db_nyor",
            "total_books": book_count,
            "tables": ["books", "alembic_version"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database unavailable: {str(e)}"
        )

@app.on_event("startup")
async def startup_event():
    """Перевіряємо стан бази при запуску"""
    try:
        print("🚀 Starting Bookstore API...")
        print("📊 Connected to Render.com PostgreSQL")
        print("🗃️ Database: hpk_db_nyor")
        
        # Перевіряємо чи таблиця books існує
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"📋 Available tables: {tables}")
        
        if 'books' in tables:
            print("✅ Books table exists and ready to use!")
        else:
            print("⚠️ Books table not found, but other tables exist")
            
    except Exception as e:
        print(f"❌ Startup error: {e}")

@app.get("/db-info")
def database_info(db: Session = Depends(get_db)):
    """Детальна інформація про базу даних"""
    try:
        # Інформація про базу
        result = db.execute("""
            SELECT 
                current_database(),
                current_user,
                version()
        """)
        db_info = result.fetchone()
        
        # Інформація про таблиці
        result = db.execute("""
            SELECT 
                table_name,
                table_type
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = result.fetchall()
        
        return {
            "database_name": db_info[0],
            "current_user": db_info[1],
            "postgres_version": db_info[2],
            "tables": [{"name": table[0], "type": table[1]} for table in tables]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)