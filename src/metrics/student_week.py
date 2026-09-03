from pathlib import Path
import logging

import pandas as pd


logger = logging.getLogger(__name__)


STUDENT_WEEK_KEY = [
    "id_student",
    "code_module",
    "code_presentation",
    "week",
]


def build_student_week_spine(
    student_enrollment_path: Path,
    course_presentation_path: Path,
) -> pd.DataFrame:
    """
    Build the eligible course-period student-week timeline.

    Grain:
        One row per student, module, presentation, and eligible course week.

    Week 0 is not generated here.
    This function creates only course-period weeks starting from Week 1.
    """

    student_enrollment = pd.read_parquet(
        student_enrollment_path
    )

    course_presentation = pd.read_parquet(
        course_presentation_path
    )

    logger.info(
        "Building student-week spine from %s enrollments",
        len(student_enrollment),
    )

    enrollment = student_enrollment.merge(
        course_presentation,
        on=[
            "code_module",
            "code_presentation",
        ],
        how="left",
        validate="many_to_one",
    )

    enrollment["final_eligible_day"] = (
        enrollment["module_presentation_length"]
    ).astype("Float64")

    known_unregistration = (
        enrollment["date_unregistration"].notna()
    )

    enrollment.loc[
        known_unregistration,
        "final_eligible_day",
    ] = (
        enrollment.loc[
            known_unregistration,
            [
                "date_unregistration",
                "final_eligible_day",
            ],
        ]
        .min(axis=1)
    )

    enrollment = enrollment[
        enrollment["final_eligible_day"] >= 0
    ].copy()

    enrollment["final_week"] = (
        enrollment["final_eligible_day"] // 7
    ).astype(int) + 1

    student_week = (
        enrollment[
            [
                "id_student",
                "code_module",
                "code_presentation",
                "final_week",
            ]
        ]
        .assign(
            week=lambda dataframe: dataframe[
                "final_week"
            ].apply(
                lambda value: list(
                    range(
                        1,
                        value + 1,
                    )
                )
            )
        )
        .explode(
            "week",
            ignore_index=True,
        )
        .drop(
            columns="final_week"
        )
    )

    student_week["week"] = (
        student_week["week"].astype(int)
    )

    logger.info(
        "Student-week spine built with %s course-period rows",
        len(student_week),
    )

    return student_week


def build_student_week_engagement(
    student_week_spine: pd.DataFrame,
    weekly_engagement: pd.DataFrame,
) -> pd.DataFrame:
    """
    Combine the eligible student-week spine with observed weekly engagement.

    Eligible weeks without observed VLE activity are represented explicitly
    with zero clicks and zero active days.

    Observed activity outside the eligible student-week spine is excluded
    from this participation-based metric table.
    """

    logger.info(
        "Building student-week engagement from %s eligible weeks "
        "and %s observed weekly activity rows",
        len(student_week_spine),
        len(weekly_engagement),
    )

    course_weekly_engagement = weekly_engagement[
        weekly_engagement["week"] > 0
    ].copy()

    student_week_engagement = student_week_spine.merge(
        course_weekly_engagement,
        on=STUDENT_WEEK_KEY,
        how="left",
        validate="one_to_one",
    )

    student_week_engagement[
        ["weekly_clicks", "weekly_active_days"]
    ] = (
        student_week_engagement[
            ["weekly_clicks", "weekly_active_days"]
        ]
        .fillna(0)
        .astype("int64")
    )

    logger.info(
        "Student-week engagement built with %s rows",
        len(student_week_engagement),
    )

    return student_week_engagement


def add_weekly_engagement_change(
    student_week_engagement: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add week-over-week click change for consecutive eligible course weeks.

    Percentage change is calculated only when the previous week's
    click count is greater than zero.

    The first eligible week and zero-denominator transitions are
    represented as missing rather than producing artificial or
    infinite percentage values.
    """

    result = student_week_engagement.sort_values(
        STUDENT_WEEK_KEY
    ).copy()

    enrollment_key = [
        "id_student",
        "code_module",
        "code_presentation",
    ]

    result["previous_weekly_clicks"] = (
        result.groupby(
            enrollment_key,
            sort=False,
        )["weekly_clicks"]
        .shift(1)
    )

    valid_denominator = (
        result["previous_weekly_clicks"] > 0
    )

    result["weekly_click_change_pct"] = pd.NA

    result.loc[
        valid_denominator,
        "weekly_click_change_pct",
    ] = (
        (
            result.loc[
                valid_denominator,
                "weekly_clicks",
            ]
            - result.loc[
                valid_denominator,
                "previous_weekly_clicks",
            ]
        )
        / result.loc[
            valid_denominator,
            "previous_weekly_clicks",
        ]
        * 100
    )

    result["weekly_click_change_pct"] = (
        pd.to_numeric(
            result["weekly_click_change_pct"],
            errors="coerce",
        ).astype("Float64")
    )

    logger.info(
        "Weekly engagement change calculated for %s rows",
        valid_denominator.sum(),
    )

    return result

def validate_student_week_engagement(
    student_week_engagement: pd.DataFrame,
) -> dict:
    """
    Validate the student-week engagement metric table.
    """

    duplicate_key_count = (
        student_week_engagement.duplicated(
            subset=STUDENT_WEEK_KEY
        ).sum()
    )

    invalid_week_count = (
        student_week_engagement["week"] < 1
    ).sum()

    negative_click_count = (
        student_week_engagement["weekly_clicks"] < 0
    ).sum()

    invalid_active_days_count = (
        (
            student_week_engagement["weekly_active_days"] < 0
        )
        | (
            student_week_engagement["weekly_active_days"] > 7
        )
    ).sum()

    missing_click_count = (
        student_week_engagement["weekly_clicks"]
        .isna()
        .sum()
    )

    missing_active_days_count = (
        student_week_engagement["weekly_active_days"]
        .isna()
        .sum()
    )

    infinite_change_count = 0

    if "weekly_click_change_pct" in student_week_engagement.columns:
        change_values = (
            student_week_engagement[
                "weekly_click_change_pct"
            ]
            .dropna()
            .astype(float)
        )

        infinite_change_count = (
            (~pd.Series(change_values).map(
                lambda value: float("-inf")
                < value
                < float("inf")
            ))
            .sum()
        )

    status = (
        "passed"
        if all(
            count == 0
            for count in [
                duplicate_key_count,
                invalid_week_count,
                negative_click_count,
                invalid_active_days_count,
                missing_click_count,
                missing_active_days_count,
                infinite_change_count,
            ]
        )
        else "failed"
    )

    return {
        "status": status,
        "row_count": len(student_week_engagement),
        "duplicate_key_count": int(duplicate_key_count),
        "invalid_week_count": int(invalid_week_count),
        "negative_click_count": int(negative_click_count),
        "invalid_active_days_count": int(
            invalid_active_days_count
        ),
        "missing_click_count": int(missing_click_count),
        "missing_active_days_count": int(
            missing_active_days_count
        ),
        "infinite_change_count": int(
            infinite_change_count
        ),
    }

def write_student_week_engagement(
    student_week_engagement: pd.DataFrame,
    output_path: Path,
) -> None:
    """
    Write the validated student-week engagement metric table to Parquet.
    """

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    student_week_engagement.to_parquet(
        output_path,
        index=False,
    )

    logger.info(
        "Student-week engagement written to %s with %s rows",
        output_path,
        len(student_week_engagement),
    )



    