import os
from typing import Dict

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import StockData


def store_data(data: Dict[str, pd.DataFrame], **kwargs) -> None:
    engine = create_engine(os.environ["DATABASE_URL"])
    Session = sessionmaker(bind=engine)
    session = Session()

    for ticker, df in data.items():
        for index, row in df.iterrows():
            stock_data = StockData(
                ticker=ticker,
                date=index.date(),  # type: ignore
                open=row["Open"],
                high=row["High"],
                low=row["Low"],
                close=row["Close"],
                volume=row["Volume"],
                adj_close=row["Adj Close"],
                ma_100=row["MA_100"],
                atr_20=row["ATR_20"],
            )
            session.merge(stock_data)

    session.commit()
    session.close()
