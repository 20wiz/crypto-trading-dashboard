import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def format_price(price):
    """Format price based on its magnitude"""
    if pd.isna(price):
        return ''
    if abs(price) >= 1000:  # Large numbers (1000+)
        return f'${price:,.2f}'  # Use comma separator and 2 decimal places
    elif abs(price) >= 1:  # Medium numbers (1-999)
        return f'${price:.2f}'   # 2 decimal places without comma
    else:  # Small numbers (<1)
        return f'${price:.6f}'   # 6 decimal places for small numbers

def display_signals(signals: list):
    """
    Display trading signals in a formatted table with improved styling
    """
    if not signals:
        st.warning("No signals generated yet")
        return

    # Create signals DataFrame
    signals_df = pd.DataFrame(signals)
    
    # Format timestamp as datetime if it isn't already
    if 'timestamp' in signals_df.columns and not pd.api.types.is_datetime64_any_dtype(signals_df['timestamp']):
        signals_df['timestamp'] = pd.to_datetime(signals_df['timestamp'])
    
    # Format the table
    st.subheader("Trading Signals")
    
    # Apply custom price formatting to the DataFrame
    if 'price' in signals_df.columns:
        signals_df['price'] = signals_df['price'].apply(format_price)
    
    # Enhanced table display with better formatting
    st.dataframe(
        signals_df,
        use_container_width=True,
        height=400,
        column_config={
            "timestamp": st.column_config.DatetimeColumn(
                "Time",
                format="DD/MM/YY HH:mm",
                help="Signal timestamp"
            ),
            "price": st.column_config.TextColumn(
                "Price",
                help="Asset price at signal",
            ),
            "action": st.column_config.Column(
                "Action",
                help="Buy or Sell signal"
            ),
            "indicator": st.column_config.Column(
                "Indicator Details",
                help="Technical indicator values"
            )
        }
    )
    
    # Add a summary section with metrics
    if signals:
        col1, col2, col3 = st.columns(3)
        
        # Calculate metrics
        buy_signals = len([s for s in signals if s['action'] == 'BUY'])
        sell_signals = len([s for s in signals if s['action'] == 'SELL'])
        signal_rate = f"{(len(signals) / len(signals_df)) * 100:.1f}%" if len(signals_df) > 0 else "0%"
        
        # Display metrics
        with col1:
            st.metric("Buy Signals", buy_signals)
        with col2:
            st.metric("Sell Signals", sell_signals)
        with col3:
            st.metric("Signal Rate", signal_rate)
        
        # Display latest signal with custom price formatting
        if signals:
            latest = signals[-1]
            st.info(
                f"Latest Signal: {latest['action']} @ {format_price(latest['price'])}\n"
                f"Time: {latest['timestamp']}\n"
                f"Indicators: {latest['indicator']}"
            )
