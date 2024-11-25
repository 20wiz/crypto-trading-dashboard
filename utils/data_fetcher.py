import ccxt
import pandas as pd
from datetime import datetime, timedelta

def get_historical_data(exchange_name: str, symbol: str, timeframe: str, limit: int = 1000) -> pd.DataFrame:
    """
    Fetch historical OHLCV data from the specified exchange
    """
    try:

        exchange = getattr(ccxt, exchange_name)()
        
        # Fetch OHLCV data
        ohlcv = exchange.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit
        )
        
        # Convert to DataFrame
        df = pd.DataFrame(
            ohlcv,
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        return df
        
    except Exception as e:
        raise Exception(f"Error fetching data: {str(e)}")
