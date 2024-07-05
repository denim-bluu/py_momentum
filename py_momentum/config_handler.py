from dataclasses import dataclass
from datetime import datetime
from typing import Any

import yaml


@dataclass
class DataConfig:
    start_date: datetime
    end_date: datetime
    index_symbol: str


@dataclass
class StrategyConfig:
    name: str
    lookback_period: int
    trend_ma_window: int


@dataclass
class PortfolioConfig:
    initial_capital: float
    risk_per_trade: float


@dataclass
class ExecutionConfig:
    commission_rate: float


@dataclass
class BacktestConfig:
    rebalance_frequency: int


@dataclass
class Config:
    data: DataConfig
    strategy: StrategyConfig
    portfolio: PortfolioConfig
    execution: ExecutionConfig
    backtest: BacktestConfig


def load_config(file_path: str) -> Config:
    with open(file_path, "r") as file:
        yaml_config = yaml.safe_load(file)

    data_config = DataConfig(
        start_date=datetime.strptime(yaml_config["data"]["start_date"], "%Y-%m-%d"),
        end_date=datetime.strptime(yaml_config["data"]["end_date"], "%Y-%m-%d"),
        index_symbol=yaml_config["data"]["index_symbol"],
    )

    strategy_config = StrategyConfig(**yaml_config["strategy"])
    portfolio_config = PortfolioConfig(**yaml_config["portfolio"])
    execution_config = ExecutionConfig(**yaml_config["execution"])
    backtest_config = BacktestConfig(**yaml_config["backtest"])

    return Config(
        data=data_config,
        strategy=strategy_config,
        portfolio=portfolio_config,
        execution=execution_config,
        backtest=backtest_config,
    )


def get_config_value(config: Config, key_path: str) -> Any:
    keys = key_path.split(".")
    value = config
    for key in keys:
        value = getattr(value, key)
    return value
