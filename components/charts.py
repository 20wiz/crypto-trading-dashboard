import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def create_price_chart(data: pd.DataFrame, symbol: str, chart_params: dict = None) -> go.Figure:
    """
    Create an interactive price chart with volume and optional overlays
    
    Args:
        data: DataFrame with OHLCV data
        symbol: Trading pair symbol
        chart_params: Dictionary containing chart overlay parameters
            - show_ma: bool, whether to show moving averages
            - ma_periods: list of integers, periods for moving averages
            - show_bb: bool, whether to show Bollinger Bands
            - bb_period: int, period for Bollinger Bands
            - bb_std: float, standard deviation for Bollinger Bands
            - y_axis_range: tuple, custom range for price y-axis (min, max)
            - volume_range: tuple, custom range for volume y-axis (min, max)
    """
    # Verify volume data
    if 'volume' not in data.columns or data['volume'].isnull().all():
        raise ValueError("Volume data is missing or invalid")
    
    # Set volume range
    min_volume = data['volume'].max() * 0.001
    volume_data = data['volume'].where(data['volume'] > min_volume, min_volume)
    volume_max = volume_data.max()
    
    # Get custom ranges from chart_params
    if chart_params:
        y_axis_range = chart_params.get('y_axis_range')
        volume_range = chart_params.get('volume_range', (0, volume_max * 1.1))
    else:
        price_min = data['low'].min()
        price_max = data['high'].max()
        price_range = price_max - price_min
        y_axis_range = (price_min - (price_range * 0.1), price_max + (price_range * 0.1))
        volume_range = (0, volume_max * 1.1)
    
    # Calculate price colors
    colors = ['red' if close < open else 'green' 
              for open, close in zip(data['open'], data['close'])]
    
    # Create figure with secondary y-axis
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=(f'{symbol} Price', 'Volume'),
        row_heights=[0.825, 0.175]
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

    # Add Moving Averages if requested
    if chart_params and chart_params.get('show_ma') and chart_params.get('ma_periods'):
        for period in chart_params['ma_periods']:
            ma = data['close'].rolling(window=period).mean()
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=ma,
                    name=f'MA{period}',
                    line=dict(width=1.5)
                ),
                row=1, col=1
            )

    # Add Bollinger Bands if requested
    if chart_params and chart_params.get('show_bb'):
        period = chart_params.get('bb_period', 20)
        std_dev = chart_params.get('bb_std', 2.0)
        
        middle_band = data['close'].rolling(window=period).mean()
        std = data['close'].rolling(window=period).std()
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)
        
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=upper_band,
                name='Upper BB',
                line=dict(dash='dash', width=1),
                opacity=0.7
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=middle_band,
                name='Middle BB',
                line=dict(dash='dash', width=1),
                opacity=0.7
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=lower_band,
                name='Lower BB',
                line=dict(dash='dash', width=1),
                opacity=0.7
            ),
            row=1, col=1
        )

    # Volume chart with color coding
    fig.add_trace(
        go.Bar(
            x=data.index,
            y=volume_data,
            name='Volume',
            marker=dict(
                color=colors,
                opacity=0.8,
                line=dict(width=1, color='rgba(255, 255, 255, 0.5)')
            ),
            width=0.8
        ),
        row=2, col=1
    )

    # Update layout for better visualization
    fig.update_layout(
        height=533,  # Changed from 800 to 533 (2/3 of original)
        showlegend=True,
        xaxis_rangeslider_visible=False,
        template='plotly_dark',
        margin=dict(t=30, b=30),
        yaxis=dict(
            title="Price",
            gridcolor='rgba(128, 128, 128, 0.1)',
            zerolinecolor='rgba(128, 128, 128, 0.2)',
            domain=[0.2, 1],
            range=y_axis_range
        ),
        yaxis2=dict(
            title="Volume",
            gridcolor='rgba(128, 128, 128, 0.1)',
            zerolinecolor='rgba(128, 128, 128, 0.2)',
            tickformat='.2s',
            domain=[0, 0.18],
            range=volume_range
        )
    )

    # Update axes for better gridlines
    fig.update_xaxes(gridcolor='rgba(128, 128, 128, 0.1)')
    fig.update_yaxes(gridcolor='rgba(128, 128, 128, 0.1)')

    return fig
