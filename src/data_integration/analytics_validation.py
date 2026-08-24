from pathlib import Path
from typing import Any
import json
import logging

import pandas as pd


logger = logging.getLogger(__name__)


COURSE_PRESENTATION_KEY = [
    "code_module",
    "code_presentation",
]

ENROLLMENT_KEY = [
    "id_student",
    "code_module",
    "code_presentation",
]


def validate_reference_relationship(
    child_path: Path,
    parent_path: Path,
    child_columns: list[str],
    parent_columns: list[str],
) -> dict[str, int | str]:
    """
    Validate that every child analytical record references
    an existing parent analytical record.
    """

    child = pd.read_parquet(
        child_path,
        columns=child_columns,
    )

    parent = pd.read_parquet(
        parent_path,
        columns=parent_columns,
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

    logger.info(
        "Validated analytical relationship with %s child rows "
        "and %s invalid references",
        len(child),
        invalid_row_count,
    )

    return {
        "status": status,
        "child_row_count": len(child),
        "invalid_row_count": invalid_row_count,
    }


def build_analytics_relationship_results(
    analytics_dir: Path,
) -> dict[str, dict[str, int | str]]:
    """
    Run the core analytics-layer referential-integrity checks.
    """

    return {
        "student_enrollment_to_course_presentation": (
            validate_reference_relationship(
                analytics_dir / "student_enrollment.parquet",
                analytics_dir / "course_presentation.parquet",
                COURSE_PRESENTATION_KEY,
                COURSE_PRESENTATION_KEY,
            )
        ),
        "assessment_submission_to_course_presentation": (
            validate_reference_relationship(
                analytics_dir / "assessment_submission.parquet",
                analytics_dir / "course_presentation.parquet",
                COURSE_PRESENTATION_KEY,
                COURSE_PRESENTATION_KEY,
            )
        ),
        "vle_activity_to_course_presentation": (
            validate_reference_relationship(
                analytics_dir / "vle_activity.parquet",
                analytics_dir / "course_presentation.parquet",
                COURSE_PRESENTATION_KEY,
                COURSE_PRESENTATION_KEY,
            )
        ),
        "assessment_submission_to_student_enrollment": (
            validate_reference_relationship(
                analytics_dir / "assessment_submission.parquet",
                analytics_dir / "student_enrollment.parquet",
                ENROLLMENT_KEY,
                ENROLLMENT_KEY,
            )
        ),
        "vle_activity_to_student_enrollment": (
            validate_reference_relationship(
                analytics_dir / "vle_activity.parquet",
                analytics_dir / "student_enrollment.parquet",
                ENROLLMENT_KEY,
                ENROLLMENT_KEY,
            )
        ),
    }


def build_analytics_validation_summary(
    relationship_results: dict[str, dict[str, int | str]],
) -> dict[str, Any]:
    """
    Build a machine-readable analytics-layer validation summary.
    """

    all_relationships_passed = all(
        result.get("status") == "passed"
        for result in relationship_results.values()
    )

    overall_status = (
        "passed"
        if all_relationships_passed
        else "failed"
    )

    return {
        "overall_status": overall_status,
        "analytics_ready": overall_status == "passed",
        "relationships": relationship_results,
    }


def write_analytics_validation_summary(
    summary: dict[str, Any],
    output_path: Path,
) -> None:
    """
    Write the analytics-layer validation summary to JSON.
    """

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            summary,
            file,
            indent=2,
        )


def run_analytics_validation(
    analytics_dir: Path,
    output_path: Path,
) -> dict[str, Any]:
    """
    Run the complete analytics-layer validation workflow
    and persist its summary.
    """

    relationship_results = build_analytics_relationship_results(
        analytics_dir
    )

    summary = build_analytics_validation_summary(
        relationship_results
    )

    write_analytics_validation_summary(
        summary,
        output_path
    )

    return summary