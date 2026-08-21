from pathlib import Path
import json
from typing import Any

import pandas as pd


def validate_clean_table(
    file_path: Path,
    rules: dict[str, Any]
) -> dict[str, Any]:
    """
    Validate one clean-layer Parquet table against its configured rules.
    """

    dataframe = pd.read_parquet(file_path)

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

    # ---------------------------------------------------------
    # 2. Validate required-column nullability
    # ---------------------------------------------------------

    required_nulls = (
        int(
            dataframe[required_columns]
            .isna()
            .sum()
            .sum()
        )
        if required_columns
        else 0
    )

    # ---------------------------------------------------------
    # 3. Validate configured data types
    # ---------------------------------------------------------

    data_type_mismatches = [
        {
            "column": column,
            "actual": str(dataframe[column].dtype),
            "expected": expected_dtype
        }
        for column, expected_dtype in rules.get(
            "data_types",
            {}
        ).items()
        if str(dataframe[column].dtype) != expected_dtype
    ]

    # ---------------------------------------------------------
    # 4. Validate configured key uniqueness
    # ---------------------------------------------------------

    duplicate_rule = rules.get(
        "duplicate_rule",
        {}
    )

    duplicate_key_count = 0

    if duplicate_rule.get("type") in {
        "unique_key",
        "composite_key"
    }:
        key_columns = duplicate_rule.get(
            "columns",
            []
        )

        if not key_columns:
            duplicate_key_count = -1
        else:
            duplicate_key_count = int(
                dataframe.duplicated(
                    subset=key_columns
                ).sum()
            )

    # ---------------------------------------------------------
    # 5. Determine table validation status
    # ---------------------------------------------------------

    status = (
        "passed"
        if not missing_columns
        and required_nulls == 0
        and not data_type_mismatches
        and duplicate_key_count == 0
        else "failed"
    )

    return {
        "status": status,
        "row_count": len(dataframe),
        "missing_columns": missing_columns,
        "required_nulls": required_nulls,
        "data_type_mismatches": data_type_mismatches,
        "duplicate_key_count": duplicate_key_count
    }



def validate_reference_relationship(
    child_file: Path,
    parent_file: Path,
    child_columns: list[str],
    parent_columns: list[str]
) -> dict[str, Any]:
    """
    Validate that every child key has a corresponding parent key.
    """

    child = pd.read_parquet(
        child_file,
        columns=child_columns
    )

    parent = pd.read_parquet(
        parent_file,
        columns=parent_columns
    )

    child_keys = pd.MultiIndex.from_frame(
        child[child_columns]
    )

    parent_keys = pd.MultiIndex.from_frame(
        parent[parent_columns]
        .drop_duplicates()
    )

    invalid_mask = ~child_keys.isin(
        parent_keys
    )

    invalid_row_count = int(
        invalid_mask.sum()
    )

    status = (
        "passed"
        if invalid_row_count == 0
        else "failed"
    )

    return {
        "status": status,
        "child_row_count": len(child),
        "invalid_row_count": invalid_row_count
    }

def build_table_results(
    clean_dir: Path,
    config: dict[str, Any]
) -> dict[str, Any]:
    """
    Validate all clean-layer tables using their configured rules.
    """

    mapping = {
        "courses": "courses.parquet",
        "student_info": "student_info.parquet",
        "student_registration": "student_registration.parquet",
        "assessments": "assessments.parquet",
        "student_assessment": "student_assessment.parquet",
        "vle": "vle.parquet",
        "student_vle": "student_vle.parquet"
    }

    return {
        table_name: validate_clean_table(
            clean_dir / file_name,
            config[table_name]
        )
        for table_name, file_name in mapping.items()
    }



def build_relationship_results(
    clean_dir: Path
) -> dict[str, Any]:
    """
    Run the core clean-layer referential-integrity checks.
    """

    return {
        "student_info_to_courses": validate_reference_relationship(
            clean_dir / "student_info.parquet",
            clean_dir / "courses.parquet",
            ["code_module", "code_presentation"],
            ["code_module", "code_presentation"]
        ),

        "student_registration_to_student_info": (
            validate_reference_relationship(
                clean_dir / "student_registration.parquet",
                clean_dir / "student_info.parquet",
                [
                    "id_student",
                    "code_module",
                    "code_presentation"
                ],
                [
                    "id_student",
                    "code_module",
                    "code_presentation"
                ]
            )
        ),

        "student_assessment_to_assessments": (
            validate_reference_relationship(
                clean_dir / "student_assessment.parquet",
                clean_dir / "assessments.parquet",
                ["id_assessment"],
                ["id_assessment"]
            )
        ),

        "student_vle_to_vle": validate_reference_relationship(
            clean_dir / "student_vle.parquet",
            clean_dir / "vle.parquet",
            ["id_site"],
            ["id_site"]
        ),

        "student_vle_to_student_info": (
            validate_reference_relationship(
                clean_dir / "student_vle.parquet",
                clean_dir / "student_info.parquet",
                [
                    "id_student",
                    "code_module",
                    "code_presentation"
                ],
                [
                    "id_student",
                    "code_module",
                    "code_presentation"
                ]
            )
        )
    }


def build_clean_layer_validation_summary(
    table_results: dict[str, Any],
    relationship_results: dict[str, Any]
) -> dict[str, Any]:
    """
    Build a machine-readable summary of clean-layer validation results.
    """

    all_table_checks_passed = all(
        result.get("status") == "passed"
        for result in table_results.values()
    )

    all_relationship_checks_passed = all(
        result.get("status") == "passed"
        for result in relationship_results.values()
    )

    overall_status = (
        "passed"
        if all_table_checks_passed
        and all_relationship_checks_passed
        else "failed"
    )

    return {
        "overall_status": overall_status,
        "integration_ready": overall_status == "passed",
        "tables": table_results,
        "relationships": relationship_results
    }


def write_clean_layer_validation_summary(
    summary: dict[str, Any],
    output_path: Path
) -> None:
    """
    Write the clean-layer validation summary to JSON.
    """

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with output_path.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            summary,
            file,
            indent=2
        )


def run_clean_layer_validation(
    clean_dir: Path,
    config: dict[str, Any],
    output_path: Path
) -> dict[str, Any]:
    """
    Run the complete clean-layer validation workflow and persist its summary.
    """

    table_results = build_table_results(
        clean_dir,
        config
    )

    relationship_results = build_relationship_results(
        clean_dir
    )

    summary = build_clean_layer_validation_summary(
        table_results,
        relationship_results
    )

    write_clean_layer_validation_summary(
        summary,
        output_path
    )

    return summary