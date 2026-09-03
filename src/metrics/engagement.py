from pathlib import Path
import logging

import pandas as pd


logger = logging.getLogger(__name__)


STUDENT_ENROLLMENT_KEY = [
    "id_student",
    "code_module",
    "code_presentation",
]

STUDENT_WEEK_KEY = [
    "id_student",
    "code_module",
    "code_presentation",
    "week",
]


def build_engagement_metrics(
    vle_activity_path: Path,
) -> pd.DataFrame:
    """
    Build student-level engagement metrics from VLE activity.

    Grain:
        One row per student, module, and presentation.
    """

    vle_activity = pd.read_parquet(
        vle_activity_path
    )

    logger.info(
        "Building engagement metrics from %s VLE activity rows",
        len(vle_activity),
    )

    engagement_metrics = (
        vle_activity
        .groupby(
            STUDENT_ENROLLMENT_KEY,
            as_index=False,
            sort=False,
        )
        .agg(
            total_clicks=(
                "daily_clicks",
                "sum",
            ),
            active_days=(
                "date",
                "nunique",
            ),
            last_activity_day=(
                "date",
                "max",
            ),
        )
    )

    engagement_metrics[
        "avg_clicks_per_active_day"
    ] = (
        engagement_metrics["total_clicks"]
        / engagement_metrics["active_days"]
    )

    logger.info(
        "Engagement metrics built with %s student-enrollment rows",
        len(engagement_metrics),
    )

    return engagement_metrics


def build_weekly_engagement_metrics(
    vle_activity_path: Path,
) -> pd.DataFrame:
    """
    Build weekly student engagement metrics from VLE activity.

    Grain:
        One row per student, module, presentation, and week.

    Week 0 represents all observed pre-course activity.
    Week 1 begins on presentation day 0.
    """

    vle_activity = pd.read_parquet(
        vle_activity_path
    )

    logger.info(
        "Building weekly engagement metrics from %s VLE activity rows",
        len(vle_activity),
    )

    vle_activity = vle_activity.copy()

    vle_activity["week"] = (
        (vle_activity["date"] // 7) + 1
    )

    vle_activity.loc[
        vle_activity["date"] < 0,
        "week",
    ] = 0

    weekly_metrics = (
        vle_activity
        .groupby(
            STUDENT_WEEK_KEY,
            as_index=False,
            sort=False,
        )
        .agg(
            weekly_clicks=(
                "daily_clicks",
                "sum",
            ),
            weekly_active_days=(
                "date",
                "nunique",
            ),
        )
    )

    logger.info(
        "Weekly engagement metrics built with %s student-week rows",
        len(weekly_metrics),
    )

    return weekly_metrics


def build_continuous_weekly_engagement(
    weekly_metrics: pd.DataFrame,
    course_presentation_path: Path,
) -> pd.DataFrame:
    """
    Create continuous weekly engagement timelines.

    Missing course weeks for students with observed VLE activity are
    represented as zero engagement.

    Week 0 is retained only for students with observed pre-course
    activity. Course weeks begin at week 1.
    """

    course_presentations = pd.read_parquet(
        course_presentation_path,
        columns=[
            "code_module",
            "code_presentation",
            "module_presentation_length",
        ],
    )

    logger.info(
        "Building continuous weekly engagement from %s observed "
        "student-week rows",
        len(weekly_metrics),
    )

    student_presentations = (
        weekly_metrics[
            STUDENT_ENROLLMENT_KEY
        ]
        .drop_duplicates()
        .merge(
            course_presentations,
            on=[
                "code_module",
                "code_presentation",
            ],
            how="left",
            validate="many_to_one",
        )
    )

    if student_presentations[
        "module_presentation_length"
    ].isna().any():
        raise ValueError(
            "Missing course-presentation length while building "
            "continuous weekly engagement."
        )

    course_week_frames = []

    for row in student_presentations.itertuples(index=False):
        max_week = (
            int(row.module_presentation_length) - 1
        ) // 7 + 1

        course_week_frames.append(
            pd.DataFrame(
                {
                    "id_student": row.id_student,
                    "code_module": row.code_module,
                    "code_presentation": row.code_presentation,
                    "week": range(1, max_week + 1),
                }
            )
        )

    continuous_course_weeks = pd.concat(
        course_week_frames,
        ignore_index=True,
    )

    continuous_course_weeks = (
        continuous_course_weeks
        .merge(
            weekly_metrics,
            on=STUDENT_WEEK_KEY,
            how="left",
            validate="one_to_one",
        )
    )

    continuous_course_weeks[
        [
            "weekly_clicks",
            "weekly_active_days",
        ]
    ] = (
        continuous_course_weeks[
            [
                "weekly_clicks",
                "weekly_active_days",
            ]
        ]
        .fillna(0)
        .astype("int64")
    )

    pre_course_weeks = weekly_metrics.loc[
        weekly_metrics["week"] == 0
    ].copy()

    continuous_weekly_metrics = pd.concat(
        [
            pre_course_weeks,
            continuous_course_weeks,
        ],
        ignore_index=True,
    )

    continuous_weekly_metrics = (
        continuous_weekly_metrics
        .sort_values(STUDENT_WEEK_KEY)
        .reset_index(drop=True)
    )

    logger.info(
        "Continuous weekly engagement built with %s student-week rows",
        len(continuous_weekly_metrics),
    )

    return continuous_weekly_metrics

def add_weekly_engagement_change(
    weekly_metrics: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate week-to-week percentage change in VLE clicks.

    Percentage change is calculated only when the immediately
    preceding course week has non-zero activity.

    Week 0 is treated as pre-course activity and is not used as the
    comparison baseline for week 1.

    When the previous week's click count is zero, percentage change
    is undefined and remains missing.
    """

    metrics = weekly_metrics.copy()

    metrics = metrics.sort_values(
        STUDENT_WEEK_KEY
    ).reset_index(drop=True)

    course_weeks = metrics["week"] > 0

    course_metrics = metrics.loc[
        course_weeks
    ].copy()

    course_metrics["previous_week_clicks"] = (
        course_metrics
        .groupby(
            STUDENT_ENROLLMENT_KEY,
            sort=False,
        )["weekly_clicks"]
        .shift(1)
    )

    valid_comparison = (
        course_metrics["previous_week_clicks"].notna()
        & (course_metrics["previous_week_clicks"] > 0)
    )

    course_metrics["weekly_click_change_pct"] = pd.NA

    course_metrics.loc[
        valid_comparison,
        "weekly_click_change_pct",
    ] = (
        (
            course_metrics.loc[
                valid_comparison,
                "weekly_clicks",
            ]
            - course_metrics.loc[
                valid_comparison,
                "previous_week_clicks",
            ]
        )
        / course_metrics.loc[
            valid_comparison,
            "previous_week_clicks",
        ]
        * 100
    )

    course_metrics["weekly_click_change_pct"] = (
        pd.to_numeric(
            course_metrics["weekly_click_change_pct"],
            errors="coerce",
        ).astype("Float64")
    )

    metrics["previous_week_clicks"] = pd.NA
    metrics["weekly_click_change_pct"] = pd.NA

    metrics.loc[
        course_metrics.index,
        "previous_week_clicks",
    ] = course_metrics["previous_week_clicks"]

    metrics.loc[
        course_metrics.index,
        "weekly_click_change_pct",
    ] = course_metrics["weekly_click_change_pct"]

    metrics["previous_week_clicks"] = pd.to_numeric(
        metrics["previous_week_clicks"],
        errors="coerce",
    ).astype("Float64")

    metrics["weekly_click_change_pct"] = pd.to_numeric(
        metrics["weekly_click_change_pct"],
        errors="coerce",
    ).astype("Float64")

    logger.info(
        "Weekly engagement change calculated for %s student-week rows",
        metrics["weekly_click_change_pct"].notna().sum(),
    )

    return metrics
    


def validate_weekly_engagement_metrics(
    weekly_metrics: pd.DataFrame,
) -> dict[str, int | str]:
    """
    Validate weekly student engagement metric output.
    """

    duplicate_key_count = int(
        weekly_metrics.duplicated(
            subset=STUDENT_WEEK_KEY
        ).sum()
    )

    invalid_week_count = int(
        (
            weekly_metrics["week"] < 0
        ).sum()
    )

    invalid_weekly_clicks = int(
        (
            weekly_metrics["weekly_clicks"] < 0
        ).sum()
    )

    invalid_weekly_active_days = int(
        (
            weekly_metrics["weekly_active_days"] < 0
        ).sum()
    )

    invalid_course_week_active_days = int(
        (
            (weekly_metrics["week"] > 0)
            & (weekly_metrics["weekly_active_days"] > 7)
        ).sum()
    )

    missing_metric_values = int(
        weekly_metrics[
            [
                "week",
                "weekly_clicks",
                "weekly_active_days",
            ]
        ]
        .isna()
        .sum()
        .sum()
    )

    invalid_infinite_change = int(
        (
            weekly_metrics[
                "weekly_click_change_pct"
            ]
            .astype("float64")
            .isin(
                [
                    float("inf"),
                    float("-inf"),
                ]
            )
        ).sum()
    )

    invalid_drop_to_zero_change = int(
        (
            (weekly_metrics["previous_week_clicks"] > 0)
            & (weekly_metrics["weekly_clicks"] == 0)
            & (
                weekly_metrics[
                    "weekly_click_change_pct"
                ] != -100
            )
        ).sum()
    )

    invalid_restart_change = int(
        (
            (weekly_metrics["previous_week_clicks"] == 0)
            & (weekly_metrics["weekly_clicks"] > 0)
            & weekly_metrics[
                "weekly_click_change_pct"
            ].notna()
        ).sum()
    )

    invalid_initial_week_change = int(
        (
            weekly_metrics["week"].isin([0, 1])
            & weekly_metrics[
                "weekly_click_change_pct"
            ].notna()
        ).sum()
    )

    validation_passed = (
        duplicate_key_count == 0
        and invalid_week_count == 0
        and invalid_weekly_clicks == 0
        and invalid_weekly_active_days == 0
        and invalid_course_week_active_days == 0
        and missing_metric_values == 0
        and invalid_infinite_change == 0
        and invalid_drop_to_zero_change == 0
        and invalid_restart_change == 0
        and invalid_initial_week_change == 0
    )

    status = (
        "passed"
        if validation_passed
        else "failed"
    )

    return {
        "status": status,
        "row_count": len(weekly_metrics),
        "duplicate_key_count": duplicate_key_count,
        "invalid_week_count": invalid_week_count,
        "invalid_weekly_clicks": invalid_weekly_clicks,
        "invalid_weekly_active_days": invalid_weekly_active_days,
        "invalid_course_week_active_days": (
            invalid_course_week_active_days
        ),
        "invalid_infinite_change": invalid_infinite_change,
        "invalid_drop_to_zero_change": invalid_drop_to_zero_change,
        "invalid_restart_change": invalid_restart_change,
        "invalid_initial_week_change": invalid_initial_week_change,
        "missing_metric_values": missing_metric_values,
    }




def validate_engagement_metrics(
    engagement_metrics: pd.DataFrame,
) -> dict[str, int | str]:
    """
    Validate student-level engagement metric output.
    """

    duplicate_key_count = int(
        engagement_metrics.duplicated(
            subset=STUDENT_ENROLLMENT_KEY
        ).sum()
    )

    invalid_active_days = int(
        (
            engagement_metrics["active_days"] <= 0
        ).sum()
    )

    invalid_total_clicks = int(
        (
            engagement_metrics["total_clicks"] <= 0
        ).sum()
    )

    missing_metric_values = int(
        engagement_metrics[
            [
                "total_clicks",
                "active_days",
                "last_activity_day",
                "avg_clicks_per_active_day",
            ]
        ]
        .isna()
        .sum()
        .sum()
    )

    validation_passed = (
        duplicate_key_count == 0
        and invalid_active_days == 0
        and invalid_total_clicks == 0
        and missing_metric_values == 0
    )

    status = (
        "passed"
        if validation_passed
        else "failed"
    )

    return {
        "status": status,
        "row_count": len(engagement_metrics),
        "duplicate_key_count": duplicate_key_count,
        "invalid_active_days": invalid_active_days,
        "invalid_total_clicks": invalid_total_clicks,
        "missing_metric_values": missing_metric_values,
    }


def write_engagement_metrics(
    dataframe: pd.DataFrame,
    output_path: Path,
) -> None:
    """
    Write student-level engagement metrics to Parquet.
    """

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_parquet(
        output_path,
        index=False,
    )

    logger.info(
        "Engagement metrics written to %s with %s rows",
        output_path,
        len(dataframe),
    )



def write_weekly_engagement_metrics(
    dataframe: pd.DataFrame,
    output_path: Path,
) -> None:
    """
    Write weekly student engagement metrics to Parquet.
    """

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_parquet(
        output_path,
        index=False,
    )

    logger.info(
        "Weekly engagement metrics written to %s with %s rows",
        output_path,
        len(dataframe),
    )