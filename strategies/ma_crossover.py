import pandas as pd
import numpy as np
from .base import BaseStrategy

class MACrossoverStrategy(BaseStrategy):
    def __init__(self, short_window=20, long_window=50):
        super().__init__()
        self.name = "MA Crossover"
        self.short_window = short_window
        self.long_window = long_window
    
    def generate_signals(self, data: pd.DataFrame) -> list:
        df = data.copy()
        
        # Calculate moving averages
        df['SMA_short'] = df['close'].rolling(window=self.short_window).mean()
        df['SMA_long'] = df['close'].rolling(window=self.long_window).mean()
        
        # Generate signals
        df['signal'] = 0
        df.loc[df['SMA_short'] > df['SMA_long'], 'signal'] = 1
        df.loc[df['SMA_short'] < df['SMA_long'], 'signal'] = -1
        
        # Get signal changes
        signals = []
        df['signal_change'] = df['signal'].diff()
        
        for idx, row in df[df['signal_change'] != 0].iterrows():
            signals.append({
                'timestamp': idx,
                'price': row['close'],
                'action': 'BUY' if row['signal'] == 1 else 'SELL',
                'indicator': f"Short MA: {row['SMA_short']:.2f}, Long MA: {row['SMA_long']:.2f}"
            })
            
        return signals
    
    def calculate_metrics(self, data: pd.DataFrame) -> dict:
        signals = self.generate_signals(data)
        if not signals:
            return {'total_returns': 0, 'win_rate': 0, 'avg_return': 0}
        
        returns = []
        position = None
        
        for i in range(len(signals)-1):
            if signals[i]['action'] == 'BUY':
                position = signals[i]['price']
            elif signals[i]['action'] == 'SELL' and position:
                returns.append((signals[i]['price'] - position) / position * 100)
                position = None
        
        return {
            'total_returns': sum(returns),
            'win_rate': len([r for r in returns if r > 0]) / len(returns) if returns else 0,
            'avg_return': np.mean(returns) if returns else 0
        }
