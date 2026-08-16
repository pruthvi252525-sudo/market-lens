import hashlib
import pandas as pd

def generate_record_id(quote: str, author: str) -> str:
    """Creates a deterministic unique hash for idempotency."""
    raw_str = f"{author.strip().lower()}:{quote.strip().lower()}"
    return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

def clean_and_structure(raw_records: list[dict]) -> pd.DataFrame:
    if not raw_records:
        return pd.DataFrame()
    
    df = pd.DataFrame(raw_records)
    
    # Generate unique ID for database deduplication
    df["id"] = df.apply(lambda r: generate_record_id(r["quote"], r["author"]), axis=1)
    
    # Flatten tags array into comma-separated string
    df["tags"] = df["tags"].apply(lambda tags: ", ".join(tags) if isinstance(tags, list) else "")
    
    # Trim whitespace
    df["quote"] = df["quote"].str.strip()
    df["author"] = df["author"].str.strip()
    df["scraped_at"] = pd.to_datetime(df["scraped_at"])
    
    # Deduplicate within current batch
    return df.drop_duplicates(subset=["id"])