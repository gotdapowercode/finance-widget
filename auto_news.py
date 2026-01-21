import streamlit as st
import feedparser
import yfinance as yf
import datetime

# --- Page Config ---
st.set_page_config(page_title="Finance Dashboard", layout="wide", page_icon="📈")

# --- Custom CSS ---
st.markdown("""
<style>
    .news-card {
        background-color: #f0f2f6;
        padding: 15px; border-radius: 10px; margin-bottom: 10px;
        border-left: 5px solid #FF4B4B;
    }
    .news-title { font-size: 18px; font-weight: bold; color: #0e1117; text-decoration: none; }
    .news-meta { font-size: 12px; color: #555; }
</style>
""", unsafe_allow_html=True)

st.title("📈 Market Intelligence Dashboard")

# --- Create Tabs ---
tab1, tab2 = st.tabs(["🔥 Top Stories (Live)", "🔍 Company Search"])

# ==========================
# TAB 1: GENERAL NEWS (Feed)
# ==========================
with tab1:
    st.header("Global Market News")
    if st.button("🔄 Refresh Feed"):
        st.rerun()
    
    try:
        # Yahoo Finance RSS Feed
        rss_url = "https://finance.yahoo.com/news/rssindex"
        feed = feedparser.parse(rss_url)
        
        for item in feed.entries[:10]:
            st.markdown(f"""
            <div class="news-card">
                <a href="{item.link}" target="_blank" class="news-title">{item.title}</a>
                <br><span class="news-meta">🕒 {item.published}</span>
            </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Error loading feed: {e}")
# ==========================
# TAB 2: TICKER SEARCH (RSS FIX)
# ==========================
with tab2:
    st.header("Search by Ticker")
    ticker = st.text_input("Enter Symbol (e.g., NVDA, TSLA, BTC-USD):", value="TSLA").upper()
    
    if ticker:
        # 1. Show Current Price (Keep using yfinance for PRICE only, it is reliable for that)
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            price = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
            currency = info.get('currency', 'USD')
            st.metric(label=f"{ticker} Price", value=f"{price} {currency}")
        except:
            st.warning("Could not fetch price data.")

        # 2. Show News using RSS (More Reliable)
        st.subheader(f"Latest News for {ticker}")
        
        try:
            # We use the specific RSS feed for the ticker
            rss_url = f"https://finance.yahoo.com/rss/headline?s={ticker}"
            feed = feedparser.parse(rss_url)
            
            if not feed.entries:
                st.info(f"No recent news found for {ticker} (or invalid symbol).")
            else:
                for item in feed.entries:
                    title = item.get('title', 'No Title')
                    link = item.get('link', '#')
                    published = item.get('published', 'Recent')
                    
                    st.markdown(f"""
                    <div class="news-card" style="border-left: 5px solid #2e7bcf;">
                        <a href="{link}" target="_blank" class="news-title">{title}</a>
                        <br><span class="news-meta">🕒 {published}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
        except Exception as e:
            st.error(f"Error fetching news: {e}")