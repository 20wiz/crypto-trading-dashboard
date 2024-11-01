# Cryptocurrency Trading Dashboard

A real-time cryptocurrency trading dashboard with interactive charts, multiple strategies, and signal notifications built using Streamlit.

## Features

- Real-time cryptocurrency price charts
- Multiple trading strategies:
  - Moving Average Crossover
  - RSI (Relative Strength Index)
  - Bollinger Bands with ATR-based exits
  - MACD (Moving Average Convergence Divergence)
  - Strategy Combination capabilities
- Interactive backtesting functionality
- Performance metrics and signal notifications
- Customizable strategy parameters

## Setup Instructions

1. Clone the repository 

2. Dependencies 


## Usage

1. Select your desired configuration in the sidebar:
   - Exchange (Binance, Coinbase, Kraken)
   - Trading pair
   - Timeframe
   - Trading strategy

2. Customize strategy parameters:
   - Each strategy has its own set of configurable parameters
   - For combined strategies, select which strategies to include

3. View real-time data and signals in the "Live Trading" tab

4. Test strategies using the "Backtesting" tab:
   - Set initial capital
   - Choose backtest period
   - View performance metrics and trade history

## Project Structure

- `main.py`: Main application file
- `strategies/`: Trading strategy implementations
- `components/`: UI components and visualizations
- `utils/`: Utility functions for data fetching and backtesting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details
