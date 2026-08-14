from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_yaml_config(config_path: str) -> dict:
    """
    Load a YAML configuration file relative to the CLAF project root.

    Parameters
    ----------
    config_path : str
        Relative path to the YAML configuration file.

    Returns
    -------
    dict
        Parsed YAML configuration.

    Raises
    ------
    FileNotFoundError
        If the configuration file does not exist.

    ValueError
        If the YAML file is empty.
    """

    path = PROJECT_ROOT / config_path

    if not path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {path}"
        )

    with path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    if config is None:
        raise ValueError(
            f"Configuration file is empty: {path}"
        )

    return config