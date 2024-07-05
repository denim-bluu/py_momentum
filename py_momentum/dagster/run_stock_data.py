from dagster import materialize
from py_momentum.dagster.assets.stock_data import StockDataConfig
from py_momentum.dagster.assets.stock_data import (
    snp500_symbols,
    stock_data,
    processed_stock_data,
    store_stock_data,
)

from py_momentum.dagster.resources.database import DatabaseResource

config = StockDataConfig(start_date="2020-01-01", end_date="2023-06-01")


def run_stock_data_job(start_date, end_date):
    config = StockDataConfig(start_date=start_date, end_date=end_date)

    result = materialize(
        [snp500_symbols, stock_data, processed_stock_data, store_stock_data],
        run_config={"ops": {"stock_data": {"config": config.dict()}}},
        resources={
            "database": DatabaseResource(connection_string="sqlite:///stock_data.db")
        },
    )
    if result.success:
        print("Job completed successfully.")

    else:
        print("Job failed.")
    return result.success


if __name__ == "__main__":
    start_date = "2020-01-01"
    end_date = "2023-06-01"

    success = run_stock_data_job(start_date, end_date)
