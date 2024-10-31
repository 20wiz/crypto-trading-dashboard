import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def create_price_chart(data: pd.DataFrame, symbol: str) -> go.Figure:
    """
    Create an interactive price chart with volume
    """
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.03, subplot_titles=(f'{symbol} Price', 'Volume'),
                        row_width=[0.7, 0.3])

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

    # Volume chart
    fig.add_trace(
        go.Bar(
            x=data.index,
            y=data['volume'],
            name='Volume'
        ),
        row=2, col=1
    )

    # Update layout
    fig.update_layout(
        height=800,
        showlegend=False,
        xaxis_rangeslider_visible=False,
        template='plotly_dark'
    )

    return fig
