import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json
import re

# Load environment variables
load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

def fetch_latest_news(query="forex OR \"exchange rate\"", page_size=10):
    if not NEWS_API_KEY:
        print("NEWS_API_KEY not found in .env")
        return []
    
    # Fetch news from the last 48 hours for maximum freshness
    from_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "sortBy": "publishedAt",
        "pageSize": page_size,
        "apiKey": NEWS_API_KEY,
        "language": "en",
        "from": from_date
    }

    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        articles = response.json().get("articles", [])
        
        # If no articles in last 48h, try without date restriction
        if not articles:
            print("No news in last 48h, trying without date filter...")
            params.pop("from", None)
            response = requests.get(url, params=params)
            response.raise_for_status()
            articles = response.json().get("articles", [])
            
        return articles
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []


def analyze_news_with_gemini(articles):
    if not articles:
        return []
    
    if not GEMINI_API_KEY:
        for art in articles:
            art["summary"] = art.get("description", "")
            art["sentiment"] = "Neutral"
            art["currency"] = "Global"
        return articles

    news_items = []
    for i, art in enumerate(articles):
        news_items.append(f"ARTICLE {i+1}: {art['title']}\nDESC: {art.get('description', 'N/A')}")
    
    prompt = f"""
    Analyze these {len(articles)} forex news items. 
    Return a JSON list of objects, one for each article, with:
    - "summary": Max 15 word summary.
    - "sentiment": "Positive", "Negative", or "Neutral".
    - "currency": Standard 3-letter currency code (USD, EUR, INR, JPY, GBP) or "Global" if it affects multiple or the whole market.

    Articles:
    {chr(10).join(news_items)}

    Important: 
    1. The JSON must have exactly {len(articles)} items in order.
    2. Return ONLY a valid JSON array. No markdown, no pre-amble.
    """



    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean markdown if present
        text = re.sub(r'```json\s*|\s*```', '', text)
        
        analysis = json.loads(text)
        
        for i, art in enumerate(articles):
            if i < len(analysis):
                res = analysis[i]
                art["summary"] = res.get("summary", art.get("description", ""))
                art["sentiment"] = res.get("sentiment", "Neutral")
                art["currency"] = res.get("currency", "Global")
            else:
                art["summary"] = art.get("description", "")
                art["sentiment"] = "Neutral"
                art["currency"] = "Global"
        
        return articles
    except Exception as e:
        print(f"Gemini error: {e}")
        for art in articles:
            art["summary"] = art.get("description", "")
            art["sentiment"] = "Neutral"
            art["currency"] = "Global"
        return articles

def get_processed_news(query="forex OR \"exchange rate\"", page_size=5, currencies=None):
    """
    Fetches and processes news. If currencies are provided, it tries to fetch news 
    specifically for those to ensure coverage.
    """
    if not currencies or "Global" in currencies:
        articles = fetch_latest_news(query, page_size)
    else:
        # Fetch a mix of general forex news and specific currency news
        combined_query = f"({query}) AND ({' OR '.join(currencies)})"
        articles = fetch_latest_news(combined_query, page_size)
        
        # If still very few articles, fallback to general search but prioritize the specific ones
        if len(articles) < 5:
            general = fetch_latest_news(query, page_size)
            articles.extend(general)
            # Remove duplicates by URL
            seen = set()
            articles = [x for x in articles if not (x['url'] in seen or seen.add(x['url']))]
            articles = articles[:page_size]

    return analyze_news_with_gemini(articles)


if __name__ == "__main__":
    res = get_processed_news(page_size=3)
    print(json.dumps(res, indent=2))
