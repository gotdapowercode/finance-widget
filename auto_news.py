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

# --- SIDEBAR: Market Selection ---
st.sidebar.title("⚙️ Settings")
market = st.sidebar.selectbox("Select Market", ["🇺🇸 United States", "🇦🇺 Australia"])

# Define settings based on selection
if market == "🇦🇺 Australia":
    # Yahoo Finance Australia RSS
    DEFAULT_RSS = "https://au.finance.yahoo.com/news/rssindex"
    SUFFIX = ".AX"
    CURRENCY_SYMBOL = "A$"
    EXAMPLE_TICKER = "BHP" # Example for the text input default
else:
    # Yahoo Finance US RSS
    DEFAULT_RSS = "https://finance.yahoo.com/news/rssindex"
    SUFFIX = ""
    CURRENCY_SYMBOL = "$"
    EXAMPLE_TICKER = "NVDA"

st.title(f"📈 Market Intelligence Dashboard ({market})")

# --- Create Tabs ---
tab1, tab2 = st.tabs([f"🔥 Top Stories ({market})", "🔍 Company Search"])

# ==========================
# TAB 1: GENERAL NEWS (Feed)
# ==========================
with tab1:
    st.header(f"Top Financial News")
    if st.button("🔄 Refresh Feed"):
        st.rerun()
    
    try:
        feed = feedparser.parse(DEFAULT_RSS)
        
        if not feed.entries:
            st.warning("No news found. The feed might be temporarily down.")
        
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
# TAB 2: TICKER SEARCH
# ==========================
with tab2:
    st.header("Search by Ticker")
    
    # Dynamic placeholder based on region
    user_input = st.text_input(
        f"Enter Symbol (e.g., {EXAMPLE_TICKER}):", 
        value=EXAMPLE_TICKER
    ).upper().strip()
    
    if user_input:
        # --- Smart Suffix Logic ---
        # If we are in AU mode, user didn't type .AX, and it looks like a stock (no hyphens like BTC-USD)
        # We auto-add the suffix
        if market == "🇦🇺 Australia" and not user_input.endswith(".AX") and "-" not in user_input:
            ticker = f"{user_input}{SUFFIX}"
            st.caption(f"ℹ️ Automatically searching for Australian ticker: **{ticker}**")
        else:
            ticker = user_input

        # 1. Show Current Price
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Use 'regularMarketPrice' as a fallback if 'currentPrice' is missing
            price = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
            currency = info.get('currency', 'USD')
            
            # Simple color coding: Green if positive change, Red if negative (requires 'regularMarketChangePercent')
            change = info.get('regularMarketChangePercent', 0) * 100
            delta_color = "normal"
            if change > 0: delta_color = "off" # Streamlit metric handles color automatically if we use delta

            col1, col2 = st.columns([1, 3])
            with col1:
                st.metric(
                    label=f"{ticker} Price", 
                    value=f"{price} {currency}", 
                    delta=f"{change:.2f}%" if price != 'N/A' else None
                )
            with col2:
                # Show the company name if available
                long_name = info.get('longName', ticker)
                st.markdown(f"### **{long_name}**")
                
        except Exception:
            st.warning(f"Could not fetch price data for {ticker}. Check the symbol.")

        # 2. Show News using RSS
        st.subheader(f"Latest News for {ticker}")
        
        try:
            # RSS URL is generally the same structure for both markets when searching by symbol
            rss_url = f"https://finance.yahoo.com/rss/headline?s={ticker}"
            feed = feedparser.parse(rss_url)
            
            if not feed.entries:
                st.info(f"No recent news found for {ticker}.")
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
