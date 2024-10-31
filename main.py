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
from utils.backtester import Backtester

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

# Backtesting Parameters
st.sidebar.subheader("Backtesting")
initial_capital = st.sidebar.number_input("Initial Capital (USDT)", min_value=100, value=10000, step=100)
backtest_days = st.sidebar.slider("Backtest Period (Days)", min_value=1, max_value=365, value=30)

# Main content
st.title("Cryptocurrency Trading Dashboard")

# Initialize strategies with parameters
if strategy == "MA Crossover":
    active_strategy = MACrossoverStrategy(**strategy_params)
else:
    active_strategy = RSIStrategy(**strategy_params)

# Create tabs for live trading and backtesting
tab1, tab2 = st.tabs(["Live Trading", "Backtesting"])

def main():
    try:
        # Fetch latest data
        data = get_historical_data(exchange, symbol, timeframe)
        
        with tab1:
            # Live Trading View
            col1, col2 = st.columns([2, 1])
            
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
        
        with tab2:
            # Backtesting View
            st.subheader("Backtest Results")
            
            # Get historical data for backtesting
            end_date = datetime.now()
            start_date = end_date - timedelta(days=backtest_days)
            backtest_data = get_historical_data(exchange, symbol, timeframe, limit=1440*backtest_days)
            
            # Run backtest
            backtester = Backtester(active_strategy, initial_capital)
            results = backtester.run(backtest_data)
            
            # Display metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Total Return", f"{results['total_return']:.2f}%")
            col2.metric("Sharpe Ratio", f"{results['sharpe_ratio']:.2f}")
            col3.metric("Max Drawdown", f"{results['max_drawdown']:.2f}%")
            col4.metric("Win Rate", f"{results['win_rate']:.2f}%")
            col5.metric("Total Trades", results['total_trades'])
            
            # Display backtest chart
            backtest_chart = backtester.plot_results()
            if backtest_chart:
                st.plotly_chart(backtest_chart, use_container_width=True)
            
            # Notifications for new signals
            if len(signals) > 0 and signals[-1] not in st.session_state.notifications:
                st.balloons()
                st.session_state.notifications.append(signals[-1])

    except Exception as e:
        st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
