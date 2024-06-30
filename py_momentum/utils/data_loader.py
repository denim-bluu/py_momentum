import os
from typing import Dict

import pandas as pd


def load_stock_data(directory: str) -> Dict[str, pd.DataFrame]:
    stock_data = {}
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            ticker = filename[:-4]
            df = pd.read_csv(
                os.path.join(directory, filename),
                parse_dates=["Date"],
                index_col="Date",
            )
            stock_data[ticker] = df
    return stock_data
