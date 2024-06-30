# config_utils.py
from typing import Any, Dict

import yaml


def load_config(config_file: str = "config.yaml") -> Dict[str, Any]:
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)

    # Add derived configurations
    config["max_lookback_days"] = max(
        config["strategy"]["momentum_window"],
        config["strategy"]["ma_window"],
        config["strategy"]["long_trend_window"],  # for MA200
    )

    config["indicator_configs"] = {
        "MA100": {"window": config["strategy"]["ma_window"]},
        "MA200": {"window": config["strategy"]["long_trend_window"]},
        "ATR": {"window": config["strategy"]["atr_window"]},
        "Momentum": {"window": config["strategy"]["momentum_window"]},
    }

    return config
