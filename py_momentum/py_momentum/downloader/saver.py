import pandas as pd
import os
from abc import ABC, abstractmethod

class DataSaver(ABC):
    @abstractmethod
    def save(self, ticker: str, df: pd.DataFrame):
        pass

class CSVSaver(DataSaver):
    def __init__(self, save_dir: str):
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)

    def save(self, ticker: str, df: pd.DataFrame):
        file_path = os.path.join(self.save_dir, f"{ticker}.csv")
        df.to_csv(file_path)