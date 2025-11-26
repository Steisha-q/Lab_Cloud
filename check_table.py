import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def check_table_structure():
    print("🔍 Checking books table structure...")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Отримуємо структуру таблиці books
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'books' 
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print("📊 Current books table structure:")
        for col in columns:
            print(f"  - {col[0]} ({col[1]}, nullable: {col[2]})")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_table_structure()