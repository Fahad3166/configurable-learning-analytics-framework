"""Build the course-presentation dimension for the CLAF BI semantic layer."""

from pathlib import Path

import pandas as pd


COURSE_PRESENTATION_KEY = [
    "code_module",
    "code_presentation",
]


def build_course_presentation_dimension(
    course_presentation: pd.DataFrame,
) -> pd.DataFrame:
    """Create one BI dimension row per module-presentation combination."""

    required_columns = [
        "code_module",
        "code_presentation",
        "module_presentation_length",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in course_presentation.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Course presentation data is missing required columns: "
            f"{missing_columns}"
        )

    dimension = course_presentation[required_columns].copy()

    duplicate_keys = dimension.duplicated(
        COURSE_PRESENTATION_KEY
    ).sum()

    if duplicate_keys:
        raise ValueError(
            "Course-presentation dimension contains duplicate "
            f"business keys: {duplicate_keys}"
        )

    # Create a stable BI-friendly surrogate-style key.
    dimension["course_presentation_key"] = (
        dimension["code_module"]
        + "_"
        + dimension["code_presentation"]
    )

    dimension = dimension[
        [
            "course_presentation_key",
            "code_module",
            "code_presentation",
            "module_presentation_length",
        ]
    ]

    dimension = (
        dimension
        .sort_values(
            ["code_module", "code_presentation"]
        )
        .reset_index(drop=True)
    )

    return dimension


def validate_course_presentation_dimension(
    dimension: pd.DataFrame,
    course_presentation: pd.DataFrame,
) -> dict:
    """Validate course-presentation dimension grain and coverage."""

    duplicate_business_keys = int(
        dimension.duplicated(
            ["code_module", "code_presentation"]
        ).sum()
    )

    duplicate_dimension_keys = int(
        dimension.duplicated(
            ["course_presentation_key"]
        ).sum()
    )

    source_keys = course_presentation[
        ["code_module", "code_presentation"]
    ].drop_duplicates()

    dimension_keys = dimension[
        ["code_module", "code_presentation"]
    ]

    coverage = source_keys.merge(
        dimension_keys,
        on=["code_module", "code_presentation"],
        how="left",
        indicator=True,
    )

    missing_presentations = int(
        (coverage["_merge"] == "left_only").sum()
    )

    expected_rows = len(source_keys)

    passed = (
        len(dimension) == expected_rows
        and duplicate_business_keys == 0
        and duplicate_dimension_keys == 0
        and missing_presentations == 0
    )

    return {
        "passed": passed,
        "row_count": len(dimension),
        "expected_row_count": expected_rows,
        "duplicate_business_keys": duplicate_business_keys,
        "duplicate_dimension_keys": duplicate_dimension_keys,
        "missing_presentations": missing_presentations,
    }


def write_course_presentation_dimension(
    dimension: pd.DataFrame,
    output_path: Path,
) -> None:
    """Persist the course-presentation dimension as Parquet."""

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dimension.to_parquet(
        output_path,
        index=False,
    )