import logging
import pandas as pd
from pathlib import Path



logger = logging.getLogger(__name__)


STUDENT_ENROLLMENT_KEY = [
    "id_student",
    "code_module",
    "code_presentation",
]


def build_assessment_progression(
    assessment_submission: pd.DataFrame,
    student_enrollment: pd.DataFrame,
    course_presentation: pd.DataFrame,
    improvement_config: dict,
) -> pd.DataFrame:
    """
    Build enrollment-level assessment progression metrics.

    The metric compares the mean score of the most recent configured
    assessment window with the immediately preceding assessment window
    at a configurable course-progress observation point.
    """

    cfg = improvement_config["assessment_progression"]

    observation_progress = cfg["observation_progress"]
    window_assessments = cfg["window_assessments"]
    minimum_scored_assessments = cfg[
        "minimum_scored_assessments"
    ]
    assessment_types = cfg["assessment_types"]

    if not 0 < observation_progress <= 1:
        raise ValueError(
            "observation_progress must be greater than 0 "
            "and less than or equal to 1."
        )

    if window_assessments <= 0:
        raise ValueError(
            "window_assessments must be greater than 0."
        )

    expected_minimum = window_assessments * 2

    if minimum_scored_assessments < expected_minimum:
        raise ValueError(
            "minimum_scored_assessments must be at least "
            "two assessment windows."
        )

    required_assessment_columns = {
        *STUDENT_ENROLLMENT_KEY,
        "id_assessment",
        "assessment_type",
        "score",
        "date",
    }

    missing = (
        required_assessment_columns
        - set(assessment_submission.columns)
    )

    if missing:
        raise ValueError(
            "assessment_submission is missing required columns: "
            f"{sorted(missing)}"
        )

    coursework = assessment_submission[
        assessment_submission["assessment_type"].isin(
            assessment_types
        )
        & assessment_submission["score"].notna()
        & assessment_submission["date"].notna()
    ].copy()

    coursework = coursework.merge(
        student_enrollment[
            STUDENT_ENROLLMENT_KEY
            + ["date_unregistration"]
        ],
        on=STUDENT_ENROLLMENT_KEY,
        how="left",
        validate="many_to_one",
    )

    coursework = coursework.merge(
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

    if coursework[
        "module_presentation_length"
    ].isna().any():
        raise ValueError(
            "Some assessment rows are missing presentation length."
        )

    eligible = (
        coursework["date_unregistration"].isna()
        | (
            coursework["date"]
            <= coursework["date_unregistration"]
        )
    )

    coursework = coursework[
        eligible
    ].copy()

    coursework["observation_day"] = (
        coursework["module_presentation_length"]
        * observation_progress
    ).round()

    coursework = coursework[
        coursework["date"]
        <= coursework["observation_day"]
    ].copy()

    coursework = coursework.sort_values(
        STUDENT_ENROLLMENT_KEY
        + [
            "date",
            "id_assessment",
        ]
    )

    coursework["assessment_position"] = (
        coursework
        .groupby(STUDENT_ENROLLMENT_KEY)
        .cumcount()
        + 1
    )

    coursework["scored_assessment_count"] = (
        coursework
        .groupby(STUDENT_ENROLLMENT_KEY)[
            "id_assessment"
        ]
        .transform("size")
    )

    usable = coursework[
        coursework["scored_assessment_count"]
        >= minimum_scored_assessments
    ].copy()

    usable["relative_from_end"] = (
        usable["scored_assessment_count"]
        - usable["assessment_position"]
    )

    latest_window_limit = (
        window_assessments - 1
    )

    previous_window_start = window_assessments
    previous_window_end = (
        window_assessments * 2 - 1
    )

    recent = (
        usable[
            usable["relative_from_end"]
            .between(
                0,
                latest_window_limit,
            )
        ]
        .groupby(
            STUDENT_ENROLLMENT_KEY
        )["score"]
        .mean()
        .rename("recent_assessment_mean")
    )

    previous = (
        usable[
            usable["relative_from_end"]
            .between(
                previous_window_start,
                previous_window_end,
            )
        ]
        .groupby(
            STUDENT_ENROLLMENT_KEY
        )["score"]
        .mean()
        .rename("previous_assessment_mean")
    )

    progression = pd.concat(
        [
            previous,
            recent,
        ],
        axis=1,
    ).reset_index()

    progression["assessment_score_change"] = (
        progression["recent_assessment_mean"]
        - progression["previous_assessment_mean"]
    )

    progression[
        "assessment_observation_progress"
    ] = observation_progress

    progression[
        "assessment_window_size"
    ] = window_assessments

    if progression.duplicated(
        STUDENT_ENROLLMENT_KEY
    ).any():
        raise ValueError(
            "Duplicate enrollment keys found in "
            "assessment progression output."
        )

    logger.info(
        "Built assessment progression metrics: "
        "%s enrollment rows.",
        len(progression),
    )

    return progression


def add_assessment_improvement_category(
    assessment_progression: pd.DataFrame,
    improvement_config: dict,
) -> pd.DataFrame:
    """
    Classify assessment progression as Improved, Stable, or Declined.

    Classification thresholds are read from the improvement
    configuration rather than hard-coded in the metrics engine.
    """

    cfg = improvement_config["assessment_progression"]

    improvement_threshold = cfg[
        "improvement_threshold_points"
    ]

    decline_threshold = cfg[
        "decline_threshold_points"
    ]

    if decline_threshold >= improvement_threshold:
        raise ValueError(
            "decline_threshold_points must be lower than "
            "improvement_threshold_points."
        )

    result = assessment_progression.copy()

    change = result["assessment_score_change"]

    result["assessment_improvement_status"] = "Stable"

    result.loc[
        change >= improvement_threshold,
        "assessment_improvement_status",
    ] = "Improved"

    result.loc[
        change <= decline_threshold,
        "assessment_improvement_status",
    ] = "Declined"

    result["assessment_improvement_status"] = (
        result["assessment_improvement_status"].astype("string")
    )

    logger.info(
        "Added assessment improvement categories "
        "using thresholds %s and %s.",
        improvement_threshold,
        decline_threshold,
    )

    return result


from pathlib import Path


def validate_assessment_improvement(
    assessment_improvement: pd.DataFrame,
) -> dict:
    """
    Validate assessment improvement metrics.
    """

    duplicate_key_count = (
        assessment_improvement.duplicated(
            STUDENT_ENROLLMENT_KEY
        ).sum()
    )

    missing_change_count = (
        assessment_improvement[
            "assessment_score_change"
        ].isna().sum()
    )

    invalid_status_count = (
        ~assessment_improvement[
            "assessment_improvement_status"
        ].isin(
            [
                "Improved",
                "Stable",
                "Declined",
            ]
        )
    ).sum()

    invalid_previous_score_count = (
        (
            assessment_improvement[
                "previous_assessment_mean"
            ] < 0
        )
        | (
            assessment_improvement[
                "previous_assessment_mean"
            ] > 100
        )
    ).sum()

    invalid_recent_score_count = (
        (
            assessment_improvement[
                "recent_assessment_mean"
            ] < 0
        )
        | (
            assessment_improvement[
                "recent_assessment_mean"
            ] > 100
        )
    ).sum()

    checks = {
        "duplicate_key_count": int(
            duplicate_key_count
        ),
        "missing_change_count": int(
            missing_change_count
        ),
        "invalid_status_count": int(
            invalid_status_count
        ),
        "invalid_previous_score_count": int(
            invalid_previous_score_count
        ),
        "invalid_recent_score_count": int(
            invalid_recent_score_count
        ),
    }

    passed = all(
        value == 0
        for value in checks.values()
    )

    return {
        "status": (
            "passed"
            if passed
            else "failed"
        ),
        "row_count": len(
            assessment_improvement
        ),
        "checks": checks,
    }


def write_assessment_improvement(
    assessment_improvement: pd.DataFrame,
    output_path: str | Path,
) -> None:
    """
    Persist assessment improvement metrics to Parquet.
    """

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    assessment_improvement.to_parquet(
        output_path,
        index=False,
    )

    logger.info(
        "Wrote assessment improvement metrics "
        "to %s.",
        output_path,
    )