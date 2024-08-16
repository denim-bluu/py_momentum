from datetime import date

import pytest

from app.strategy.models import (
    MarketRegime,
    SignalRequest,
    SignalResponse,
    SignalType,
    StockSignal,
    StrategyParameters,
)


def test_market_regime_enum():
    assert MarketRegime.BULL.value == "bull"
    assert MarketRegime.BEAR.value == "bear"
    assert MarketRegime.NEUTRAL.value == "neutral"


def test_order_signal_enum():
    assert SignalType.BUY.value == "BUY"
    assert SignalType.SELL.value == "SELL"


def test_stock_signal():
    stock_signal = StockSignal(
        symbol="AAPL",
        signal="BUY",
        risk_unit=0.1,
        momentum_score=1.5,
        current_price=150.0,
    )
    assert stock_signal.symbol == "AAPL"
    assert stock_signal.signal == "BUY"
    assert stock_signal.risk_unit == 0.1
    assert stock_signal.momentum_score == 1.5
    assert stock_signal.current_price == 150.0


def test_strategy_parameters():
    strategy_params = StrategyParameters(
        lookback_period=120,
        top_percentage=0.3,
        risk_factor=0.002,
        market_regime_period=250,
    )
    assert strategy_params.lookback_period == 120
    assert strategy_params.top_percentage == 0.3
    assert strategy_params.risk_factor == 0.002
    assert strategy_params.market_regime_period == 250


def test_signal_request():
    signal_request = SignalRequest(
        symbols=["AAPL", "GOOGL"],
        date=date(2023, 1, 1),
        interval="1d",
        market_index="SP500",
    )
    assert signal_request.symbols == ["AAPL", "GOOGL"]
    assert signal_request.date == date(2023, 1, 1)
    assert signal_request.interval == "1d"
    assert signal_request.market_index == "SP500"


def test_signal_response():
    stock_signal = StockSignal(
        symbol="AAPL",
        signal="BUY",
        risk_unit=0.1,
        momentum_score=1.5,
        current_price=150.0,
    )
    signal_response = SignalResponse(signals=[stock_signal])
    assert len(signal_response.signals) == 1
    assert signal_response.signals[0].symbol == "AAPL"
    assert signal_response.signals[0].signal == "BUY"
    assert signal_response.signals[0].risk_unit == 0.1
    assert signal_response.signals[0].momentum_score == 1.5
    assert signal_response.signals[0].current_price == 150.0


if __name__ == "__main__":
    pytest.main()
