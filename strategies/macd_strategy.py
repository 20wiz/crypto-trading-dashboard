import pandas as pd
import numpy as np
from .base import BaseStrategy

class MACDStrategy(BaseStrategy):
    def __init__(self, fast_period=12, slow_period=26, signal_period=9, histogram_threshold=0):
        super().__init__()
        self.name = "MACD"
        self.validate_parameters(fast_period, slow_period, signal_period, histogram_threshold)
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        self.histogram_threshold = histogram_threshold
    
    def validate_parameters(self, fast_period, slow_period, signal_period, histogram_threshold):
        if not all(isinstance(x, int) for x in [fast_period, slow_period, signal_period]):
            raise ValueError("Periods must be integers")
        if not all(x > 0 for x in [fast_period, slow_period, signal_period]):
            raise ValueError("Periods must be positive")
        if fast_period >= slow_period:
            raise ValueError("Fast period must be less than slow period")
        if not isinstance(histogram_threshold, (int, float)):
            raise ValueError("Histogram threshold must be a number")
    
    def calculate_macd(self, data: pd.DataFrame) -> tuple:
        # Calculate exponential moving averages
        ema_fast = data['close'].ewm(span=self.fast_period, adjust=False).mean()
        ema_slow = data['close'].ewm(span=self.slow_period, adjust=False).mean()
        
        # Calculate MACD line and signal line
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=self.signal_period, adjust=False).mean()
        
        # Calculate MACD histogram
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def generate_signals(self, data: pd.DataFrame) -> list:
        df = data.copy()
        
        # Calculate MACD components
        macd_line, signal_line, histogram = self.calculate_macd(df)
        df['MACD'] = macd_line
        df['Signal'] = signal_line
        df['Histogram'] = histogram
        
        signals = []
        position_open = False
        
        for i in range(1, len(df)):
            if pd.isna(df['MACD'].iloc[i]) or pd.isna(df['Signal'].iloc[i]):
                continue
                
            current_price = df['close'].iloc[i]
            current_time = df.index[i]
            prev_hist = df['Histogram'].iloc[i-1]
            curr_hist = df['Histogram'].iloc[i]
            
            # Entry conditions
            if not position_open:
                # Bullish crossing with histogram threshold
                if (prev_hist < -self.histogram_threshold and 
                    curr_hist >= -self.histogram_threshold and 
                    df['MACD'].iloc[i] > df['Signal'].iloc[i]):
                    signals.append({
                        'timestamp': current_time,
                        'price': current_price,
                        'action': 'BUY',
                        'indicator': f"MACD: {df['MACD'].iloc[i]:.2f}, Signal: {df['Signal'].iloc[i]:.2f}, Hist: {curr_hist:.2f}"
                    })
                    position_open = True
            else:
                # Exit conditions
                # Bearish crossing with histogram threshold
                if (prev_hist > self.histogram_threshold and 
                    curr_hist <= self.histogram_threshold and 
                    df['MACD'].iloc[i] < df['Signal'].iloc[i]):
                    signals.append({
                        'timestamp': current_time,
                        'price': current_price,
                        'action': 'SELL',
                        'indicator': f"MACD: {df['MACD'].iloc[i]:.2f}, Signal: {df['Signal'].iloc[i]:.2f}, Hist: {curr_hist:.2f}"
                    })
                    position_open = False
        
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
