import requests
import streamlit as st
from typing import List, Dict, Optional

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_news(query: str, api_key: str, max_results: int = 10) -> List[Dict]:
    """
    Fetch news articles from NewsData.io API
    
    Args:
        query: Search query or topic
        api_key: NewsData.io API key
        max_results: Maximum number of articles to fetch
    
    Returns:
        List of article dictionaries with title, description, and url
    """
    
    # NewsData.io API endpoint
    base_url = "https://newsdata.io/api/1/news"
    
    # Prepare parameters
    params = {
        "apikey": api_key,
        "q": query,
        "language": "en",
        "size": max_results
    }
    
    try:
        # Make API request
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        
        # Parse response
        data = response.json()
        
        if data.get("status") != "success":
            st.error(f"API Error: {data.get('results', {}).get('message', 'Unknown error')}")
            return []
        
        # Extract articles
        articles = []
        for item in data.get("results", []):
            # Only include articles with sufficient content
            if item.get("title") and (item.get("description") or item.get("content")):
                article = {
                    "title": item.get("title", "Untitled"),
                    "description": item.get("description") or item.get("content", "")[:300],
                    "url": item.get("link", "#"),
                    "source": item.get("source_id", "Unknown"),
                    "published_at": item.get("pubDate", "")
                }
                articles.append(article)
        
        return articles
    
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. Please try again.")
        return []
    
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Network error: {str(e)}")
        return []
    
    except Exception as e:
        st.error(f"❌ Unexpected error fetching news: {str(e)}")
        return []


def fetch_news_fallback_newsapi(query: str, api_key: str, max_results: int = 10) -> List[Dict]:
    """
    Fallback function to fetch news from NewsAPI.org
    
    Args:
        query: Search query or topic
        api_key: NewsAPI.org API key
        max_results: Maximum number of articles to fetch
    
    Returns:
        List of article dictionaries with title, description, and url
    """
    
    # NewsAPI.org endpoint
    base_url = "https://newsapi.org/v2/everything"
    
    # Prepare parameters
    params = {
        "apiKey": api_key,
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": max_results
    }
    
    try:
        # Make API request
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        
        # Parse response
        data = response.json()
        
        if data.get("status") != "ok":
            st.error(f"API Error: {data.get('message', 'Unknown error')}")
            return []
        
        # Extract articles
        articles = []
        for item in data.get("articles", []):
            # Only include articles with sufficient content
            if item.get("title") and item.get("description"):
                article = {
                    "title": item.get("title", "Untitled"),
                    "description": item.get("description", ""),
                    "url": item.get("url", "#"),
                    "source": item.get("source", {}).get("name", "Unknown"),
                    "published_at": item.get("publishedAt", "")
                }
                articles.append(article)
        
        return articles
    
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. Please try again.")
        return []
    
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Network error: {str(e)}")
        return []
    
    except Exception as e:
        st.error(f"❌ Unexpected error fetching news: {str(e)}")
        return []
