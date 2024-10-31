from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    def __init__(self):
        self.name = "Base Strategy"
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> list:
        pass
    
    @abstractmethod
    def calculate_metrics(self, data: pd.DataFrame) -> dict:
        pass
