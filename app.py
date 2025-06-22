import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import ta

st.set_page_config(page_title="Trading Dashboard", layout="wide")
st.title("📈 Trading Dashboard")

# Sidebar inputs
symbol = st.sidebar.text_input("Stock Symbol (e.g. AAPL, RELIANCE.NS)", "AAPL")
period = st.sidebar.selectbox("Select Period", ["30d", "90d", "180d", "1y", "2y"], index=1)

# Download data
data = yf.download(symbol, period=period)

# Check for essential column
if 'Close' not in data.columns:
    st.error("❌ 'Close' column not found. Invalid symbol or data unavailable.")
    st.stop()

# Clean and check data
data = data.dropna(subset=['Close'])
if data.empty:
    st.error("❌ No data available after cleaning. Try another symbol or timeframe.")
    st.stop()

# Technical indicators
data["SMA_20"] = ta.trend.sma_indicator(data['Close'], window=20)
data["RSI"] = ta.momentum.rsi(data['Close'], window=14)
macd = ta.trend.macd(data['Close'])
macd_signal = ta.trend.macd_signal(data['Close'])
data["MACD"] = macd - macd_signal

# Signal logic
data["Signal"] = 0
data.loc[data["RSI"] < 30, "Signal"] = 1
data.loc[data["RSI"] > 70, "Signal"] = -1

# Candlestick chart
fig = go.Figure()
fig.add_trace(go.Candlestick(x=data.index,
                             open=data['Open'],
                             high=data['High'],
                             low=data['Low'],
                             close=data['Close'],
                             name='Candlestick'))

fig.add_trace(go.Scatter(x=data.index, y=data['SMA_20'], mode='lines', name='SMA 20'))

# Buy/Sell signals
buy_signals = data[data['Signal'] == 1]
sell_signals = data[data['Signal'] == -1]

fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals['Close'],
                         mode='markers',
                         marker=dict(symbol='triangle-up', color='green', size=10),
                         name='Buy Signal'))

fig.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals['Close'],
                         mode='markers',
                         marker=dict(symbol='triangle-down', color='red', size=10),
                         name='Sell Signal'))

fig.update_layout(title=f"{symbol} Price Chart with Indicators",
                  xaxis_title="Date",
                  yaxis_title="Price")

st.plotly_chart(fig, use_container_width=True)

# Additional indicators
st.subheader("📉 RSI & MACD Chart")
st.line_chart(data[['RSI', 'MACD']])
