## Overview of the System

This project is a Python-based algorithmic trading system designed to facilitate the development, backtesting, and execution of trading strategies. The system is modular and extensible, allowing for easy integration of new strategies and data sources.

## Project Structure

1. Data Service ✅:
   - Fetch and store historical and real-time market data
   - Provide data to other services via API
   - Calculate and store common technical indicators
   - Manage data caching for improved performance
2. Strategy Service ✅:
   - Implement and manage multiple trading strategies
   - Generate trading signals based on market data and configured strategies
   - Provide risk calculations for potential trades
   - Allow dynamic configuration of strategy parameters
3. Portfolio Service 🚧:
   - Receive signals from the Strategy Service
   - Determine desired portfolio state based on signals and current market conditions
   - Implement rebalancing logic and scheduling
   - Generate trade orders to align actual portfolio with desired state
   - Implement portfolio-level risk management rules
   - Manage cash allocations within the portfolio
   - Provide APIs for querying desired portfolio state and manually triggering rebalances
4. Trade Execution Service 🚧:
   - Receive and execute trade orders from the Portfolio Service
   - Interact with broker APIs or simulate trades in backtest mode
   - Track status of submitted orders (pending, filled, partially filled, cancelled)
   - Provide real-time updates on order status
   - Implement smart order routing and execution algorithms
   - Handle order types relevant to the trading strategies (e.g., market, limit, stop orders)
5. Portfolio State Service 🚧:
   - Maintain the actual, settled portfolio state
   - Reconcile desired state (from Portfolio Service) with executed trades (from Trade Execution Service)
   - Track actual positions, cash balance, and transaction history
   - Calculate and store portfolio performance metrics
   - Handle corporate actions (e.g., dividends, splits)
   - Provide APIs for querying current portfolio state and historical performance
6. Backtesting Service 🚧:
   - Coordinate with other services to simulate historical trading
   - Fetch historical data from Data Service
   - Generate historical signals using Strategy Service
   - Simulate portfolio management using Portfolio Service
   - Simulate trade execution using Trade Execution Service in backtest mode
   - Track simulated portfolio state using Portfolio State Service
   - Calculate and report backtesting performance metrics
   - Provide tools for strategy optimization and parameter tunin  g

```mermaid
graph TD
    A[Data Service] --> B[Strategy Service]
    A --> C[Portfolio Service]
    A --> D[Trade Execution Service]
    A --> E[Portfolio State Service]
    A --> F[Backtesting Service]
    B --> C
    C --> D
    D --> E
    C -.-> E
    F --> A
    F --> B
    F --> C
    F --> D
    F --> E
```

## Configuration

Configuration settings for the application are managed using the `Config` class.

## Installation

To install the required dependencies, run:

```sh
pdm install
```

## Running the Application

To start the application, execute:

```sh
python py_momentum/app/main.py
```

## Testing

To run the tests, use:

```sh
pytest
```

## Dependencies

The project relies on several key dependencies, including but not limited to:

- `yfinance`
- `pandas`
- `fastapi`
- `sqlalchemy`
- `pytest`

For a complete list of dependencies, refer to the [pyproject.toml](pyproject.toml) and [pdm.lock](pdm.lock) files.

## Authors

- Joon Kang - [denim.bluu@gmail.com](mailto:denim.bluu@gmail.com)
``
