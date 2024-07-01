from typing import Dict, List, Tuple

import pandas as pd


def get_trading_dates(
    stock_data: Dict[str, pd.DataFrame],
    index_data: pd.DataFrame,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
) -> List[pd.Timestamp]:
    all_dates = set()
    for df in stock_data.values():
        all_dates.update(df.index)
    all_dates.update(index_data.index)

    trading_dates = sorted(
        [date for date in all_dates if start_date <= date <= end_date]
    )

    if not trading_dates:
        raise ValueError("No trading dates found in the specified date range")

    return trading_dates


def filter_data_to_dates(data: pd.DataFrame, dates: List[pd.Timestamp]) -> pd.DataFrame:
    return data.loc[data.index.isin(dates)]


def align_data(
    stock_data: Dict[str, pd.DataFrame],
    index_data: pd.DataFrame,
    dates: List[pd.Timestamp],
) -> Tuple[Dict[str, pd.DataFrame], pd.DataFrame]:
    aligned_stock_data = {
        ticker: filter_data_to_dates(df, dates) for ticker, df in stock_data.items()
    }
    aligned_index_data = filter_data_to_dates(index_data, dates)
    return aligned_stock_data, aligned_index_data
