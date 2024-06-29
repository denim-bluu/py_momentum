from typing import Protocol
import pandas as pd


class Metric(Protocol):
    def calculate(self, df: pd.DataFrame) -> float:
        raise NotImplementedError

    def get_name(self) -> str:
        raise NotImplementedError
