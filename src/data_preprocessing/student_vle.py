from pathlib import Path
from typing import Any
import logging

import pandas as pd


logger = logging.getLogger(__name__)


def preprocess_student_vle(
    source_path: Path,
    rules: dict[str, Any]
) -> pd.DataFrame:
    """
    Preprocess the OULAD studentVle dataset according
    to configured CLAF preprocessing rules.
    """

    dataframe = pd.read_csv(source_path)

    logger.info(
        "Starting preprocessing for studentVle with %s rows",
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
            "Missing expected columns in studentVle dataset: "
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
        "Data-type validation completed for studentVle"
    )

    # ---------------------------------------------------------
    # 3. Validate numeric rules
    # ---------------------------------------------------------

    numeric_rules = rules.get(
        "numeric_rules",
        {}
    )

    for column, rule in numeric_rules.items():

        if "min" in rule:
            invalid_min = dataframe[column] < rule["min"]

            if invalid_min.any():
                raise ValueError(
                    f"Values below minimum in {column}: "
                    f"{dataframe.loc[invalid_min, column].unique().tolist()}"
                )

        if "max" in rule:
            invalid_max = dataframe[column] > rule["max"]

            if invalid_max.any():
                raise ValueError(
                    f"Values above maximum in {column}: "
                    f"{dataframe.loc[invalid_max, column].unique().tolist()}"
                )

    logger.info(
        "Numeric validation passed for %s columns",
        len(numeric_rules)
    )

    # ---------------------------------------------------------
    # 4. Apply duplicate policy
    # ---------------------------------------------------------

    duplicate_rule = rules.get(
        "duplicate_rule",
        {}
    )

    if duplicate_rule.get("type") == "preserve":
        logger.info(
            "Duplicate preservation rule applied for studentVle; "
            "source observations are retained"
        )

    # ---------------------------------------------------------
    # 5. Complete preprocessing
    # ---------------------------------------------------------

    logger.info(
        "Completed preprocessing for studentVle with %s rows",
        len(dataframe)
    )

    return dataframe



def write_clean_student_vle(
    dataframe: pd.DataFrame,
    output_path: Path
) -> None:
    """
    Write the cleaned studentVle dataset to Parquet.
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
        "Clean studentVle dataset written to %s with %s rows",
        output_path,
        len(dataframe)
    )