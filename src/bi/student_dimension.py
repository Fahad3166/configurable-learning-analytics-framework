"""Build the student dimension for the CLAF BI semantic layer."""

from pathlib import Path

import pandas as pd


STUDENT_KEY = ["id_student"]

STUDENT_ATTRIBUTES = [
    "id_student",
    "gender",
    "region",
    "highest_education",
    "imd_band",
    "disability",
]


def build_student_dimension(
    student_profile: pd.DataFrame,
) -> pd.DataFrame:
    """Create one BI dimension row per student."""

    missing_columns = [
        column
        for column in STUDENT_ATTRIBUTES
        if column not in student_profile.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Student profile is missing required columns: {missing_columns}"
        )

    source = student_profile[STUDENT_ATTRIBUTES].copy()

    # All selected demographic attributes must be stable for each student.
    attribute_columns = [
        column for column in STUDENT_ATTRIBUTES if column != "id_student"
    ]

    stability = (
        source.groupby("id_student")[attribute_columns]
        .nunique(dropna=False)
    )

    unstable = stability.gt(1).any(axis=1)

    if unstable.any():
        unstable_students = stability.index[unstable].tolist()

        raise ValueError(
            "Student dimension contains attributes that change across "
            f"enrollments. Unstable students: {len(unstable_students)}"
        )

    dimension = (
        source
        .drop_duplicates()
        .sort_values("id_student")
        .reset_index(drop=True)
    )

    return dimension


def validate_student_dimension(
    dimension: pd.DataFrame,
    student_profile: pd.DataFrame,
) -> dict:
    """Validate student dimension grain and source coverage."""

    expected_students = student_profile["id_student"].nunique()

    duplicate_keys = int(
        dimension.duplicated(STUDENT_KEY).sum()
    )

    missing_students = (
        student_profile[["id_student"]]
        .drop_duplicates()
        .merge(
            dimension[["id_student"]],
            on="id_student",
            how="left",
            indicator=True,
        )
    )

    missing_student_count = int(
        (missing_students["_merge"] == "left_only").sum()
    )

    passed = (
        len(dimension) == expected_students
        and duplicate_keys == 0
        and missing_student_count == 0
    )

    return {
        "passed": passed,
        "row_count": len(dimension),
        "expected_student_count": expected_students,
        "duplicate_student_keys": duplicate_keys,
        "missing_students": missing_student_count,
    }


def write_student_dimension(
    dimension: pd.DataFrame,
    output_path: Path,
) -> None:
    """Persist the student dimension as Parquet."""

    output_path.parent.mkdir(parents=True, exist_ok=True)

    dimension.to_parquet(
        output_path,
        index=False,
    )