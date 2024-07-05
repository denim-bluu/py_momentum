from typing import Protocol


class PositionSizer(Protocol):
    def calculate_position_size(self, *args, **kwargs) -> float: ...
