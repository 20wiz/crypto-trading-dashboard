import pandas as pd
import numpy as np
from typing import List, Dict
from .base import BaseStrategy

class CombinedStrategy(BaseStrategy):
    def __init__(self, strategies: List[BaseStrategy], combination_method: str = 'AND'):
        """
        Initialize combined strategy
        
        Args:
            strategies: List of strategy instances to combine
            combination_method: 'AND' (all strategies must agree) or 'OR' (any strategy can trigger)
        """
        super().__init__()
        self.name = "Combined Strategy"
        self.validate_parameters(strategies, combination_method)
        self.strategies = strategies
        self.combination_method = combination_method.upper()
    
    def validate_parameters(self, strategies, combination_method):
        if not strategies or len(strategies) < 2:
            raise ValueError("At least two strategies are required")
        if combination_method.upper() not in ['AND', 'OR']:
            raise ValueError("Combination method must be 'AND' or 'OR'")
    
    def generate_signals(self, data: pd.DataFrame) -> list:
        # Get signals from all strategies
        strategy_signals = []
        for strategy in self.strategies:
            signals = strategy.generate_signals(data)
            strategy_signals.append({signal['timestamp']: signal for signal in signals})
        
        combined_signals = []
        all_timestamps = sorted(set().union(*(s.keys() for s in strategy_signals)))
        
        for timestamp in all_timestamps:
            signals_at_timestamp = []
            
            # Check signals from each strategy at this timestamp
            for strat_signals in strategy_signals:
                if timestamp in strat_signals:
                    signals_at_timestamp.append(strat_signals[timestamp])
            
            if not signals_at_timestamp:
                continue
                
            # Apply combination logic
            if self.combination_method == 'AND':
                # All strategies must agree on the action
                if len(signals_at_timestamp) == len(self.strategies):
                    actions = set(s['action'] for s in signals_at_timestamp)
                    if len(actions) == 1:  # All strategies agree
                        signal = signals_at_timestamp[0].copy()
                        signal['indicator'] = ' | '.join(s['indicator'] for s in signals_at_timestamp)
                        combined_signals.append(signal)
            else:  # 'OR'
                # Take the first signal at this timestamp
                signal = signals_at_timestamp[0].copy()
                signal['indicator'] = ' | '.join(s['indicator'] for s in signals_at_timestamp)
                combined_signals.append(signal)
        
        return combined_signals
    
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
