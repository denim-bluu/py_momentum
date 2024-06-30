# trade_logger.py
import pandas as pd
from loguru import logger


class TradeLogger:
    def __init__(self):
        self.trades = []

    def log_trade(self, date, ticker, action, shares, price, costs):
        trade = {
            "date": date,
            "ticker": ticker,
            "action": action,
            "shares": shares,
            "price": price,
            "costs": costs,
            "total": shares * price + costs,
        }
        self.trades.append(trade)
        logger.info(
            f"Trade: {date} - {action} {shares} shares of {ticker} at {price:.2f}, costs: {costs:.2f}"
        )

    def get_trade_history(self):
        return pd.DataFrame(self.trades)

    def save_trade_history(self, filename):
        df = self.get_trade_history()
        df.to_csv(filename, index=False)
        logger.info(f"Trade history saved to {filename}")
