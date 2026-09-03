"""Build the weekly student fact table for the CLAF BI semantic layer."""

from pathlib import Path

import pandas as pd


WEEK_FACT_KEY = [
    "id_student",
    "course_presentation_key",
    "week",
]


def build_student_week_fact(
    student_week_engagement: pd.DataFrame,
    course_dimension: pd.DataFrame,
) -> pd.DataFrame:
    """Build the BI-ready weekly student engagement fact table."""

    required_columns = [
        "id_student",
        "code_module",
        "code_presentation",
        "week",
        "weekly_clicks",
        "weekly_active_days",
        "previous_weekly_clicks",
        "weekly_click_change_pct",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in student_week_engagement.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required student-week columns: "
            f"{missing_columns}"
        )

    required_course_columns = [
        "course_presentation_key",
        "module_presentation_length",
    ]

    missing_course_columns = [
        column
        for column in required_course_columns
        if column not in course_dimension.columns
    ]

    if missing_course_columns:
        raise ValueError(
            "Missing required course dimension columns: "
            f"{missing_course_columns}"
        )

    fact = student_week_engagement[
        required_columns
    ].copy()

    # --------------------------------------------------------------
    # Create BI course-presentation key
    # --------------------------------------------------------------

    fact["course_presentation_key"] = (
        fact["code_module"].astype("string")
        + "_"
        + fact["code_presentation"].astype("string")
    )

    # --------------------------------------------------------------
    # Enforce weekly fact grain
    # --------------------------------------------------------------

    duplicate_keys = int(
        fact.duplicated(
            [
                "id_student",
                "course_presentation_key",
                "week",
            ]
        ).sum()
    )

    if duplicate_keys > 0:
        raise ValueError(
            "Duplicate student-week fact grain detected: "
            f"{duplicate_keys}"
        )

    # --------------------------------------------------------------
    # Attach presentation length
    # --------------------------------------------------------------

    course_lookup = course_dimension[
        [
            "course_presentation_key",
            "module_presentation_length",
        ]
    ].copy()

    duplicate_course_keys = int(
        course_lookup.duplicated(
            ["course_presentation_key"]
        ).sum()
    )

    if duplicate_course_keys > 0:
        raise ValueError(
            "Course dimension contains duplicate "
            "course_presentation_key values: "
            f"{duplicate_course_keys}"
        )

    fact = fact.merge(
        course_lookup,
        on="course_presentation_key",
        how="left",
        validate="many_to_one",
    )

    missing_lengths = int(
        fact["module_presentation_length"]
        .isna()
        .sum()
    )

    if missing_lengths > 0:
        raise ValueError(
            "Student-week fact contains rows without "
            "presentation length: "
            f"{missing_lengths}"
        )

    # --------------------------------------------------------------
    # Presentation-aware week positioning
    # --------------------------------------------------------------

    fact["week_start_day"] = (
        fact["week"] - 1
    ) * 7

    fact["course_progress_pct"] = (
        fact["week_start_day"]
        / fact["module_presentation_length"]
        * 100
    )

    # --------------------------------------------------------------
    # Course progress bands
    # --------------------------------------------------------------

    fact["course_progress_band"] = pd.cut(
        fact["course_progress_pct"],
        bins=[
            -0.001,
            25,
            50,
            75,
            100,
        ],
        labels=[
            "Early (0-25%)",
            "Early-Mid (25-50%)",
            "Late-Mid (50-75%)",
            "Late (75-100%)",
        ],
        include_lowest=True,
        right=True,
    ).astype("string")

    # Presentation length belongs in the dimension rather than
    # being duplicated in the weekly fact.
    fact = fact.drop(
        columns=["module_presentation_length"]
    )

    # --------------------------------------------------------------
    # Final BI column order
    # --------------------------------------------------------------

    fact = fact[
        [
            "id_student",
            "course_presentation_key",
            "code_module",
            "code_presentation",
            "week",
            "week_start_day",
            "course_progress_pct",
            "course_progress_band",
            "weekly_clicks",
            "weekly_active_days",
            "previous_weekly_clicks",
            "weekly_click_change_pct",
        ]
    ]

    fact = fact.sort_values(
        [
            "code_module",
            "code_presentation",
            "id_student",
            "week",
        ]
    ).reset_index(drop=True)

    return fact


def validate_student_week_fact(
    fact: pd.DataFrame,
    student_week_engagement: pd.DataFrame,
    student_dimension: pd.DataFrame,
    course_dimension: pd.DataFrame,
) -> dict:
    """Validate the BI weekly fact table."""

    duplicate_fact_keys = int(
        fact.duplicated(
            WEEK_FACT_KEY
        ).sum()
    )

    # --------------------------------------------------------------
    # Student dimension relationship
    # --------------------------------------------------------------

    fact_students = (
        fact[["id_student"]]
        .drop_duplicates()
    )

    student_fk_check = fact_students.merge(
        student_dimension[["id_student"]],
        on="id_student",
        how="left",
        indicator=True,
    )

    missing_students = int(
        (
            student_fk_check["_merge"]
            == "left_only"
        ).sum()
    )

    # --------------------------------------------------------------
    # Course-presentation dimension relationship
    # --------------------------------------------------------------

    fact_courses = (
        fact[["course_presentation_key"]]
        .drop_duplicates()
    )

    course_fk_check = fact_courses.merge(
        course_dimension[
            ["course_presentation_key"]
        ],
        on="course_presentation_key",
        how="left",
        indicator=True,
    )

    missing_courses = int(
        (
            course_fk_check["_merge"]
            == "left_only"
        ).sum()
    )

    # --------------------------------------------------------------
    # Metric reconciliation
    # --------------------------------------------------------------

    source_weekly_clicks = int(
        student_week_engagement[
            "weekly_clicks"
        ].sum()
    )

    fact_weekly_clicks = int(
        fact["weekly_clicks"].sum()
    )

    source_weekly_active_days = int(
        student_week_engagement[
            "weekly_active_days"
        ].sum()
    )

    fact_weekly_active_days = int(
        fact["weekly_active_days"].sum()
    )

    # --------------------------------------------------------------
    # Progress validation
    # --------------------------------------------------------------

    missing_progress = int(
        fact["course_progress_pct"]
        .isna()
        .sum()
    )

    progress_below_zero = int(
        (
            fact["course_progress_pct"] < 0
        ).sum()
    )

    progress_above_100 = int(
        (
            fact["course_progress_pct"] > 100
        ).sum()
    )

    missing_progress_band = int(
        fact["course_progress_band"]
        .isna()
        .sum()
    )

    # --------------------------------------------------------------
    # Overall status
    # --------------------------------------------------------------

    passed = all(
        [
            len(fact)
            == len(student_week_engagement),
            duplicate_fact_keys == 0,
            missing_students == 0,
            missing_courses == 0,
            source_weekly_clicks
            == fact_weekly_clicks,
            source_weekly_active_days
            == fact_weekly_active_days,
            missing_progress == 0,
            progress_below_zero == 0,
            progress_above_100 == 0,
            missing_progress_band == 0,
        ]
    )

    return {
        "passed": passed,
        "row_count": int(len(fact)),
        "expected_row_count": int(
            len(student_week_engagement)
        ),
        "duplicate_fact_keys": duplicate_fact_keys,
        "missing_student_dimension_keys": missing_students,
        "missing_course_dimension_keys": missing_courses,
        "source_weekly_clicks": source_weekly_clicks,
        "fact_weekly_clicks": fact_weekly_clicks,
        "source_weekly_active_days": (
            source_weekly_active_days
        ),
        "fact_weekly_active_days": (
            fact_weekly_active_days
        ),
        "missing_course_progress": missing_progress,
        "course_progress_below_zero": progress_below_zero,
        "course_progress_above_100": progress_above_100,
        "missing_course_progress_band": (
            missing_progress_band
        ),
        "min_week": int(
            fact["week"].min()
        ),
        "max_week": int(
            fact["week"].max()
        ),
        "min_course_progress_pct": float(
            fact["course_progress_pct"].min()
        ),
        "max_course_progress_pct": float(
            fact["course_progress_pct"].max()
        ),
    }


def write_student_week_fact(
    fact: pd.DataFrame,
    output_path: Path,
) -> None:
    """Write the BI weekly fact table to Parquet."""

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fact.to_parquet(
        output_path,
        index=False,
    )