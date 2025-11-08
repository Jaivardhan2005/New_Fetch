import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from news_fetcher import fetch_news
from ai_processor import analyze_article

# ========== CONFIGURATION ==========
# You can use environment variables for security or hardcode for quick testing
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDovQaUVVcDEeEr4YltP5FRXyf67BgEkVU")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "pub_5f7c0585e0484d0d8aeb3e03010721d8")

# ========== PAGE CONFIGURATION ==========
st.set_page_config(
    page_title="InsightVault Lite",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========== CUSTOM CSS FOR DARK THEME ==========
st.markdown("""
<style>
    /* Main app styling */
    .main {
        background-color: #0E1117;
    }
    
    /* Header styling */
    .header-container {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .header-title {
        font-size: 3rem;
        font-weight: 800;
        color: white;
        margin: 0;
    }
    
    .header-subtitle {
        font-size: 1.2rem;
        color: #E0E0E0;
        margin-top: 0.5rem;
    }
    
    /* Card styling */
    .news-card {
        background: #1E1E1E;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s, box-shadow 0.2s;
        border-left: 4px solid #667eea;
    }
    
    .news-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(102, 126, 234, 0.4);
    }
    
    .news-headline {
        font-size: 1.3rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 0.8rem;
    }
    
    .news-summary {
        color: #B0B0B0;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    
    .sentiment-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        margin-right: 0.5rem;
    }
    
    .sentiment-positive { background-color: #4CAF50; color: white; }
    .sentiment-negative { background-color: #F44336; color: white; }
    .sentiment-tense { background-color: #FF9800; color: white; }
    .sentiment-neutral { background-color: #9E9E9E; color: white; }
    
    .impact-score {
        font-size: 1.1rem;
        font-weight: 600;
        color: #667eea;
    }
    
    .news-link {
        color: #667eea;
        text-decoration: none;
        font-weight: 500;
    }
    
    .news-link:hover {
        text-decoration: underline;
    }
    
    /* Update timestamp */
    .update-time {
        text-align: center;
        color: #888;
        font-size: 0.9rem;
        margin-top: 1rem;
    }
    
    /* Top impact section */
    .top-impact-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ========== HELPER FUNCTIONS ==========
def get_sentiment_color(sentiment):
    """Return color for sentiment badge"""
    sentiment = sentiment.lower()
    if 'positive' in sentiment:
        return 'sentiment-positive'
    elif 'negative' in sentiment:
        return 'sentiment-negative'
    elif 'tense' in sentiment:
        return 'sentiment-tense'
    else:
        return 'sentiment-neutral'

def create_impact_bar(score):
    """Create visual impact score bar"""
    max_score = 10
    filled = int((score / max_score) * 10)
    empty = 10 - filled
    
    if score >= 7:
        color = "🟥"
    elif score >= 4:
        color = "🟨"
    else:
        color = "🟩"
    
    return color * filled + "⬜" * empty

# ========== MAIN APP ==========
def main():
    # Header
    st.markdown("""
    <div class="header-container">
        <h1 class="header-title">🔍 InsightVault Lite</h1>
        <p class="header-subtitle">AI-Powered News & Threat Analysis Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Input Section
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        topic_options = ["Defence", "Technology", "Geopolitics", "Cybersecurity", "Economy", "Custom"]
        selected_topic = st.selectbox("Select Topic", topic_options)
    
    with col2:
        if selected_topic == "Custom":
            search_query = st.text_input("Enter your keywords", placeholder="e.g., AI weapons, climate policy")
        else:
            search_query = selected_topic
    
    with col3:
        st.write("")  # Spacing
        st.write("")  # Spacing
        analyze_button = st.button("🔎 Analyze News", type="primary", use_container_width=True)
    
    # Main Analysis Section
    if analyze_button and search_query:
        with st.spinner("🔄 Fetching latest news..."):
            # Fetch news articles
            articles = fetch_news(search_query, NEWS_API_KEY, max_results=10)
            
            if not articles:
                st.error("❌ No articles found. Please try a different query or check your API key.")
                return
            
            st.success(f"✅ Found {len(articles)} articles. Analyzing with AI...")
        
        # Analyze articles with AI
        analyzed_articles = []
        progress_bar = st.progress(0)
        
        for idx, article in enumerate(articles):
            with st.spinner(f"Analyzing article {idx + 1}/{len(articles)}..."):
                analysis = analyze_article(article, GEMINI_API_KEY)
                if analysis:
                    analyzed_articles.append({
                        **article,
                        **analysis
                    })
            progress_bar.progress((idx + 1) / len(articles))
        
        progress_bar.empty()
        
        if not analyzed_articles:
            st.error("❌ Failed to analyze articles. Please check your Gemini API key.")
            return
        
        # Display timestamp
        st.markdown(f'<p class="update-time">Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>', 
                   unsafe_allow_html=True)
        
        # Top 3 High-Impact News Section
        st.markdown("---")
        st.markdown("## 🚨 Top 3 High-Impact News")
        
        top_impact = sorted(analyzed_articles, key=lambda x: x.get('impact_score', 0), reverse=True)[:3]
        
        for idx, article in enumerate(top_impact, 1):
            st.markdown(f"""
            <div class="top-impact-card">
                <h3>#{idx} {article['title']}</h3>
                <p>{article['summary']}</p>
                <p><strong>Impact Score:</strong> {article['impact_score']}/10 | 
                <strong>Sentiment:</strong> {article['sentiment']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Sentiment Analysis Chart
        st.markdown("---")
        st.markdown("## 📊 Sentiment Distribution")
        
        sentiment_counts = {}
        for article in analyzed_articles:
            sentiment = article.get('sentiment', 'neutral').lower()
            # Normalize sentiment names
            if 'positive' in sentiment:
                sentiment = 'Positive'
            elif 'negative' in sentiment:
                sentiment = 'Negative'
            elif 'tense' in sentiment:
                sentiment = 'Tense'
            else:
                sentiment = 'Neutral'
            
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        
        # Create bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=list(sentiment_counts.keys()),
                y=list(sentiment_counts.values()),
                marker=dict(
                    color=['#4CAF50' if s == 'Positive' else 
                           '#F44336' if s == 'Negative' else 
                           '#FF9800' if s == 'Tense' else 
                           '#9E9E9E' for s in sentiment_counts.keys()]
                ),
                text=list(sentiment_counts.values()),
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title="Article Sentiment Breakdown",
            xaxis_title="Sentiment",
            yaxis_title="Number of Articles",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display All Articles
        st.markdown("---")
        st.markdown("## 📰 Detailed Analysis")
        
        for idx, article in enumerate(analyzed_articles, 1):
            sentiment_class = get_sentiment_color(article.get('sentiment', 'neutral'))
            impact_score = article.get('impact_score', 0)
            
            st.markdown(f"""
            <div class="news-card">
                <div class="news-headline">{idx}. {article['title']}</div>
                <div class="news-summary">{article['summary']}</div>
                <div style="margin: 1rem 0;">
                    <span class="sentiment-badge {sentiment_class}">
                        {article.get('sentiment', 'Neutral')}
                    </span>
                    <span class="impact-score">Impact: {impact_score}/10</span>
                </div>
                <div style="margin: 0.5rem 0;">
                    {create_impact_bar(impact_score)}
                </div>
                <a href="{article['url']}" target="_blank" class="news-link">
                    🔗 Read full article
                </a>
            </div>
            """, unsafe_allow_html=True)
    
    elif analyze_button:
        st.warning("⚠️ Please enter a search query or select a topic.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem 0;">
        <p>Built with ❤️ using Streamlit + Google Gemini AI</p>
        <p style="font-size: 0.8rem;">InsightVault Lite v1.0 | Powered by NewsData.io</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()