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
                    self.trades.append({
                        'type': 'ENTRY',
                        'time': current_time,
                        'price': current_price,
                        'size': position
                    })
                elif signal['action'] == 'SELL' and position > 0:
                    # Exit long position
                    capital = position * current_price
                    self.trades.append({
                        'type': 'EXIT',
                        'time': current_time,
                        'price': current_price,
                        'size': position,
                        'pnl': (current_price - entry_price) * position
                    })
                    position = 0
            
            # Track portfolio value
            self.portfolio_value.append({
                'timestamp': current_time,
                'value': capital if position == 0 else position * current_price
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
        if not self.portfolio_value:
            return None
            
        portfolio_df = pd.DataFrame(self.portfolio_value)
        portfolio_df.set_index('timestamp', inplace=True)
        
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                          subplot_titles=('Portfolio Value', 'Drawdown'),
                          row_heights=[0.7, 0.3])
        
        # Portfolio value
        fig.add_trace(
            go.Scatter(x=portfolio_df.index, y=portfolio_df['value'],
                      name='Portfolio Value',
                      line=dict(color='rgb(49,130,189)')),
            row=1, col=1
        )
        
        # Drawdown
        portfolio_df['cummax'] = portfolio_df['value'].cummax()
        portfolio_df['drawdown'] = (portfolio_df['cummax'] - portfolio_df['value']) / portfolio_df['cummax'] * 100
        
        fig.add_trace(
            go.Scatter(x=portfolio_df.index, y=portfolio_df['drawdown'],
                      name='Drawdown',
                      line=dict(color='rgb(204,0,0)')),
            row=2, col=1
        )
        
        # Add trade markers
        for trade in self.trades:
            marker_color = 'green' if trade['type'] == 'ENTRY' else 'red'
            marker_symbol = 'triangle-up' if trade['type'] == 'ENTRY' else 'triangle-down'
            
            fig.add_trace(
                go.Scatter(x=[trade['time']], y=[trade['price']],
                          mode='markers',
                          name=trade['type'],
                          marker=dict(color=marker_color, size=10, symbol=marker_symbol)),
                row=1, col=1
            )
        
        fig.update_layout(height=800, showlegend=True,
                         template='plotly_dark',
                         title=f"Backtest Results - {self.strategy.name}")
        
        return fig
