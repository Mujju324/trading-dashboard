import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from ta.trend import SMAIndicator, MACD
from ta.momentum import RSIIndicator

st.set_page_config(page_title="Trading Dashboard", layout="wide")
st.title("📈 Trading Dashboard")

# Sidebar Inputs
symbol = st.sidebar.text_input("Stock Symbol (e.g. AAPL, RELIANCE.NS)", "AAPL")
period = st.sidebar.selectbox("Select Period", ["30d", "90d", "180d", "1y", "2y"], index=1)

# Download Data
data = yf.download(symbol, period=period)

# Basic Validations
if data.empty:
    st.error("❌ No data fetched. Please check the stock symbol or time period.")
    st.stop()

if 'Close' not in data.columns:
    st.error("❌ 'Close' column not found in data.")
    st.stop()

data = data.dropna(subset=['Close'])

if data.empty:
    st.error("❌ All 'Close' values are missing. Cannot proceed.")
    st.stop()

# Calculate Technical Indicators
data["SMA_20"] = SMAIndicator(close=data['Close'], window=20).sma_indicator()
data["RSI"] = RSIIndicator(close=data['Close'], window=14).rsi()
macd = MACD(close=data['Close'])
data["MACD"] = macd.macd_diff()

# Buy/Sell Signals
data["Signal"] = 0
data.loc[data["RSI"] < 30, "Signal"] = 1  # Buy
data.loc[data["RSI"] > 70, "Signal"] = -1  # Sell

# Candlestick Chart
fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=data.index, open=data['Open'], high=data['High'],
    low=data['Low'], close=data['Close'], name='Candlestick'
))
fig.add_trace(go.Scatter(x=data.index, y=data["SMA_20"], mode="lines", name="SMA 20"))

# Buy/Sell markers
buy = data[data["Signal"] == 1]
sell = data[data["Signal"] == -1]

fig.add_trace(go.Scatter(
    x=buy.index, y=buy["Close"], mode="markers",
    marker=dict(symbol="triangle-up", color="green", size=10), name="Buy"
))
fig.add_trace(go.Scatter(
    x=sell.index, y=sell["Close"], mode="markers",
    marker=dict(symbol="triangle-down", color="red", size=10), name="Sell"
))

fig.update_layout(
    title=f"{symbol} Price Chart + SMA/Buy-Sell Signals",
    xaxis_title="Date", yaxis_title="Price"
)
st.plotly_chart(fig, use_container_width=True)

# RSI & MACD Line Chart
st.subheader("📊 RSI & MACD Indicators")
st.line_chart(data[["RSI", "MACD"]])
