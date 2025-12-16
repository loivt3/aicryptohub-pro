"""Test script to check database schema"""
from app.services.database import get_db_service
from sqlalchemy import text

db = get_db_service()

# Check columns in aihub_coins table
with db.engine.connect() as conn:
    # Get columns
    result = conn.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'aihub_coins'
        ORDER BY ordinal_position
    """))
    columns = [row[0] for row in result.fetchall()]
    print("=== COLUMNS ===")
    for col in columns:
        print(f"  - {col}")
    print(f"\nTotal: {len(columns)} columns")

