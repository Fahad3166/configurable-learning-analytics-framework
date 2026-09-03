"""Build the enrollment-level learning fact for the CLAF BI semantic layer."""

from pathlib import Path

import pandas as pd


FACT_KEY = [
    "id_student",
    "code_module",
    "code_presentation",
]


def build_student_learning_fact(
    student_profile: pd.DataFrame,
    cohort_metrics: pd.DataFrame,
    risk_metrics: pd.DataFrame,
    improvement_metrics: pd.DataFrame,
) -> pd.DataFrame:
    """Create one BI fact row per student enrollment."""

    for name, df in {
        "student_profile": student_profile,
        "cohort_metrics": cohort_metrics,
        "risk_metrics": risk_metrics,
        "improvement_metrics": improvement_metrics,
    }.items():
        missing_keys = [
            column for column in FACT_KEY
            if column not in df.columns
        ]

        if missing_keys:
            raise ValueError(
                f"{name} is missing fact keys: {missing_keys}"
            )

        duplicates = int(
            df.duplicated(FACT_KEY).sum()
        )

        if duplicates:
            raise ValueError(
                f"{name} contains duplicate fact keys: {duplicates}"
            )

    fact = student_profile.copy()

    # Cohort metrics already contain some fields also present in risk.
    cohort_columns = [
        *FACT_KEY,
        "cohort_mean_clicks",
        "cohort_engagement_count",
        "clicks_vs_cohort",
        "cohort_mean_score",
        "cohort_score_count",
        "score_vs_cohort",
    ]

    fact = fact.merge(
        cohort_metrics[cohort_columns],
        on=FACT_KEY,
        how="left",
        validate="one_to_one",
    )

    risk_columns = [
        *FACT_KEY,
        "risk_score",
        "risk_level",
        "available_signal_count",
        "evidence_coverage",
        "evidence_status",
        "four_week_click_change_pct",
    ]

    fact = fact.merge(
        risk_metrics[risk_columns],
        on=FACT_KEY,
        how="left",
        validate="one_to_one",
    )

    improvement_columns = [
        *FACT_KEY,
        "previous_assessment_mean",
        "recent_assessment_mean",
        "assessment_score_change",
        "assessment_observation_progress",
        "assessment_window_size",
        "assessment_improvement_status",
    ]

    fact = fact.merge(
        improvement_metrics[improvement_columns],
        on=FACT_KEY,
        how="left",
        validate="one_to_one",
    )

    fact["course_presentation_key"] = (
        fact["code_module"]
        + "_"
        + fact["code_presentation"]
    )

    # Student demographics that are stable at student level belong in dim_student.
    # Keep enrollment-dependent attributes and analytical measures in the fact.
    fact = fact.drop(
        columns=[
            "gender",
            "region",
            "highest_education",
            "imd_band",
            "disability",
        ]
    )

    ordered_columns = [
        "id_student",
        "course_presentation_key",
        "code_module",
        "code_presentation",
        "age_band",
        "num_of_prev_attempts",
        "studied_credits",
        "final_result",
        "date_registration",
        "date_unregistration",
    ]

    remaining_columns = [
        column
        for column in fact.columns
        if column not in ordered_columns
    ]

    fact = fact[
        ordered_columns + remaining_columns
    ]

    return (
        fact
        .sort_values(
            ["code_module", "code_presentation", "id_student"]
        )
        .reset_index(drop=True)
    )


def validate_student_learning_fact(
    fact: pd.DataFrame,
    student_profile: pd.DataFrame,
    student_dimension: pd.DataFrame,
    course_dimension: pd.DataFrame,
) -> dict:
    """Validate fact grain and dimension relationships."""

    duplicate_fact_keys = int(
        fact.duplicated(FACT_KEY).sum()
    )

    expected_rows = len(student_profile)

    student_fk_check = fact[
        ["id_student"]
    ].merge(
        student_dimension[["id_student"]],
        on="id_student",
        how="left",
        indicator=True,
    )

    missing_student_keys = int(
        (student_fk_check["_merge"] == "left_only").sum()
    )

    course_fk_check = fact[
        ["course_presentation_key"]
    ].merge(
        course_dimension[["course_presentation_key"]],
        on="course_presentation_key",
        how="left",
        indicator=True,
    )

    missing_course_keys = int(
        (course_fk_check["_merge"] == "left_only").sum()
    )

    missing_risk_records = int(
        fact["risk_score"].isna().sum()
    )

    missing_improvement_records = int(
        fact["assessment_improvement_status"].isna().sum()
    )

    passed = (
        len(fact) == expected_rows
        and duplicate_fact_keys == 0
        and missing_student_keys == 0
        and missing_course_keys == 0
        and missing_risk_records == 0
    )

    return {
        "passed": passed,
        "row_count": len(fact),
        "expected_row_count": expected_rows,
        "duplicate_fact_keys": duplicate_fact_keys,
        "missing_student_dimension_keys": missing_student_keys,
        "missing_course_dimension_keys": missing_course_keys,
        "missing_risk_records": missing_risk_records,
        "missing_improvement_records": missing_improvement_records,
    }


def write_student_learning_fact(
    fact: pd.DataFrame,
    output_path: Path,
) -> None:
    """Persist the enrollment-level BI fact."""

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fact.to_parquet(
        output_path,
        index=False,
    )