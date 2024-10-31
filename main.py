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

# Strategy Parameters
st.sidebar.subheader("Strategy Parameters")
if strategy == "MA Crossover":
    short_window = st.sidebar.slider("Short MA Window", min_value=5, max_value=50, value=20, step=1)
    long_window = st.sidebar.slider("Long MA Window", min_value=20, max_value=200, value=50, step=5)
    strategy_params = {'short_window': short_window, 'long_window': long_window}
else:
    rsi_period = st.sidebar.slider("RSI Period", min_value=2, max_value=30, value=14, step=1)
    rsi_overbought = st.sidebar.slider("Overbought Level", min_value=50, max_value=90, value=70, step=1)
    rsi_oversold = st.sidebar.slider("Oversold Level", min_value=10, max_value=50, value=30, step=1)
    strategy_params = {
        'period': rsi_period,
        'overbought': rsi_overbought,
        'oversold': rsi_oversold
    }

# Main content
st.title("Cryptocurrency Trading Dashboard")

# Initialize strategies with parameters
if strategy == "MA Crossover":
    active_strategy = MACrossoverStrategy(**strategy_params)
else:
    active_strategy = RSIStrategy(**strategy_params)

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
            signals = active_strategy.generate_signals(data)
            display_signals(signals)

        with col2:
            # Metrics
            st.subheader("Performance Metrics")
            display_metrics(data, signals)
            
            # Latest signals
            st.subheader("Recent Signals")
            for signal in signals[-5:]:
                st.write(f"Signal: {signal['action']} at {signal['price']:.2f}")
                
            # Display current strategy parameters
            st.subheader("Current Strategy Settings")
            for param, value in strategy_params.items():
                st.write(f"{param.replace('_', ' ').title()}: {value}")
            
            # Notifications
            if len(signals) > 0 and signals[-1] not in st.session_state.notifications:
                st.balloons()
                st.session_state.notifications.append(signals[-1])

    except Exception as e:
        st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
