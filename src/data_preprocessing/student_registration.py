from pathlib import Path
from typing import Any
import logging

import pandas as pd


logger = logging.getLogger(__name__)


def preprocess_student_registration(
    source_path: Path,
    rules: dict[str, Any]
) -> pd.DataFrame:
    """
    Preprocess the OULAD studentRegistration dataset according
    to configured CLAF preprocessing rules.
    """

    dataframe = pd.read_csv(source_path)

    logger.info(
        "Starting preprocessing for studentRegistration with %s rows",
        len(dataframe)
    )

    # ---------------------------------------------------------
    # 1. Validate expected columns
    # ---------------------------------------------------------

    required_columns = rules.get(
        "required_columns",
        []
    )

    nullable_columns = rules.get(
        "nullable_columns",
        []
    )

    expected_columns = set(
        required_columns + nullable_columns
    )

    missing_columns = sorted(
        expected_columns - set(dataframe.columns)
    )

    if missing_columns:
        raise ValueError(
            "Missing expected columns in studentRegistration dataset: "
            f"{missing_columns}"
        )

    # ---------------------------------------------------------
    # 2. Enforce configured data types
    # ---------------------------------------------------------

    data_types = rules.get(
        "data_types",
        {}
    )

    for column, dtype in data_types.items():
        dataframe[column] = dataframe[column].astype(
            dtype
        )

    logger.info(
        "Data-type validation completed for studentRegistration"
    )

    # ---------------------------------------------------------
    # 3. Validate duplicate rules
    # ---------------------------------------------------------

    duplicate_rule = rules.get(
        "duplicate_rule",
        {}
    )

    if duplicate_rule.get("type") == "composite_key":

        key_columns = duplicate_rule.get(
            "columns",
            []
        )

        if not key_columns:
            raise ValueError(
                "Composite-key duplicate rule does not define any columns"
            )

        duplicate_mask = dataframe.duplicated(
            subset=key_columns,
            keep=False
        )

        if duplicate_mask.any():
            raise ValueError(
                "Duplicate composite-key records found for columns "
                f"{key_columns}"
            )

        logger.info(
            "Composite-key validation passed for %s",
            key_columns
        )

    # ---------------------------------------------------------
    # 4. Complete preprocessing
    # ---------------------------------------------------------

    logger.info(
        "Completed preprocessing for studentRegistration with %s rows",
        len(dataframe)
    )

    return dataframe



def write_clean_student_registration(
    dataframe: pd.DataFrame,
    output_path: Path
) -> None:
    """
    Write the cleaned studentRegistration dataset to Parquet.
    """

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    dataframe.to_parquet(
        output_path,
        index=False
    )

    logger.info(
        "Clean studentRegistration dataset written to %s with %s rows",
        output_path,
        len(dataframe)
    )