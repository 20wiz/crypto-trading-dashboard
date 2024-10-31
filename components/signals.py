import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def display_signals(signals: list):
    """
    Display trading signals in a formatted table with improved styling
    """
    if not signals:
        st.warning("No signals generated yet")
        return

    # Create signals DataFrame
    signals_df = pd.DataFrame(signals)
    
    # Format the table
    st.subheader("Trading Signals")
    
    # Style the DataFrame using the new map method instead of deprecated applymap
    def color_action(df):
        return df.map(lambda val: f'color: {"green" if val == "BUY" else "red"}')
    
    styled_df = signals_df.style.map(
        color_action,
        subset=['action']
    )
    
    # Enhanced table display with better formatting
    st.dataframe(
        styled_df,
        use_container_width=True,
        height=400,
        column_config={
            "timestamp": st.column_config.DatetimeColumn(
                "Time",
                format="DD/MM/YY HH:mm"
            ),
            "price": st.column_config.NumberColumn(
                "Price",
                format="$.2f"
            ),
            "action": "Action",
            "indicator": "Indicator Details"
        }
    )
    
    # Add a summary section
    if signals:
        col1, col2 = st.columns(2)
        with col1:
            buy_signals = len([s for s in signals if s['action'] == 'BUY'])
            sell_signals = len([s for s in signals if s['action'] == 'SELL'])
            st.metric("Buy Signals", buy_signals)
        with col2:
            st.metric("Sell Signals", sell_signals)
