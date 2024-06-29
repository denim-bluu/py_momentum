from typing import Protocol
import pandas as pd


class RankingCriteria(Protocol):
    def apply(self, df: pd.DataFrame) -> bool:
        raise NotImplementedError
