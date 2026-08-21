from pathlib import Path
from typing import Any
import logging

import pandas as pd


logger = logging.getLogger(__name__)


def preprocess_student_assessment(
    source_path: Path,
    rules: dict[str, Any]
) -> pd.DataFrame:
    """
    Preprocess the OULAD studentAssessment dataset according
    to configured CLAF preprocessing rules.
    """

    dataframe = pd.read_csv(source_path)

    logger.info(
        "Starting preprocessing for studentAssessment with %s rows",
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
            "Missing expected columns in studentAssessment dataset: "
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
        "Data-type validation completed for studentAssessment"
    )

    # ---------------------------------------------------------
    # 3. Validate categorical rules
    # ---------------------------------------------------------

    categorical_rules = rules.get(
        "categorical_rules",
        {}
    )

    for column, rule in categorical_rules.items():

        allowed_values = set(
            rule.get("allowed_values", [])
        )

        actual_values = set(
            dataframe[column]
            .dropna()
            .unique()
        )

        invalid_values = sorted(
            actual_values - allowed_values
        )

        if invalid_values:
            raise ValueError(
                f"Invalid categorical values in {column}: "
                f"{invalid_values}"
            )

    logger.info(
        "Categorical validation passed for %s columns",
        len(categorical_rules)
    )

    # ---------------------------------------------------------
    # 4. Validate numeric rules
    # ---------------------------------------------------------

    numeric_rules = rules.get(
        "numeric_rules",
        {}
    )

    for column, rule in numeric_rules.items():

        if "min" in rule:
            invalid_min = (
                dataframe[column].notna()
                & (dataframe[column] < rule["min"])
            )

            if invalid_min.any():
                raise ValueError(
                    f"Values below minimum in {column}: "
                    f"{dataframe.loc[invalid_min, column].unique().tolist()}"
                )

        if "max" in rule:
            invalid_max = (
                dataframe[column].notna()
                & (dataframe[column] > rule["max"])
            )

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
    # 5. Validate composite-key uniqueness
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
                "Duplicate student-assessment records found for columns "
                f"{key_columns}"
            )

        logger.info(
            "Composite-key validation passed for %s",
            key_columns
        )

    # ---------------------------------------------------------
    # 6. Complete preprocessing
    # ---------------------------------------------------------

    logger.info(
        "Completed preprocessing for studentAssessment with %s rows",
        len(dataframe)
    )

    return dataframe


def write_clean_student_assessment(
    dataframe: pd.DataFrame,
    output_path: Path
) -> None:
    """
    Write the cleaned studentAssessment dataset to Parquet.
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
        "Clean studentAssessment dataset written to %s with %s rows",
        output_path,
        len(dataframe)
    )