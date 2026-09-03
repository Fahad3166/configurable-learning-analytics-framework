import logging
from pathlib import Path
import pandas as pd


logger = logging.getLogger(__name__)


STUDENT_ENROLLMENT_KEY = [
    "id_student",
    "code_module",
    "code_presentation",
]


def build_engagement_trajectory(
    student_week_engagement: pd.DataFrame,
    course_presentation: pd.DataFrame,
    observation_progress: float,
    window_weeks: int,
) -> pd.DataFrame:
    """
    Build an enrollment-level engagement trajectory metric.

    The metric compares clicks in the most recent configured window with
    clicks in the immediately preceding window at a configurable course
    progress observation point.

    A trajectory is undefined when the previous comparison window contains
    zero clicks because no valid percentage-change baseline exists.
    """

    if not 0 < observation_progress <= 1:
        raise ValueError(
            "observation_progress must be greater than 0 and less than "
            "or equal to 1."
        )

    if window_weeks <= 0:
        raise ValueError(
            "window_weeks must be greater than 0."
        )

    required_weekly_columns = {
        *STUDENT_ENROLLMENT_KEY,
        "week",
        "weekly_clicks",
    }

    missing_weekly_columns = (
        required_weekly_columns
        - set(student_week_engagement.columns)
    )

    if missing_weekly_columns:
        raise ValueError(
            "student_week_engagement is missing required columns: "
            f"{sorted(missing_weekly_columns)}"
        )

    required_presentation_columns = {
        "code_module",
        "code_presentation",
        "module_presentation_length",
    }

    missing_presentation_columns = (
        required_presentation_columns
        - set(course_presentation.columns)
    )

    if missing_presentation_columns:
        raise ValueError(
            "course_presentation is missing required columns: "
            f"{sorted(missing_presentation_columns)}"
        )

    weekly = student_week_engagement.merge(
        course_presentation[
            [
                "code_module",
                "code_presentation",
                "module_presentation_length",
            ]
        ],
        on=[
            "code_module",
            "code_presentation",
        ],
        how="left",
        validate="many_to_one",
    )

    if weekly["module_presentation_length"].isna().any():
        raise ValueError(
            "Some student-week rows are missing presentation length."
        )

    weekly["course_week_count"] = (
        weekly["module_presentation_length"] // 7 + 1
    ).astype(int)

    weekly["observation_week"] = (
        weekly["course_week_count"]
        * observation_progress
    ).round().astype(int)

    total_window_weeks = window_weeks * 2

    weekly["window_start"] = (
        weekly["observation_week"]
        - total_window_weeks
        + 1
    )

    window = weekly[
        (weekly["week"] >= weekly["window_start"])
        & (weekly["week"] <= weekly["observation_week"])
    ].copy()

    window["relative_position"] = (
        window["week"]
        - window["window_start"]
        + 1
    )

    previous = (
        window[
            window["relative_position"].between(
                1,
                window_weeks,
            )
        ]
        .groupby(STUDENT_ENROLLMENT_KEY)["weekly_clicks"]
        .sum()
        .rename("previous_window_clicks")
    )

    recent = (
        window[
            window["relative_position"].between(
                window_weeks + 1,
                total_window_weeks,
            )
        ]
        .groupby(STUDENT_ENROLLMENT_KEY)["weekly_clicks"]
        .sum()
        .rename("recent_window_clicks")
    )

    weeks_available = (
        window
        .groupby(STUDENT_ENROLLMENT_KEY)
        .size()
        .rename("trajectory_weeks_available")
    )

    trajectory = pd.concat(
        [
            previous,
            recent,
            weeks_available,
        ],
        axis=1,
    ).reset_index()

    full_window = (
        trajectory["trajectory_weeks_available"]
        == total_window_weeks
    )

    trajectory[
        "four_week_click_change_pct"
    ] = pd.Series(
        pd.NA,
        index=trajectory.index,
        dtype="Float64",
    )

    valid_baseline = (
        full_window
        & (trajectory["previous_window_clicks"] > 0)
    )

    trajectory.loc[
        valid_baseline,
        "four_week_click_change_pct",
    ] = (
        (
            trajectory.loc[
                valid_baseline,
                "recent_window_clicks",
            ]
            - trajectory.loc[
                valid_baseline,
                "previous_window_clicks",
            ]
        )
        / trajectory.loc[
            valid_baseline,
            "previous_window_clicks",
        ]
        * 100
    )

    trajectory[
        "trajectory_observation_progress"
    ] = observation_progress

    trajectory[
        "trajectory_window_weeks"
    ] = window_weeks

    logger.info(
        "Built engagement trajectory metrics: "
        "%s enrollment rows, %s valid trajectories.",
        len(trajectory),
        trajectory[
            "four_week_click_change_pct"
        ].notna().sum(),
    )

    return trajectory




def build_risk_metrics(
    student_learning_profile: pd.DataFrame,
    cohort_metrics: pd.DataFrame,
    trajectory_metrics: pd.DataFrame,
    risk_config: dict,
) -> pd.DataFrame:
    """
    Build enrollment-level multi-signal risk metrics.
    """

    key = STUDENT_ENROLLMENT_KEY

    risk = (
        student_learning_profile[
            key + [
                "assessment_completion_rate",
                "on_time_submission_rate",
            ]
        ]
        .merge(
            cohort_metrics[
                key + [
                    "clicks_vs_cohort",
                    "score_vs_cohort",
                ]
            ],
            on=key,
            how="left",
            validate="one_to_one",
        )
        .merge(
            trajectory_metrics[
                key + [
                    "four_week_click_change_pct",
                ]
            ],
            on=key,
            how="left",
            validate="one_to_one",
        )
    )

    thresholds = risk_config["thresholds"]
    scoring = risk_config["scoring"]
    evidence_cfg = risk_config["evidence"]
    classes = risk_config["classification"]

    risk["risk_score"] = 0

    signal_specs = [
        (
            "clicks_vs_cohort",
            thresholds["engagement"]["warning_clicks_vs_cohort"],
            thresholds["engagement"]["high_risk_clicks_vs_cohort"],
            scoring["engagement"],
        ),
        (
            "score_vs_cohort",
            thresholds["performance"]["warning_score_vs_cohort"],
            thresholds["performance"]["high_risk_score_vs_cohort"],
            scoring["performance"],
        ),
        (
            "assessment_completion_rate",
            thresholds["assessment"]["warning_completion_rate"],
            thresholds["assessment"]["high_risk_completion_rate"],
            scoring["assessment"],
        ),
        (
            "on_time_submission_rate",
            thresholds["submission"]["warning_on_time_rate"],
            thresholds["submission"]["high_risk_on_time_rate"],
            scoring["submission"],
        ),
        (
            "four_week_click_change_pct",
            thresholds["trajectory"]["warning_four_week_click_change_pct"],
            thresholds["trajectory"]["high_risk_four_week_click_change_pct"],
            scoring["trajectory"],
        ),
    ]

    for metric, warning, high, points in signal_specs:

        risk[f"{metric}_available"] = risk[metric].notna()

        risk[f"{metric}_warning"] = False
        risk[f"{metric}_high_risk"] = False

        available = risk[metric].notna()

        if metric in {
            "assessment_completion_rate",
            "on_time_submission_rate",
        }:
            high_mask = available & (risk[metric] < high)
            warning_mask = (
                available
                & (risk[metric] < warning)
                & ~high_mask
            )
        else:
            high_mask = available & (risk[metric] <= high)
            warning_mask = (
                available
                & (risk[metric] <= warning)
                & ~high_mask
            )

        risk.loc[
            high_mask,
            f"{metric}_high_risk",
        ] = True

        risk.loc[
            warning_mask,
            f"{metric}_warning",
        ] = True

        risk.loc[
            high_mask,
            "risk_score",
        ] += points["high_risk_points"]

        risk.loc[
            warning_mask,
            "risk_score",
        ] += points["warning_points"]

    available_cols = [
        f"{metric}_available"
        for metric, *_ in signal_specs
    ]

    risk["available_signal_count"] = (
        risk[available_cols]
        .sum(axis=1)
        .astype(int)
    )

    risk["evidence_coverage"] = (
        risk["available_signal_count"]
        / evidence_cfg["total_signals"]
    )

    sufficient = (
        risk["available_signal_count"]
        >= evidence_cfg["minimum_signals_for_classification"]
    )

    risk["risk_level"] = pd.Series(
        pd.NA,
        index=risk.index,
        dtype="object",
    )

    risk["risk_level"] = risk["risk_level"].astype("object")

    risk.loc[
        sufficient
        & (
            risk["risk_score"]
            <= classes["low"]["max_score"]
        ),
        "risk_level",
    ] = "Low"

    risk.loc[
        sufficient
        & (
            risk["risk_score"]
            >= classes["moderate"]["min_score"]
        )
        & (
            risk["risk_score"]
            <= classes["moderate"]["max_score"]
        ),
        "risk_level",
    ] = "Moderate"

    risk.loc[
        sufficient
        & (
            risk["risk_score"]
            >= classes["high"]["min_score"]
        ),
        "risk_level",
    ] = "High"

    risk["evidence_status"] = "Sufficient"

    risk.loc[
        risk["available_signal_count"].between(1, 2),
        "evidence_status",
    ] = "Limited"

    risk.loc[
        risk["available_signal_count"] == 0,
        "evidence_status",
    ] = "Insufficient"

    return risk[
        key + [
            "risk_score",
            "risk_level",
            "available_signal_count",
            "evidence_coverage",
            "evidence_status",
            "clicks_vs_cohort",
            "score_vs_cohort",
            "assessment_completion_rate",
            "on_time_submission_rate",
            "four_week_click_change_pct",
        ]
    ]


def validate_risk_metrics(
    risk_metrics: pd.DataFrame,
) -> dict:
    """
    Validate enrollment-level risk metrics.
    """

    key = STUDENT_ENROLLMENT_KEY

    checks = {
        "duplicate_key_count":
            int(risk_metrics.duplicated(key).sum()),

        "negative_risk_score":
            int((risk_metrics["risk_score"] < 0).sum()),

        "invalid_evidence_coverage":
            int(
                (
                    (risk_metrics["evidence_coverage"] < 0)
                    |
                    (risk_metrics["evidence_coverage"] > 1)
                ).sum()
            ),

        "invalid_signal_count":
            int(
                (
                    (risk_metrics["available_signal_count"] < 0)
                    |
                    (risk_metrics["available_signal_count"] > 5)
                ).sum()
            ),

        "classified_with_insufficient_evidence":
            int(
                (
                    (risk_metrics["available_signal_count"] < 3)
                    &
                    risk_metrics["risk_level"].notna()
                ).sum()
            ),
    }

    status = (
        "passed"
        if all(value == 0 for value in checks.values())
        else "failed"
    )

    return {
        "status": status,
        "row_count": len(risk_metrics),
        "checks": checks,
    }


def write_risk_metrics(
    risk_metrics: pd.DataFrame,
    output_path: str | Path,
) -> None:
    """
    Persist risk metrics as Parquet.
    """

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    risk_metrics.to_parquet(
        output_path,
        index=False,
    )

    logger.info(
        "Wrote risk metrics to %s",
        output_path,
    )