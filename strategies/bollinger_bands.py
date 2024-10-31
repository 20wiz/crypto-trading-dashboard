import pandas as pd
import numpy as np
from .base import BaseStrategy

class BollingerBandsStrategy(BaseStrategy):
    def __init__(self, period=20, std_dev=2.0, use_atr_exits=True, atr_period=14, atr_multiplier=2.0):
        super().__init__()
        self.name = "Bollinger Bands"
        self.validate_parameters(period, std_dev, atr_period, atr_multiplier)
        self.period = period
        self.std_dev = std_dev
        self.use_atr_exits = use_atr_exits
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier
    
    def validate_parameters(self, period, std_dev, atr_period, atr_multiplier):
        if not isinstance(period, int) or not isinstance(atr_period, int):
            raise ValueError("Periods must be integers")
        if period <= 0 or atr_period <= 0:
            raise ValueError("Periods must be positive")
        if std_dev <= 0 or atr_multiplier <= 0:
            raise ValueError("Multipliers must be positive")
    
    def calculate_atr(self, data: pd.DataFrame) -> pd.Series:
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift())
        low_close = np.abs(data['low'] - data['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        return true_range.rolling(window=self.atr_period).mean()
    
    def generate_signals(self, data: pd.DataFrame) -> list:
        df = data.copy()
        
        # Calculate Bollinger Bands
        df['SMA'] = df['close'].rolling(window=self.period).mean()
        df['STD'] = df['close'].rolling(window=self.period).std()
        df['Upper'] = df['SMA'] + (df['STD'] * self.std_dev)
        df['Lower'] = df['SMA'] - (df['STD'] * self.std_dev)
        
        # Calculate ATR for dynamic exits if enabled
        if self.use_atr_exits:
            df['ATR'] = self.calculate_atr(df)
        
        # Generate signals
        signals = []
        position_open = False
        stop_loss = None
        
        for i in range(len(df)):
            if pd.isna(df['Upper'].iloc[i]) or pd.isna(df['Lower'].iloc[i]):
                continue
                
            current_price = df['close'].iloc[i]
            current_time = df.index[i]
            
            if not position_open:
                # Entry conditions
                if current_price < df['Lower'].iloc[i]:
                    stop_loss = current_price - (df['ATR'].iloc[i] * self.atr_multiplier) if self.use_atr_exits else None
                    signals.append({
                        'timestamp': current_time,
                        'price': current_price,
                        'action': 'BUY',
                        'indicator': f"BB Lower: {df['Lower'].iloc[i]:.2f}, ATR: {df['ATR'].iloc[i]:.2f}" if self.use_atr_exits else f"BB Lower: {df['Lower'].iloc[i]:.2f}"
                    })
                    position_open = True
            else:
                # Exit conditions
                exit_signal = False
                exit_reason = ""
                
                if current_price > df['Upper'].iloc[i]:
                    exit_signal = True
                    exit_reason = "Upper Band"
                elif self.use_atr_exits and stop_loss is not None and current_price < stop_loss:
                    exit_signal = True
                    exit_reason = "Stop Loss"
                
                if exit_signal:
                    signals.append({
                        'timestamp': current_time,
                        'price': current_price,
                        'action': 'SELL',
                        'indicator': f"Exit - {exit_reason}"
                    })
                    position_open = False
                    stop_loss = None
        
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
