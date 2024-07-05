from typing import Dict

import pandas as pd
from great_expectations.dataset import PandasDataset


def validate_data(data: Dict[str, pd.DataFrame], **kwargs) -> None:
    for ticker, df in data.items():
        dataset = PandasDataset(df)
        dataset.expect_column_values_to_not_be_null("Adj Close")
        dataset.expect_column_values_to_be_between("Volume", 0, 1e10)
        validation_result = dataset.validate()
        if not validation_result["success"]:
            raise ValueError(f"Data validation failed for {ticker}")
