import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fetch_raw_data() -> list[dict]:
    url = "https://quotes.toscrape.com/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    records = []
    
    for item in soup.select(".quote"):
        quote_text = item.select_one(".text").get_text(strip=True)
        author = item.select_one(".author").get_text(strip=True)
        tags = [t.get_text(strip=True) for t in item.select(".tag")]
        
        records.append({
            "quote": quote_text,
            "author": author,
            "tags": tags,
            "scraped_at": datetime.utcnow().isoformat()
        })
        
    return records