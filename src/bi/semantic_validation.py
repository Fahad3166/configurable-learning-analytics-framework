"""Cross-table semantic validation for the CLAF BI layer."""

import pandas as pd


LEARNING_KEY = [
    "id_student",
    "course_presentation_key",
]

WEEK_KEY = [
    "id_student",
    "course_presentation_key",
    "week",
]


def validate_bi_semantic_model(
    dim_student: pd.DataFrame,
    dim_course: pd.DataFrame,
    fact_learning: pd.DataFrame,
    fact_week: pd.DataFrame,
) -> dict:
    """Validate relationships and reconciliation across the BI model."""

    checks = {}

    # --------------------------------------------------------------
    # Dimension primary keys
    # --------------------------------------------------------------

    checks["duplicate_student_dimension_keys"] = int(
        dim_student.duplicated(["id_student"]).sum()
    )

    checks["duplicate_course_dimension_keys"] = int(
        dim_course.duplicated(
            ["course_presentation_key"]
        ).sum()
    )

    # --------------------------------------------------------------
    # Fact grains
    # --------------------------------------------------------------

    checks["duplicate_learning_fact_keys"] = int(
        fact_learning.duplicated(
            LEARNING_KEY
        ).sum()
    )

    checks["duplicate_week_fact_keys"] = int(
        fact_week.duplicated(
            WEEK_KEY
        ).sum()
    )

    # --------------------------------------------------------------
    # Student foreign keys
    # --------------------------------------------------------------

    learning_student_fk = (
        fact_learning[["id_student"]]
        .drop_duplicates()
        .merge(
            dim_student[["id_student"]],
            on="id_student",
            how="left",
            indicator=True,
        )
    )

    checks["learning_fact_missing_students"] = int(
        (
            learning_student_fk["_merge"]
            == "left_only"
        ).sum()
    )

    week_student_fk = (
        fact_week[["id_student"]]
        .drop_duplicates()
        .merge(
            dim_student[["id_student"]],
            on="id_student",
            how="left",
            indicator=True,
        )
    )

    checks["week_fact_missing_students"] = int(
        (
            week_student_fk["_merge"]
            == "left_only"
        ).sum()
    )

    # --------------------------------------------------------------
    # Course-presentation foreign keys
    # --------------------------------------------------------------

    learning_course_fk = (
        fact_learning[["course_presentation_key"]]
        .drop_duplicates()
        .merge(
            dim_course[["course_presentation_key"]],
            on="course_presentation_key",
            how="left",
            indicator=True,
        )
    )

    checks["learning_fact_missing_courses"] = int(
        (
            learning_course_fk["_merge"]
            == "left_only"
        ).sum()
    )

    week_course_fk = (
        fact_week[["course_presentation_key"]]
        .drop_duplicates()
        .merge(
            dim_course[["course_presentation_key"]],
            on="course_presentation_key",
            how="left",
            indicator=True,
        )
    )

    checks["week_fact_missing_courses"] = int(
        (
            week_course_fk["_merge"]
            == "left_only"
        ).sum()
    )

    # --------------------------------------------------------------
    # Weekly fact enrollment relationship
    # --------------------------------------------------------------

    learning_enrollments = (
        fact_learning[LEARNING_KEY]
        .drop_duplicates()
    )

    weekly_enrollments = (
        fact_week[LEARNING_KEY]
        .drop_duplicates()
    )

    weekly_orphans = weekly_enrollments.merge(
        learning_enrollments,
        on=LEARNING_KEY,
        how="left",
        indicator=True,
    )

    checks["week_enrollments_without_learning_fact"] = int(
        (
            weekly_orphans["_merge"]
            == "left_only"
        ).sum()
    )

    checks["learning_enrollment_count"] = int(
        len(learning_enrollments)
    )

    checks["weekly_enrollment_count"] = int(
        len(weekly_enrollments)
    )

    # --------------------------------------------------------------
    # Metric reconciliation
    # --------------------------------------------------------------

    checks["learning_total_clicks"] = int(
        fact_learning["total_clicks"]
        .fillna(0)
        .sum()
    )

    checks["weekly_total_clicks"] = int(
        fact_week["weekly_clicks"].sum()
    )

    checks["learning_missing_improvement"] = int(
        fact_learning[
            "assessment_improvement_status"
        ]
        .isna()
        .sum()
    )

    checks["learning_missing_risk_level"] = int(
        fact_learning["risk_level"]
        .isna()
        .sum()
    )

    checks["learning_missing_risk_score"] = int(
        fact_learning["risk_score"]
        .isna()
        .sum()
    )

    # --------------------------------------------------------------
    # Overall pass
    # --------------------------------------------------------------

    zero_required_checks = [
        "duplicate_student_dimension_keys",
        "duplicate_course_dimension_keys",
        "duplicate_learning_fact_keys",
        "duplicate_week_fact_keys",
        "learning_fact_missing_students",
        "week_fact_missing_students",
        "learning_fact_missing_courses",
        "week_fact_missing_courses",
        "week_enrollments_without_learning_fact",
        "learning_missing_risk_score",
    ]

    passed = all(
        checks[name] == 0
        for name in zero_required_checks
    )

    return {
        "passed": passed,
        **checks,
    }