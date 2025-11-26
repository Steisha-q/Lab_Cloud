import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL not found in environment variables")

print(f"🔗 Connecting to: {DATABASE_URL.split('@')[-1]}")

try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        echo=True,
        connect_args={
            "connect_timeout": 10,
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5
        },
        pool_recycle=300
    )
    
    with engine.connect() as conn:
        print("✅ Database connection successful!")
        
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()