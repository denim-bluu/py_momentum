import os
from abc import ABC, abstractmethod

import pandas as pd


class DataSaver(ABC):
    @abstractmethod
    def save(self, ticker: str, data: pd.DataFrame, directory: str) -> None:
        pass


class CSVSaver(DataSaver):
    def save(self, ticker: str, data: pd.DataFrame, directory: str) -> None:
        os.makedirs(directory, exist_ok=True)
        data.to_csv(os.path.join(directory, f"{ticker}.csv"))
