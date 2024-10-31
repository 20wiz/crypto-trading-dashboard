import streamlit as st
import pandas as pd

def display_metrics(data: pd.DataFrame, signals: list):
    """
    Display trading metrics and statistics
    """
    if not signals:
        st.warning("No signals generated yet")
        return

    # Calculate basic metrics
    latest_price = data['close'].iloc[-1]
    price_change = ((latest_price - data['close'].iloc[0]) / data['close'].iloc[0]) * 100
    
    # Display metrics in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Current Price",
            value=f"${latest_price:.2f}",
            delta=f"{price_change:.2f}%"
        )
    
    with col2:
        st.metric(
            label="24h Volume",
            value=f"${data['volume'].tail(24).sum():,.0f}"
        )
    
    with col3:
        signal_count = len(signals)
        st.metric(
            label="Total Signals",
            value=signal_count
        )

    # Trading statistics
    st.subheader("Trading Statistics")
    
    buy_signals = len([s for s in signals if s['action'] == 'BUY'])
    sell_signals = len([s for s in signals if s['action'] == 'SELL'])
    
    stats_col1, stats_col2 = st.columns(2)
    
    with stats_col1:
        st.write(f"Buy Signals: {buy_signals}")
        st.write(f"Sell Signals: {sell_signals}")
    
    with stats_col2:
        if len(signals) > 1:
            avg_holding_time = (signals[-1]['timestamp'] - signals[0]['timestamp']) / len(signals)
            st.write(f"Avg Signal Interval: {avg_holding_time}")
