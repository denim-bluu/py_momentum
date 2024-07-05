from typing import List
from dagster import AssetIn, asset, AssetExecutionContext, Config
import pandas as pd
import yfinance as yf
from py_momentum.dagster.utils.calculations import calculate_atr
from dagster import Output, MetadataValue
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger


class StockDataConfig(Config):
    start_date: str
    end_date: str


@asset
def snp500_symbols(context: AssetExecutionContext) -> List[str]:
    symbols = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[
        0
    ]["Symbol"].tolist()
    context.log.info(f"Found {len(symbols)} S&P 500 symbols")
    return symbols


@asset(ins={"tickers": AssetIn("snp500_symbols")})
def stock_data(tickers: List[str], config: StockDataConfig) -> dict[str, pd.DataFrame]:
    data = {}
    for ticker in tickers:
        df = yf.download(ticker, start=config.start_date, end=config.end_date)
        if not df.empty:
            data[ticker] = df
        logger.info(f"Downloaded {len(df)} rows for {ticker}")
    return data


@asset(ins={"raw_data": AssetIn("stock_data")})
def processed_stock_data(raw_data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    processed_data = {}
    for ticker, df in raw_data.items():
        df["MA100"] = df["Close"].rolling(window=100).mean()
        df["ATR20"] = calculate_atr(df, window=20)
        processed_data[ticker] = df
    return processed_data


@asset(
    ins={"processed_data": AssetIn("processed_stock_data")},
    required_resource_keys={"database"},
)
def store_stock_data(context, processed_data: dict[str, pd.DataFrame]):
    engine = context.resources.database.get_engine()
    metadata = {}

    for ticker, df in processed_data.items():
        table_name = f"{ticker.upper().replace('.', '_')}"
        try:
            df.to_sql(table_name, engine, if_exists="replace", index=True)
            metadata[f"{ticker}_rows"] = len(df)
            metadata[f"{ticker}_table"] = MetadataValue.text(table_name)
        except SQLAlchemyError as e:
            context.log.error(f"Error storing data for {ticker}: {str(e)}")

    total_rows = sum(len(df) for df in processed_data.values())
    context.log.info(
        f"Stored {total_rows} rows for {len(processed_data)} tickers in separate tables."
    )

    return Output(
        value=None,
        metadata={
            "total_tickers": len(processed_data),
            "total_rows": total_rows,
            **metadata,
        },
    )
