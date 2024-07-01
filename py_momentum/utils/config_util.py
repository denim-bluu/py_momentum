from typing import Any, Dict
import yaml
import os


def load_config(config_file: str = "config/config.yaml") -> Dict[str, Any]:
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)

    # Validate required sections
    required_sections = [
        "backtesting",
        "data",
        "index",
        "output",
        "strategy",
        "transaction_costs",
        "indicator_configs",
        "download",
    ]
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required section in config: {section}")

    # Ensure paths are absolute
    config["data"]["raw_data_dir"] = os.path.abspath(config["data"]["raw_data_dir"])
    config["data"]["processed_data_dir"] = os.path.abspath(
        config["data"]["processed_data_dir"]
    )
    config["output"]["dir"] = os.path.abspath(config["output"]["dir"])
    config["output"]["log_file"] = os.path.abspath(config["output"]["log_file"])

    # Ensure directories exist
    os.makedirs(config["data"]["raw_data_dir"], exist_ok=True)
    os.makedirs(config["data"]["processed_data_dir"], exist_ok=True)
    os.makedirs(config["output"]["dir"], exist_ok=True)
    os.makedirs(os.path.dirname(config["output"]["log_file"]), exist_ok=True)

    # Validate and set default values
    config["download"]["concurrent_limit"] = config["download"].get(
        "concurrent_limit", 5
    )
    config["download"]["rate_limit"] = config["download"].get("rate_limit", 30)

    # Calculate max_lookback_days if not provided
    if "max_lookback_days" not in config:
        config["max_lookback_days"] = max(
            config["strategy"]["ranking_strategy"]["momentum_window"],
            config["strategy"]["ranking_strategy"]["ma_window"],
            config["strategy"]["market_filter"]["ma_window"],
            config["indicator_configs"]["MA200"]["window"],
            252,  # Ensure at least a year of data
        )

    # Validate strategy configurations
    strategy_types = {
        "ranking_strategy": ["momentum"],
        "position_sizer": ["fixed_risk"],
        "market_filter": ["moving_average"],
        "rebalance_strategy": ["threshold"],
    }

    for strategy, allowed_types in strategy_types.items():
        if config["strategy"][strategy]["type"] not in allowed_types:
            raise ValueError(
                f"Invalid {strategy} type. Allowed types are: {', '.join(allowed_types)}"
            )

    return config
