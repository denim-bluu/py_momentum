import asyncio
import os

import click
import pandas as pd

from py_momentum.data.fetchers import CSVFetcher
from py_momentum.data.pipeline import DataPipeline
from py_momentum.data.processors import ATRProcessor, MovingAverageProcessor
from py_momentum.data.savers import CSVSaver
from py_momentum.utils.config_util import load_config


def create_default_pipeline(config: dict) -> DataPipeline:
    fetcher = CSVFetcher(config["data"]["raw_data_dir"])
    processors = [
        MovingAverageProcessor(config["indicator_configs"]["MA100"]["window"]),
        MovingAverageProcessor(config["indicator_configs"]["MA200"]["window"]),
        ATRProcessor(config["indicator_configs"]["ATR"]["window"]),
    ]
    saver = CSVSaver()
    return DataPipeline(fetcher, processors, saver)


@click.command()
@click.option("--config", default="config.yaml", help="Path to configuration file")
@click.option(
    "--tickers",
    "-t",
    help="Comma-separated list of stock tickers to process",
)
def process_data(config: str, tickers: str):
    config_data = load_config(config)
    input_dir = config_data["data"]["raw_data_dir"]
    output_dir = config_data["data"]["processed_data_dir"]
    
    if tickers:
        ticker_list = [t.strip() for t in tickers.split(",")]
    else:
        ticker_list = [f[:-4] for f in os.listdir(input_dir) if f.endswith(".csv")]

    pipeline = create_default_pipeline(config_data)

    start_date = pd.Timestamp(config_data["backtesting"]["start_date"])
    end_date = pd.Timestamp(config_data["backtesting"]["end_date"])
    adjusted_start_date = start_date - pd.Timedelta(
        days=config_data["max_lookback_days"]
    )

    asyncio.run(pipeline.run(ticker_list, adjusted_start_date, end_date, output_dir))


if __name__ == "__main__":
    process_data()
