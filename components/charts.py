import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def create_price_chart(data: pd.DataFrame, symbol: str, chart_params: dict = None) -> go.Figure:
    """
    Create an interactive price chart with volume and optional overlays
    """
    # Verify volume data
    if 'volume' not in data.columns or data['volume'].isnull().all():
        raise ValueError("Volume data is missing or invalid")
    
    # Set volume range
    min_volume = data['volume'].max() * 0.001
    volume_data = data['volume'].where(data['volume'] > min_volume, min_volume)
    volume_max = volume_data.max()
    
    # Calculate price range
    price_min = float(data['low'].min())
    price_max = float(data['high'].max())
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
        height=533,
        showlegend=True,
        xaxis_rangeslider_visible=False,
        template='plotly_dark',
        margin=dict(t=30, b=30),
        dragmode='pan',
        yaxis=dict(
            title="Price",
            gridcolor='rgba(128, 128, 128, 0.1)',
            zerolinecolor='rgba(128, 128, 128, 0.2)',
            domain=[0.2, 1],
            fixedrange=False,
            autorange=True,
            rangemode='normal'
        ),
        yaxis2=dict(
            title="Volume",
            gridcolor='rgba(128, 128, 128, 0.1)',
            zerolinecolor='rgba(128, 128, 128, 0.2)',
            tickformat='.2s',
            domain=[0, 0.18],
            fixedrange=True
        ),
        newshape=dict(line_color='yellow'),
        hovermode='x unified',
        selectdirection='h',
        clickmode='event+select'
    )

    # Update axes for better gridlines
    fig.update_xaxes(
        gridcolor='rgba(128, 128, 128, 0.1)',
        showspikes=True,
        spikemode='across',
        spikesnap='cursor',
        showline=True,
        showgrid=True
    )
    
    fig.update_yaxes(
        gridcolor='rgba(128, 128, 128, 0.1)',
        showspikes=True,
        spikemode='across',
        spikesnap='cursor',
        showline=True,
        showgrid=True,
        row=1, col=1
    )

    # Add buttons for y-axis range control
    fig.update_layout(
        updatemenus=[
            dict(
                type='buttons',
                direction='right',
                x=0.1,
                y=1.1,
                xanchor='left',
                yanchor='top',
                pad=dict(r=10, t=10),
                showactive=False,
                buttons=[
                    dict(
                        label='Reset Zoom',
                        method='relayout',
                        args=[{'yaxis.autorange': True}]
                    ),
                    dict(
                        label='Zoom In',
                        method='relayout',
                        args=[{
                            'yaxis.range': [
                                price_min + (price_range * 0.2),
                                price_max - (price_range * 0.2)
                            ]
                        }]
                    ),
                    dict(
                        label='Zoom Out',
                        method='relayout',
                        args=[{
                            'yaxis.range': [
                                price_min - (price_range * 0.2),
                                price_max + (price_range * 0.2)
                            ]
                        }]
                    )
                ]
            )
        ]
    )

    return fig
