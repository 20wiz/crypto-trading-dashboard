import pandas as pd
import numpy as np
from .base import BaseStrategy

class RSIStrategy(BaseStrategy):
    def __init__(self, period=14, overbought=70, oversold=30):
        super().__init__()
        self.name = "RSI Strategy"
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
    
    def calculate_rsi(self, data: pd.DataFrame) -> pd.Series:
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def generate_signals(self, data: pd.DataFrame) -> list:
        df = data.copy()
        df['RSI'] = self.calculate_rsi(df)
        
        # Generate signals
        df['signal'] = 0
        df.loc[df['RSI'] < self.oversold, 'signal'] = 1
        df.loc[df['RSI'] > self.overbought, 'signal'] = -1
        
        signals = []
        df['signal_change'] = df['signal'].diff()
        
        for idx, row in df[df['signal_change'] != 0].iterrows():
            signals.append({
                'timestamp': idx,
                'price': row['close'],
                'action': 'BUY' if row['signal'] == 1 else 'SELL',
                'indicator': f"RSI: {row['RSI']:.2f}"
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
