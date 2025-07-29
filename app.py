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

# 從 CSV 載入 1000 支股票模擬資料
@st.cache_data
def load_large_sample():
    df = pd.read_csv("https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents-financials.csv")
    df = df.rename(columns={
        "Symbol": "Ticker",
        "Name": "Company",
        "Sector": "Sector",
        "Market Cap": "Market Cap",
        "Price/Earnings": "PE Ratio",
        "Dividend Yield": "Dividend Yield"
    })
    df = df.dropna(subset=["PE Ratio", "Dividend Yield", "Market Cap"])
    df["Market Cap"] = df["Market Cap"].astype(float)
    df["PE Ratio"] = df["PE Ratio"].astype(float)
    df["Dividend Yield"] = df["Dividend Yield"].astype(float)
    return df

data = load_large_sample()

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
st.dataframe(data.head(100).style.format({
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
