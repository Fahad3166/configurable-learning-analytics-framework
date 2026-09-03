from pathlib import Path
import logging

import pandas as pd


logger = logging.getLogger(__name__)


STUDENT_ENROLLMENT_KEY = [
    "id_student",
    "code_module",
    "code_presentation",
]

COHORT_KEY = [
    "code_module",
    "code_presentation",
]


def _add_leave_one_out_mean(
    frame: pd.DataFrame,
    measure: str,
    mean_output: str,
    count_output: str,
) -> pd.DataFrame:
    """
    Add leave-one-out cohort mean and peer evidence count.

    Missing measure values do not contribute to the cohort benchmark.

    For a student with an observed value:
        peer_count = cohort observed count - 1

    For a student with a missing value:
        peer_count = cohort observed count

    The benchmark remains missing when no peer evidence is available.
    """

    result = frame.copy()

    cohort_count = (
        result.groupby(COHORT_KEY)[measure]
        .transform("count")
    )

    cohort_sum = (
        result.groupby(COHORT_KEY)[measure]
        .transform("sum")
    )

    has_value = result[measure].notna()

    peer_count = cohort_count - has_value.astype(int)

    peer_sum = cohort_sum.copy()
    peer_sum.loc[has_value] = (
        cohort_sum.loc[has_value]
        - result.loc[has_value, measure]
    )

    peer_mean = peer_sum / peer_count

    peer_mean = peer_mean.where(
        peer_count > 0
    )

    result[count_output] = peer_count.astype("Int64")
    result[mean_output] = peer_mean.astype("Float64")

    return result


def build_cohort_metrics(
    student_learning_profile: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build student-level cohort benchmark metrics.

    Grain:
        id_student + code_module + code_presentation

    Cohort:
        code_module + code_presentation

    Benchmarks use leave-one-out means so that a student's own
    observation does not influence the peer benchmark against which
    that student is compared.
    """

    key = STUDENT_ENROLLMENT_KEY

    duplicate_count = (
        student_learning_profile
        .duplicated(key)
        .sum()
    )

    if duplicate_count:
        raise ValueError(
            "Student learning profile contains "
            f"{duplicate_count} duplicate enrollment keys."
        )

    required_columns = [
        *key,
        "total_clicks",
        "mean_score",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in student_learning_profile.columns
    ]

    if missing_columns:
        raise ValueError(
            "Student learning profile is missing required columns: "
            f"{missing_columns}"
        )

    metrics = student_learning_profile[
        required_columns
    ].copy()

    # -------------------------------------------------------------
    # Engagement cohort benchmark
    # -------------------------------------------------------------

    metrics = _add_leave_one_out_mean(
        frame=metrics,
        measure="total_clicks",
        mean_output="cohort_mean_clicks",
        count_output="cohort_engagement_count",
    )

    metrics["clicks_vs_cohort"] = (
        metrics["total_clicks"]
        - metrics["cohort_mean_clicks"]
    ).astype("Float64")

    # -------------------------------------------------------------
    # Score cohort benchmark
    # -------------------------------------------------------------

    metrics = _add_leave_one_out_mean(
        frame=metrics,
        measure="mean_score",
        mean_output="cohort_mean_score",
        count_output="cohort_score_count",
    )

    metrics["score_vs_cohort"] = (
        metrics["mean_score"]
        - metrics["cohort_mean_score"]
    ).astype("Float64")

    # Keep only metric outputs and authoritative grain.
    metrics = metrics[
        [
            *key,
            "cohort_mean_clicks",
            "cohort_engagement_count",
            "clicks_vs_cohort",
            "cohort_mean_score",
            "cohort_score_count",
            "score_vs_cohort",
        ]
    ]

    logger.info(
        "Built cohort metrics: %s rows, %s columns",
        len(metrics),
        len(metrics.columns),
    )

    return metrics


def validate_cohort_metrics(
    cohort_metrics: pd.DataFrame,
) -> dict:
    """
    Validate cohort benchmark metric structure and values.
    """

    key = STUDENT_ENROLLMENT_KEY

    checks = {
        "duplicate_key_count":
            int(cohort_metrics.duplicated(key).sum()),

        "negative_engagement_peer_count":
            int(
                (
                    cohort_metrics[
                        "cohort_engagement_count"
                    ].dropna() < 0
                ).sum()
            ),

        "negative_score_peer_count":
            int(
                (
                    cohort_metrics[
                        "cohort_score_count"
                    ].dropna() < 0
                ).sum()
            ),

        "nonfinite_cohort_mean_clicks":
            int(
                (
                    ~cohort_metrics[
                        "cohort_mean_clicks"
                    ].dropna().map(
                        lambda value: pd.notna(value)
                        and float("-inf") < value < float("inf")
                    )
                ).sum()
            ),

        "nonfinite_clicks_vs_cohort":
            int(
                (
                    ~cohort_metrics[
                        "clicks_vs_cohort"
                    ].dropna().map(
                        lambda value: pd.notna(value)
                        and float("-inf") < value < float("inf")
                    )
                ).sum()
            ),

        "invalid_cohort_mean_score":
            int(
                (
                    (
                        cohort_metrics[
                            "cohort_mean_score"
                        ].dropna() < 0
                    )
                    |
                    (
                        cohort_metrics[
                            "cohort_mean_score"
                        ].dropna() > 100
                    )
                ).sum()
            ),

        "nonfinite_score_vs_cohort":
            int(
                (
                    ~cohort_metrics[
                        "score_vs_cohort"
                    ].dropna().map(
                        lambda value: pd.notna(value)
                        and float("-inf") < value < float("inf")
                    )
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
        "row_count": len(cohort_metrics),
        "checks": checks,
    }


def write_cohort_metrics(
    cohort_metrics: pd.DataFrame,
    output_path: str | Path,
) -> None:
    """
    Persist cohort metrics as Parquet.
    """

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    cohort_metrics.to_parquet(
        output_path,
        index=False,
    )

    logger.info(
        "Wrote cohort metrics to %s",
        output_path,
    )