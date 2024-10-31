import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class Backtester:
    def __init__(self, strategy, initial_capital=10000):
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.positions = []
        self.portfolio_value = []
        self.trades = []
    
    def run(self, data: pd.DataFrame) -> dict:
        """Run backtest on historical data"""
        signals = self.strategy.generate_signals(data)
        
        # Initialize tracking variables
        capital = self.initial_capital
        position = 0
        entry_price = 0
        
        # Track portfolio value and trades
        for i in range(len(data)):
            current_price = data['close'].iloc[i]
            current_time = data.index[i]
            
            # Check for signals at current timestamp
            current_signals = [s for s in signals if s['timestamp'] == current_time]
            
            for signal in current_signals:
                if signal['action'] == 'BUY' and position == 0:
                    # Enter long position
                    position = capital / current_price
                    entry_price = current_price
                    portfolio_value = position * current_price
                    self.trades.append({
                        'type': 'ENTRY',
                        'time': current_time,
                        'price': current_price,
                        'portfolio_value': portfolio_value,
                        'size': position
                    })
                elif signal['action'] == 'SELL' and position > 0:
                    # Exit long position
                    portfolio_value = position * current_price
                    capital = portfolio_value
                    self.trades.append({
                        'type': 'EXIT',
                        'time': current_time,
                        'price': current_price,
                        'portfolio_value': portfolio_value,
                        'size': position,
                        'pnl': (current_price - entry_price) * position
                    })
                    position = 0
            
            # Track portfolio value
            current_value = capital if position == 0 else position * current_price
            self.portfolio_value.append({
                'timestamp': current_time,
                'value': current_value
            })
        
        return self.calculate_metrics()
    
    def calculate_metrics(self) -> dict:
        """Calculate backtest performance metrics"""
        if not self.portfolio_value:
            return {
                'total_return': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'win_rate': 0,
                'total_trades': 0
            }
        
        # Convert portfolio value to DataFrame
        portfolio_df = pd.DataFrame(self.portfolio_value)
        portfolio_df.set_index('timestamp', inplace=True)
        
        # Calculate returns
        portfolio_df['returns'] = portfolio_df['value'].pct_change()
        total_return = (portfolio_df['value'].iloc[-1] - self.initial_capital) / self.initial_capital
        
        # Calculate Sharpe ratio (assuming risk-free rate of 0.02)
        risk_free_rate = 0.02
        excess_returns = portfolio_df['returns'] - risk_free_rate/252  # Daily risk-free rate
        sharpe_ratio = np.sqrt(252) * excess_returns.mean() / excess_returns.std() if len(excess_returns) > 1 else 0
        
        # Calculate maximum drawdown
        portfolio_df['cummax'] = portfolio_df['value'].cummax()
        portfolio_df['drawdown'] = (portfolio_df['cummax'] - portfolio_df['value']) / portfolio_df['cummax']
        max_drawdown = portfolio_df['drawdown'].max()
        
        # Calculate win rate
        profitable_trades = len([t for t in self.trades if t.get('pnl', 0) > 0])
        total_trades = len([t for t in self.trades if t.get('pnl') is not None])
        win_rate = profitable_trades / total_trades if total_trades > 0 else 0
        
        return {
            'total_return': total_return * 100,  # Convert to percentage
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown * 100,  # Convert to percentage
            'win_rate': win_rate * 100,  # Convert to percentage
            'total_trades': total_trades
        }
    
    def plot_results(self) -> go.Figure:
        """Create interactive plot of backtest results"""
        # Check if we have data to plot
        if not self.portfolio_value or not self.trades:
            return None

        # Convert portfolio value list to DataFrame first
        portfolio_df = pd.DataFrame(self.portfolio_value)
        portfolio_df.set_index('timestamp', inplace=True)
        
        # Ensure portfolio value data is properly formatted
        portfolio_df['value'] = pd.to_numeric(portfolio_df['value'], errors='coerce')
        portfolio_df = portfolio_df.dropna(subset=['value'])
        
        # Calculate drawdown data before plotting
        portfolio_df['cummax'] = portfolio_df['value'].cummax()
        portfolio_df['drawdown'] = (portfolio_df['cummax'] - portfolio_df['value']) / portfolio_df['cummax'] * 100
        
        # Calculate y-axis ranges with improved padding
        min_value = portfolio_df['value'].min()
        max_value = portfolio_df['value'].max()
        value_range = max_value - min_value
        y_min = min_value - (value_range * 0.1)  # 10% padding
        y_max = max_value + (value_range * 0.1)
        
        # Create figure with increased spacing between subplots
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.15,
            subplot_titles=('Portfolio Value', 'Drawdown'),
            row_heights=[0.7, 0.3]
        )
        
        # Portfolio value line
        fig.add_trace(
            go.Scatter(
                x=portfolio_df.index,
                y=portfolio_df['value'],
                name='Portfolio Value',
                line=dict(color='rgb(49,130,189)', width=2)
            ),
            row=1, col=1
        )
        
        # Add trade markers with error handling
        try:
            for trade in self.trades:
                if not isinstance(trade, dict) or 'time' not in trade or 'portfolio_value' not in trade:
                    continue
                    
                marker_color = 'green' if trade['type'] == 'ENTRY' else 'red'
                marker_symbol = 'triangle-up' if trade['type'] == 'ENTRY' else 'triangle-down'
                
                # Ensure trade time and portfolio value are valid
                x_val = pd.to_datetime(trade['time'])
                y_val = float(trade['portfolio_value'])
                
                fig.add_trace(
                    go.Scatter(
                        x=[x_val],
                        y=[y_val],
                        mode='markers',
                        name=trade['type'],
                        marker=dict(
                            color=marker_color,
                            size=15,
                            symbol=marker_symbol,
                            line=dict(color='white', width=1)
                        ),
                        hovertemplate=(
                            f"<b>{trade['type']}</b><br>" +
                            f"Time: %{x}<br>" +
                            f"Portfolio Value: ${y_val:,.2f}<br>" +
                            f"Price: ${trade['price']:,.2f}<br>" +
                            f"Size: {trade['size']:.4f}<br>" +
                            (f"PnL: ${trade.get('pnl', 0):,.2f}" if 'pnl' in trade else "") +
                            "<extra></extra>"
                        )
                    ),
                    row=1, col=1
                )
        except Exception as e:
            print(f"Error plotting trade markers: {str(e)}")
            # Continue with the rest of the plotting even if trade markers fail
        
        # Drawdown subplot
        fig.add_trace(
            go.Scatter(
                x=portfolio_df.index,
                y=portfolio_df['drawdown'],
                name='Drawdown',
                fill='tozeroy',  # Fill area under drawdown line
                line=dict(color='rgb(204,0,0)', width=2)
            ),
            row=2, col=1
        )
        
        # Update layout with improved settings
        fig.update_layout(
            height=800,
            showlegend=True,
            template='plotly_dark',
            title=f"Backtest Results - {self.strategy.name}",
            margin=dict(t=50, b=50, l=50, r=50),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor='rgba(0,0,0,0.5)'
            )
        )
        
        # Update axes for better visualization
        fig.update_xaxes(
            gridcolor='rgba(128,128,128,0.1)',
            showgrid=True,
            zeroline=False,
            showline=True,
            linewidth=1,
            linecolor='rgba(128,128,128,0.2)'
        )
        
        # Update y-axes with proper ranges and grid
        fig.update_yaxes(
            gridcolor='rgba(128,128,128,0.1)',
            showgrid=True,
            zeroline=False,
            showline=True,
            linewidth=1,
            linecolor='rgba(128,128,128,0.2)',
            row=1, col=1,
            range=[y_min, y_max],  # Set range for portfolio value
            tickformat='$,.0f'  # Format as currency
        )
        
        # Update drawdown y-axis
        max_drawdown = portfolio_df['drawdown'].max()
        fig.update_yaxes(
            gridcolor='rgba(128,128,128,0.1)',
            showgrid=True,
            zeroline=False,
            showline=True,
            linewidth=1,
            linecolor='rgba(128,128,128,0.2)',
            range=[0, max(100, max_drawdown * 1.2)],  # Set range with 20% padding
            tickformat='.1f',  # Format as percentage
            row=2, col=1
        )
        
        return fig
