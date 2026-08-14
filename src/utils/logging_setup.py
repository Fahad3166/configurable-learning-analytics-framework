from pathlib import Path
import logging.config

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def setup_logging(
    config_path: str = "configs/logging.yaml"
) -> None:
    """
    Configure CLAF logging using a YAML configuration file.

    Parameters
    ----------
    config_path : str
        Path to the logging configuration relative to
        the CLAF project root.
    """

    path = PROJECT_ROOT / config_path

    if not path.exists():
        raise FileNotFoundError(
            f"Logging configuration not found: {path}"
        )

    with path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    if config is None:
        raise ValueError(
            f"Logging configuration is empty: {path}"
        )

    # Ensure the parent directory for file-based logs exists.
    for handler in config.get("handlers", {}).values():
        filename = handler.get("filename")

        if filename:
            log_path = PROJECT_ROOT / filename
            log_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            # Convert the relative YAML path to an absolute path.
            handler["filename"] = str(log_path)

    logging.config.dictConfig(config)