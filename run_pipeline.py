# run_pipeline.py
from src.scraper import fetch_raw_data
from src.transform import clean_and_structure
from src.db import upsert_records

def main():
    print("Fetching raw data...")
    raw = fetch_raw_data()
    print(f"Scraped {len(raw)} items.")
    
    print("Transforming and deduplicating...")
    clean_df = clean_and_structure(raw)
    
    print("Upserting into Supabase...")
    upsert_records(clean_df)
    print("Pipeline run completed successfully.")

if __name__ == "__main__":
    main()