import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def create_price_chart(data: pd.DataFrame, symbol: str) -> go.Figure:
    """
    Create an interactive price chart with volume
    """
    # Verify volume data
    if 'volume' not in data.columns or data['volume'].isnull().all():
        raise ValueError("Volume data is missing or invalid")
    
    # Set minimum volume height
    min_volume = data['volume'].max() * 0.001
    volume_data = data['volume'].where(data['volume'] > min_volume, min_volume)
    
    # Calculate price colors
    colors = ['red' if close < open else 'green' 
              for open, close in zip(data['open'], data['close'])]
    
    # Create figure with secondary y-axis
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=(f'{symbol} Price', 'Volume'),
        row_heights=[0.65, 0.35]  # Increased volume subplot height
    )

    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data['open'],
            high=data['high'],
            low=data['low'],
            close=data['close'],
            name='OHLC'
        ),
        row=1, col=1
    )

    # Volume chart with color coding and improved visibility
    fig.add_trace(
        go.Bar(
            x=data.index,
            y=volume_data,
            name='Volume',
            marker=dict(
                color=colors,
                opacity=0.8,  # Increased opacity
                line=dict(width=1, color='rgba(255, 255, 255, 0.5)')  # Add bar borders
            ),
            width=0.8  # Adjust bar width (0-1)
        ),
        row=2, col=1
    )

    # Update layout for better visualization
    fig.update_layout(
        height=800,
        showlegend=False,
        xaxis_rangeslider_visible=False,
        template='plotly_dark',
        margin=dict(t=30, b=30),  # Adjust margins
        yaxis=dict(
            title="Price",
            gridcolor='rgba(128, 128, 128, 0.1)',
            zerolinecolor='rgba(128, 128, 128, 0.2)',
            domain=[0.35, 1]  # Adjust price chart domain
        ),
        yaxis2=dict(
            title="Volume",
            gridcolor='rgba(128, 128, 128, 0.1)',
            zerolinecolor='rgba(128, 128, 128, 0.2)',
            tickformat='.2s',  # Use SI units for volume
            domain=[0, 0.32]  # Adjust volume chart domain
        )
    )

    # Update axes for better gridlines
    fig.update_xaxes(gridcolor='rgba(128, 128, 128, 0.1)')
    fig.update_yaxes(gridcolor='rgba(128, 128, 128, 0.1)')

    return fig
