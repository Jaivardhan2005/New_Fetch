import google.generativeai as genai
import streamlit as st
import re
from typing import Dict, Optional

def analyze_article(article: Dict, api_key: str) -> Optional[Dict]:
    """
    Analyze a news article using Google Gemini API
    
    Args:
        article: Dictionary containing article title and description
        api_key: Google Gemini API key
    
    Returns:
        Dictionary with summary, sentiment, and impact_score
    """
    
    # Configure Gemini API
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
    except Exception as e:
        st.error(f"❌ Failed to configure Gemini API: {str(e)}")
        return None
    
    # Prepare the prompt
    article_text = f"{article['title']}. {article['description']}"
    
    prompt = f"""You are a geopolitical intelligence analyst.

Article: {article_text}

Analyze this article and provide:
1. A summary in exactly 2 sentences
2. The sentiment (choose ONE: positive, negative, tense, or neutral)
3. A strategic impact score from 1-10 based on geopolitical importance

Format your response EXACTLY as follows:
SUMMARY: [your 2-sentence summary]
SENTIMENT: [positive/negative/tense/neutral]
IMPACT_SCORE: [number 1-10]
"""
    
    try:
        # Generate analysis
        response = model.generate_content(prompt)
        
        if not response.text:
            return {
                "summary": "Analysis unavailable.",
                "sentiment": "neutral",
                "impact_score": 5
            }
        
        # Parse the response
        analysis_text = response.text.strip()
        
        # Extract summary
        summary_match = re.search(r'SUMMARY:\s*(.+?)(?=SENTIMENT:|$)', analysis_text, re.DOTALL | re.IGNORECASE)
        summary = summary_match.group(1).strip() if summary_match else "Summary not available."
        
        # Extract sentiment
        sentiment_match = re.search(r'SENTIMENT:\s*(\w+)', analysis_text, re.IGNORECASE)
        sentiment = sentiment_match.group(1).strip().lower() if sentiment_match else "neutral"
        
        # Normalize sentiment
        if sentiment not in ['positive', 'negative', 'tense', 'neutral']:
            sentiment = 'neutral'
        
        # Extract impact score
        score_match = re.search(r'IMPACT[_ ]SCORE:\s*(\d+)', analysis_text, re.IGNORECASE)
        impact_score = int(score_match.group(1)) if score_match else 5
        
        # Ensure impact score is within range
        impact_score = max(1, min(10, impact_score))
        
        return {
            "summary": summary,
            "sentiment": sentiment.capitalize(),
            "impact_score": impact_score
        }
    
    except Exception as e:
        st.warning(f"⚠️ Failed to analyze article: {article['title'][:50]}... Error: {str(e)}")
        # Return default values on error
        return {
            "summary": article['description'][:200] + "...",
            "sentiment": "Neutral",
            "impact_score": 5
        }


def batch_analyze_articles(articles: list, api_key: str) -> list:
    """
    Analyze multiple articles in batch
    
    Args:
        articles: List of article dictionaries
        api_key: Google Gemini API key
    
    Returns:
        List of articles with added analysis data
    """
    analyzed = []
    
    for article in articles:
        analysis = analyze_article(article, api_key)
        if analysis:
            analyzed.append({
                **article,
                **analysis
            })
    
    return analyzed
