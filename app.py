import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="📈 SmartFin Lab", layout="wide")
st.title("📊 SmartFin Lab – 股票篩選器")

# Sidebar 篩選選單
st.sidebar.header("📌 篩選條件")

sectors = ["All", "Technology", "Healthcare", "Financial Services", "Consumer Defensive", "Energy"]
selected_sector = st.sidebar.selectbox("選擇產業", sectors)

pe_min, pe_max = st.sidebar.slider("本益比 (PE Ratio)", 0, 100, (0, 25))
div_min, div_max = st.sidebar.slider("殖利率 (%)", 0.0, 10.0, (0.0, 5.0))

market_cap_options = ["All", "Large Cap (>10B)", "Mid Cap (2B-10B)", "Small Cap (<2B)"]
selected_mktcap = st.sidebar.selectbox("市值等級", market_cap_options)

# 模擬股票資料（實際應接API或資料庫）
def load_sample_data():
    tickers = ['AAPL', 'MSFT', 'KO', 'JNJ', 'WMT', 'XOM', 'TSLA', 'NVDA', 'JPM', 'T']
    sectors = ['Technology', 'Technology', 'Consumer Defensive', 'Healthcare', 'Consumer Defensive',
               'Energy', 'Consumer Cyclical', 'Technology', 'Financial Services', 'Communication']
    market_caps = [2.5e12, 2.2e12, 270e9, 400e9, 400e9, 500e9, 800e9, 1.4e12, 380e9, 140e9]
    pe_ratios = [28.5, 32.2, 23.1, 17.8, 22.5, 12.3, 60.0, 45.0, 11.5, 7.2]
    dividends = [0.55, 0.75, 3.2, 2.7, 1.5, 4.1, 0.0, 0.1, 2.8, 6.0]

    df = pd.DataFrame({
        'Ticker': tickers,
        'Company': ['Apple', 'Microsoft', 'Coca-Cola', 'Johnson & Johnson', 'Walmart',
                    'Exxon Mobil', 'Tesla', 'NVIDIA', 'JPMorgan Chase', 'AT&T'],
        'Sector': sectors,
        'Market Cap': market_caps,
        'PE Ratio': pe_ratios,
        'Dividend Yield': dividends
    })
    return df

data = load_sample_data()

# 根據選擇篩選
if selected_sector != "All":
    data = data[data['Sector'] == selected_sector]

data = data[(data['PE Ratio'] >= pe_min) & (data['PE Ratio'] <= pe_max)]
data = data[(data['Dividend Yield'] >= div_min) & (data['Dividend Yield'] <= div_max)]

if selected_mktcap != "All":
    if "Large" in selected_mktcap:
        data = data[data['Market Cap'] >= 10e9]
    elif "Mid" in selected_mktcap:
        data = data[(data['Market Cap'] >= 2e9) & (data['Market Cap'] < 10e9)]
    elif "Small" in selected_mktcap:
        data = data[data['Market Cap'] < 2e9]

# 顯示結果
st.subheader("📈 篩選結果")
st.dataframe(data.style.format({
    "Market Cap": "$ {:,.0f}",
    "PE Ratio": "{:.2f}",
    "Dividend Yield": "{:.2f}%"
}))

# 個股簡易查詢
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 查詢單一股票")
ticker_input = st.sidebar.text_input("輸入股票代號 (e.g. AAPL)")

if ticker_input:
    try:
        stock = yf.Ticker(ticker_input)
        info = stock.info
        st.subheader(f"📌 {info['longName']} ({ticker_input.upper()})")
        col1, col2 = st.columns(2)
        col1.metric("市值", f"$ {info['marketCap']:,}")
        col1.metric("本益比", f"{info.get('trailingPE', 'N/A')}")
        col2.metric("殖利率", f"{info.get('dividendYield', 0)*100:.2f}%")
        col2.metric("產業類別", info.get('sector', 'N/A'))

        hist = stock.history(period="6mo")
        st.line_chart(hist['Close'])
    except:
        st.error("找不到該股票資訊，請確認代號是否正確。")
