import streamlit as st
import pandas as pd

def display_signals(signals: list):
    """
    Display trading signals in a formatted table
    """
    if not signals:
        st.warning("No signals generated yet")
        return

    # Create signals DataFrame
    signals_df = pd.DataFrame(signals)
    
    # Format the table
    st.subheader("Trading Signals")
    
    # Style the DataFrame
    def color_action(val):
        color = 'green' if val == 'BUY' else 'red'
        return f'color: {color}'
    
    styled_df = signals_df.style.applymap(
        color_action,
        subset=['action']
    )
    
    # Display the table
    st.dataframe(
        styled_df,
        use_container_width=True,
        height=400
    )
