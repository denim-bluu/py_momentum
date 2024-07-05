from dagster import Definitions, EnvVar
from dagster import define_asset_job
from py_momentum.dagster.assets.stock_data import (
    snp500_symbols,
    stock_data,
    processed_stock_data,
    store_stock_data,
)


from py_momentum.dagster.resources.database import DatabaseResource


stock_data_job = define_asset_job(
    "stock_data_job",
    selection=[snp500_symbols, stock_data, processed_stock_data, store_stock_data],
)

defs = Definitions(
    assets=[snp500_symbols, stock_data, processed_stock_data, store_stock_data],
    resources={"database": DatabaseResource(connection_string=EnvVar("DATABASE_URL"))},
    jobs=[stock_data_job],
)
