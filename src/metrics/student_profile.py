from pathlib import Path
import logging

import pandas as pd


logger = logging.getLogger(__name__)


STUDENT_ENROLLMENT_KEY = [
    "id_student",
    "code_module",
    "code_presentation",
]


def build_student_learning_profile(
    student_enrollment: pd.DataFrame,
    engagement_metrics: pd.DataFrame,
    assessment_metrics: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build the unified student learning profile.

    Grain:
        id_student + code_module + code_presentation

    The student enrollment table is the authoritative population.

    Missing-value semantics
    -----------------------
    Engagement:
    - Students who withdrew before day 0 have no valid course-period
      participation window. Their engagement metrics remain missing.
    - Students eligible from day 0 onward but with no VLE activity receive
      zero for additive engagement counts.
    - Metrics requiring observed activity, such as average clicks per active
      day and last activity day, remain missing when no activity exists.

    Assessment:
    - Students with no eligible observable assessment opportunity retain
      missing assessment metrics.
    - Existing assessment metric rows preserve their calculated zero,
      non-zero, and missing values.
    """

    key = STUDENT_ENROLLMENT_KEY

    # ------------------------------------------------------------------
    # Validate input grains
    # ------------------------------------------------------------------

    for name, frame in [
        ("student_enrollment", student_enrollment),
        ("engagement_metrics", engagement_metrics),
        ("assessment_metrics", assessment_metrics),
    ]:
        duplicate_count = frame.duplicated(key).sum()

        if duplicate_count:
            raise ValueError(
                f"{name} contains {duplicate_count} duplicate "
                f"student-enrollment keys."
            )

    # ------------------------------------------------------------------
    # Start from authoritative enrollment population
    # ------------------------------------------------------------------

    profile = student_enrollment.copy()

    # ------------------------------------------------------------------
    # Attach engagement metrics
    # ------------------------------------------------------------------

    profile = profile.merge(
        engagement_metrics,
        on=key,
        how="left",
        validate="one_to_one",
        indicator="_engagement_merge",
    )

    has_engagement_metrics = profile["_engagement_merge"].eq("both")

    eligible_course_period = (
        profile["date_unregistration"].isna()
        | profile["date_unregistration"].ge(0)
    )

    zero_engagement = (
        ~has_engagement_metrics
        & eligible_course_period
    )

    # Additive engagement metrics have meaningful zeros when the student
    # had an eligible course-period window but recorded no VLE activity.
    for column in ["total_clicks", "active_days"]:
        if column in profile.columns:
            profile.loc[zero_engagement, column] = 0

    # avg_clicks_per_active_day and last_activity_day intentionally remain
    # missing when no activity was observed.

    profile = profile.drop(columns="_engagement_merge")

    # ------------------------------------------------------------------
    # Attach assessment metrics
    # ------------------------------------------------------------------

    profile = profile.merge(
        assessment_metrics,
        on=key,
        how="left",
        validate="one_to_one",
    )

    # Assessment missingness is intentionally preserved.
    #
    # No assessment row means the enrollment had no eligible observable
    # assessment opportunity. It must not be interpreted as zero
    # completion or zero performance.

    # ------------------------------------------------------------------
    # Final grain validation
    # ------------------------------------------------------------------

    duplicate_count = profile.duplicated(key).sum()

    if duplicate_count:
        raise ValueError(
            "Student learning profile contains duplicate "
            f"student-enrollment keys: {duplicate_count}"
        )

    if len(profile) != len(student_enrollment):
        raise ValueError(
            "Student learning profile row count does not match "
            "student enrollment population."
        )

    logger.info(
        "Built student learning profile: %s rows, %s columns",
        len(profile),
        len(profile.columns),
    )

    return profile


def validate_student_learning_profile(
    profile: pd.DataFrame,
) -> dict:
    """
    Validate structural and metric-range properties of the unified
    student learning profile.
    """

    key = STUDENT_ENROLLMENT_KEY

    checks = {
        "duplicate_key_count":
            int(profile.duplicated(key).sum()),

        "negative_total_clicks":
            int(
                (
                    profile["total_clicks"].dropna() < 0
                ).sum()
            ),

        "negative_active_days":
            int(
                (
                    profile["active_days"].dropna() < 0
                ).sum()
            ),

        "invalid_assessment_completion_rate":
            int(
                (
                    (
                        profile[
                            "assessment_completion_rate"
                        ].dropna() < 0
                    )
                    |
                    (
                        profile[
                            "assessment_completion_rate"
                        ].dropna() > 1
                    )
                ).sum()
            ),

        "invalid_mean_score":
            int(
                (
                    (
                        profile["mean_score"].dropna() < 0
                    )
                    |
                    (
                        profile["mean_score"].dropna() > 100
                    )
                ).sum()
            ),

        "invalid_coursework_weighted_score":
            int(
                (
                    (
                        profile[
                            "coursework_weighted_score"
                        ].dropna() < 0
                    )
                    |
                    (
                        profile[
                            "coursework_weighted_score"
                        ].dropna() > 100
                    )
                ).sum()
            ),

        "invalid_coursework_score_coverage":
            int(
                (
                    (
                        profile[
                            "coursework_score_coverage"
                        ].dropna() < 0
                    )
                    |
                    (
                        profile[
                            "coursework_score_coverage"
                        ].dropna() > 1
                    )
                ).sum()
            ),

        "invalid_exam_score":
            int(
                (
                    (
                        profile["exam_score"].dropna() < 0
                    )
                    |
                    (
                        profile["exam_score"].dropna() > 100
                    )
                ).sum()
            ),

        "invalid_on_time_submission_rate":
            int(
                (
                    (
                        profile[
                            "on_time_submission_rate"
                        ].dropna() < 0
                    )
                    |
                    (
                        profile[
                            "on_time_submission_rate"
                        ].dropna() > 1
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
        "row_count": len(profile),
        "checks": checks,
    }


def write_student_learning_profile(
    profile: pd.DataFrame,
    output_path: str | Path,
) -> None:
    """
    Persist the student learning profile as Parquet.
    """

    output_path = Path(output_path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    profile.to_parquet(
        output_path,
        index=False,
    )

    logger.info(
        "Wrote student learning profile to %s",
        output_path,
    )