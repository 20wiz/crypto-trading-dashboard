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
from strategies.bollinger_bands import BollingerBandsStrategy
from strategies.macd_strategy import MACDStrategy
from strategies.combined_strategy import CombinedStrategy
from utils.data_fetcher import get_historical_data
from utils.backtester import Backtester

st.set_page_config(
    page_title="Crypto Trading Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .stSelectbox, .stSlider {
        background-color: #262730;
    }
    .stTab {
        background-color: #1E1E1E;
    }
    .stMetric {
        background-color: #262730;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

if 'notifications' not in st.session_state:
    st.session_state.notifications = []
if 'active_strategy' not in st.session_state:
    st.session_state.active_strategy = None
if 'data' not in st.session_state:
    st.session_state.data = None
if 'timeframe_value' not in st.session_state:
    st.session_state.timeframe_value = "5m"

timeframe_options = {
    "5 minutes": "5m",
    "15 minutes": "15m",
    "30 minutes": "30m",
    "1 hour": "1h",
    "2 hours": "2h",
    "4 hours": "4h",
    "6 hours": "6h",
    "8 hours": "8h",
    "12 hours": "12h",
    "1 day": "1d",
    "3 days": "3d",
    "1 week": "1w",
    "1 month": "1M"
}

st.sidebar.title("Configuration")
exchange = st.sidebar.selectbox("Exchange", ["binance", "coinbase", "kraken"])
symbol = st.sidebar.selectbox("Trading Pair", ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "ADA/USDT"])

st.subheader("Chart Timeframe")
timeframe = st.selectbox(
    "Select chart timeframe",
    options=list(timeframe_options.keys()),
    format_func=lambda x: x,
    key="timeframe_selector"
)
st.session_state.timeframe_value = timeframe_options[timeframe]

st.sidebar.subheader("Chart Options")

show_ma = st.sidebar.checkbox("Show Moving Averages", value=False)
if show_ma:
    ma_periods = st.sidebar.multiselect(
        "MA Periods",
        options=[20, 50, 100, 200],
        default=[50, 200]
    )

show_bb = st.sidebar.checkbox("Show Bollinger Bands", value=False)
if show_bb:
    bb_period = st.sidebar.slider("BB Period", 5, 50, 20)
    bb_std = st.sidebar.slider("BB Standard Deviation", 1.0, 4.0, 2.0, 0.1)

strategy = st.sidebar.selectbox(
    "Strategy", 
    ["MA Crossover", "RSI", "Bollinger Bands", "MACD", "Combined Strategy"]
)

st.sidebar.subheader("Strategy Parameters")
strategy_params = {}

if strategy == "MA Crossover":
    short_window = st.sidebar.slider("Short MA Window", min_value=5, max_value=50, value=20, step=1)
    long_window = st.sidebar.slider("Long MA Window", min_value=20, max_value=200, value=50, step=5)
    strategy_params = {'short_window': short_window, 'long_window': long_window}

elif strategy == "RSI":
    rsi_period = st.sidebar.slider("RSI Period", min_value=2, max_value=30, value=14, step=1)
    rsi_overbought = st.sidebar.slider("Overbought Level", min_value=50, max_value=90, value=70, step=1)
    rsi_oversold = st.sidebar.slider("Oversold Level", min_value=10, max_value=50, value=30, step=1)
    strategy_params = {
        'period': rsi_period,
        'overbought': rsi_overbought,
        'oversold': rsi_oversold
    }

elif strategy == "Bollinger Bands":
    bb_period = st.sidebar.slider("BB Period", min_value=5, max_value=50, value=20, step=1)
    bb_std = st.sidebar.slider("Standard Deviation", min_value=1.0, max_value=4.0, value=2.0, step=0.1)
    use_atr = st.sidebar.checkbox("Use ATR for Exits", value=True)
    if use_atr:
        atr_period = st.sidebar.slider("ATR Period", min_value=5, max_value=30, value=14, step=1)
        atr_multiplier = st.sidebar.slider("ATR Multiplier", min_value=1.0, max_value=5.0, value=2.0, step=0.1)
        strategy_params = {
            'period': bb_period,
            'std_dev': bb_std,
            'use_atr_exits': use_atr,
            'atr_period': atr_period,
            'atr_multiplier': atr_multiplier
        }
    else:
        strategy_params = {
            'period': bb_period,
            'std_dev': bb_std,
            'use_atr_exits': use_atr
        }

elif strategy == "MACD":
    fast_period = st.sidebar.slider("Fast Period", min_value=5, max_value=50, value=12, step=1)
    slow_period = st.sidebar.slider("Slow Period", min_value=10, max_value=100, value=26, step=1)
    signal_period = st.sidebar.slider("Signal Period", min_value=5, max_value=30, value=9, step=1)
    hist_threshold = st.sidebar.slider("Histogram Threshold", min_value=0.0, max_value=1.0, value=0.0, step=0.1)
    strategy_params = {
        'fast_period': fast_period,
        'slow_period': slow_period,
        'signal_period': signal_period,
        'histogram_threshold': hist_threshold
    }

else:  # Combined Strategy
    st.sidebar.subheader("Select Strategies to Combine")
    use_ma = st.sidebar.checkbox("Use MA Crossover", value=True)
    use_rsi = st.sidebar.checkbox("Use RSI", value=True)
    use_bb = st.sidebar.checkbox("Use Bollinger Bands")
    use_macd = st.sidebar.checkbox("Use MACD")
    
    combination_method = st.sidebar.radio(
        "Combination Method",
        ["AND", "OR"],
        help="AND: All strategies must agree | OR: Any strategy can trigger"
    )
    
    strategies_list = []
    if use_ma:
        ma_short = st.sidebar.slider("MA Short Window", min_value=5, max_value=50, value=20, step=1)
        ma_long = st.sidebar.slider("MA Long Window", min_value=20, max_value=200, value=50, step=5)
        strategies_list.append(MACrossoverStrategy(short_window=ma_short, long_window=ma_long))
        
    if use_rsi:
        rsi_period = st.sidebar.slider("RSI Period", min_value=2, max_value=30, value=14, step=1)
        rsi_ob = st.sidebar.slider("RSI Overbought", min_value=50, max_value=90, value=70, step=1)
        rsi_os = st.sidebar.slider("RSI Oversold", min_value=10, max_value=50, value=30, step=1)
        strategies_list.append(RSIStrategy(period=rsi_period, overbought=rsi_ob, oversold=rsi_os))
        
    if use_bb:
        bb_period = st.sidebar.slider("BB Period", min_value=5, max_value=50, value=20, step=1)
        bb_std = st.sidebar.slider("BB Std Dev", min_value=1.0, max_value=4.0, value=2.0, step=0.1)
        strategies_list.append(BollingerBandsStrategy(period=bb_period, std_dev=bb_std))
        
    if use_macd:
        macd_fast = st.sidebar.slider("MACD Fast", min_value=5, max_value=50, value=12, step=1)
        macd_slow = st.sidebar.slider("MACD Slow", min_value=10, max_value=100, value=26, step=1)
        macd_signal = st.sidebar.slider("MACD Signal", min_value=5, max_value=30, value=9, step=1)
        strategies_list.append(MACDStrategy(fast_period=macd_fast, slow_period=macd_slow, signal_period=macd_signal))
    
    strategy_params = {
        'strategies': strategies_list,
        'combination_method': combination_method
    }

st.sidebar.subheader("Backtesting")
initial_capital = st.sidebar.number_input("Initial Capital (USDT)", min_value=100, value=10000, step=100)
backtest_days = st.sidebar.slider("Backtest Period (Days)", min_value=1, max_value=365, value=30)

tab1, tab2 = st.tabs(["Live Trading", "Backtesting"])

def initialize_strategy():
    try:
        if strategy == "MA Crossover":
            return MACrossoverStrategy(**strategy_params)
        elif strategy == "RSI":
            return RSIStrategy(**strategy_params)
        elif strategy == "Bollinger Bands":
            return BollingerBandsStrategy(**strategy_params)
        elif strategy == "MACD":
            return MACDStrategy(**strategy_params)
        elif strategy == "Combined Strategy":
            if len(strategy_params.get('strategies', [])) < 2:
                st.error("Please select at least two strategies to combine")
                return None
            return CombinedStrategy(**strategy_params)
        return None
    except Exception as e:
        st.error(f"Error initializing strategy: {str(e)}")
        return None

def main():
    try:
        active_strategy = initialize_strategy()
        if active_strategy is None:
            st.warning("Please configure a valid strategy to continue")
            return

        try:
            data = get_historical_data(exchange, symbol, st.session_state.timeframe_value)
            if data is None or data.empty:
                st.error("Failed to fetch market data")
                return
        except Exception as e:
            st.error(f"Error fetching market data: {str(e)}")
            return

        try:
            signals = active_strategy.generate_signals(data)
        except Exception as e:
            st.error(f"Error generating signals: {str(e)}")
            return

        with tab1:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader(f"{symbol} Price Chart")
                
                chart_params = {
                    'show_ma': show_ma,
                    'ma_periods': ma_periods if show_ma else None,
                    'show_bb': show_bb,
                    'bb_period': bb_period if show_bb else None,
                    'bb_std': bb_std if show_bb else None
                }

                # Add zoom buttons in a horizontal layout
                zoom_col1, zoom_col2 = st.columns(2)
                with zoom_col1:
                    if st.button("➖ Zoom Out"):
                        y_min = float(data['low'].min() * 0.8)
                        y_max = float(data['high'].max() * 1.2)
                        chart_params['y_axis_range'] = (y_min, y_max)
                with zoom_col2:
                    if st.button("➕ Zoom In"):
                        y_min = float(data['low'].min() * 0.95)
                        y_max = float(data['high'].max() * 1.05)
                        chart_params['y_axis_range'] = (y_min, y_max)

                # Create and display the chart
                fig = create_price_chart(data, symbol, chart_params)
                st.plotly_chart(fig, use_container_width=True)
                
                try:
                    display_signals(signals)
                except Exception as e:
                    st.error(f"Error displaying signals: {str(e)}")

            with col2:
                try:
                    st.subheader("Performance Metrics")
                    display_metrics(data, signals)
                except Exception as e:
                    st.error(f"Error displaying metrics: {str(e)}")
                
                st.subheader("Recent Signals")
                if signals:
                    for signal in signals[-5:]:
                        st.write(f"Signal: {signal['action']} at {signal['price']:.2f}")
                        st.write(f"Indicators: {signal['indicator']}")
                else:
                    st.info("No signals generated yet")
                    
                st.subheader("Current Strategy Settings")
                if strategy == "Combined Strategy":
                    st.write(f"Combination Method: {strategy_params['combination_method']}")
                    st.write(f"Active Strategies: {len(strategy_params['strategies'])}")
                    for s in strategy_params['strategies']:
                        st.write(f"- {s.name}")
                else:
                    for param, value in strategy_params.items():
                        st.write(f"{param.replace('_', ' ').title()}: {value}")
        
        with tab2:
            st.subheader("Backtest Results")
            try:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=backtest_days)
                backtest_data = get_historical_data(
                    exchange, 
                    symbol, 
                    st.session_state.timeframe_value, 
                    limit=1440*backtest_days
                )
                
                if backtest_data is not None and not backtest_data.empty:
                    backtester = Backtester(active_strategy, initial_capital)
                    results = backtester.run(backtest_data)
                    
                    col1, col2, col3, col4, col5 = st.columns(5)
                    col1.metric("Total Return", f"{results['total_return']:.2f}%")
                    col2.metric("Sharpe Ratio", f"{results['sharpe_ratio']:.2f}")
                    col3.metric("Max Drawdown", f"{results['max_drawdown']:.2f}%")
                    col4.metric("Win Rate", f"{results['win_rate']:.2f}%")
                    col5.metric("Total Trades", results['total_trades'])
                    
                    backtest_chart = backtester.plot_results()
                    if backtest_chart:
                        st.plotly_chart(backtest_chart, use_container_width=True)
                    else:
                        st.warning("No backtest results to display")
                else:
                    st.error("Failed to fetch backtest data")
                    
            except Exception as e:
                st.error(f"Error during backtesting: {str(e)}")

    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
