import os
from sqlalchemy import create_engine, text
import pandas as pd

def get_engine():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set.")
    # Supabase URIs starting with postgres:// should be postgresql:// for SQLAlchemy
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    return create_engine(db_url)

def init_db():
    """Ensures the schema exists with a unique constraint on 'id'."""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS market_data (
        id VARCHAR(64) PRIMARY KEY,
        quote TEXT NOT NULL,
        author VARCHAR(255) NOT NULL,
        tags TEXT,
        scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    with get_engine().begin() as conn:
        conn.execute(text(create_table_query))

def upsert_records(df: pd.DataFrame):
    """Inserts records while skipping already existing IDs."""
    if df.empty:
        return
    
    init_db()
    engine = get_engine()
    
    # Write to a temporary staging table then insert non-existing
    with engine.begin() as conn:
        df.to_sql("temp_stage", conn, if_exists="replace", index=False)
        upsert_query = """
        INSERT INTO market_data (id, quote, author, tags, scraped_at)
        SELECT id, quote, author, tags, scraped_at FROM temp_stage
        ON CONFLICT (id) DO NOTHING;
        DROP TABLE IF EXISTS temp_stage;
        """
        conn.execute(text(upsert_query))