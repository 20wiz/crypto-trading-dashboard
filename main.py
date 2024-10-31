import streamlit as st
import ccxt
import pandas as pd
from datetime import datetime, timedelta
import time

from components.charts import create_price_chart
from components.metrics import display_metrics
from components.signals import display_signals
from strategies.ma_crossover import MACrossoverStrategy
from strategies.rsi_strategy import RSIStrategy
from utils.data_fetcher import get_historical_data

# Page config
st.set_page_config(
    page_title="Crypto Trading Dashboard",
    page_icon="📈",
    layout="wide"
)

# Initialize session state
if 'notifications' not in st.session_state:
    st.session_state.notifications = []

# Sidebar
st.sidebar.title("Configuration")
exchange = st.sidebar.selectbox("Exchange", ["binance", "coinbase", "kraken"])
symbol = st.sidebar.selectbox("Trading Pair", ["BTC/USDT", "ETH/USDT", "SOL/USDT"])
timeframe = st.sidebar.selectbox("Timeframe", ["1m", "5m", "15m", "1h", "4h", "1d"])
strategy = st.sidebar.selectbox("Strategy", ["MA Crossover", "RSI"])

# Main content
st.title("Cryptocurrency Trading Dashboard")

# Initialize strategies
ma_strategy = MACrossoverStrategy()
rsi_strategy = RSIStrategy()

# Create columns for layout
col1, col2 = st.columns([2, 1])

def main():
    try:
        # Fetch latest data
        data = get_historical_data(exchange, symbol, timeframe)
        
        with col1:
            # Price chart
            st.subheader(f"{symbol} Price Chart")
            fig = create_price_chart(data, symbol)
            st.plotly_chart(fig, use_container_width=True)
            
            # Strategy signals
            if strategy == "MA Crossover":
                signals = ma_strategy.generate_signals(data)
            else:
                signals = rsi_strategy.generate_signals(data)
            
            display_signals(signals)

        with col2:
            # Metrics
            st.subheader("Performance Metrics")
            display_metrics(data, signals)
            
            # Latest signals
            st.subheader("Recent Signals")
            for signal in signals[-5:]:
                st.write(f"Signal: {signal['action']} at {signal['price']:.2f}")
                
            # Notifications
            if len(signals) > 0 and signals[-1] not in st.session_state.notifications:
                st.balloons()
                st.session_state.notifications.append(signals[-1])

    except Exception as e:
        st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
