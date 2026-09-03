from pathlib import Path
import logging

import pandas as pd
import yaml

from src.utils.logging_setup import setup_logging

from src.metrics.engagement import (
    build_engagement_metrics,
    validate_engagement_metrics,
    write_engagement_metrics,
    build_weekly_engagement_metrics,
)

from src.metrics.student_week import (
    build_student_week_spine,
    build_student_week_engagement,
    add_weekly_engagement_change,
    validate_student_week_engagement,
    write_student_week_engagement,
)

from src.metrics.assessment import (
    load_assessment_inputs,
    build_assessment_definitions,
    build_assessment_opportunities,
    attach_assessment_submissions,
    build_assessment_metrics,
    validate_assessment_metrics,
    write_assessment_metrics,
)

from src.metrics.student_profile import (
    build_student_learning_profile,
    validate_student_learning_profile,
    write_student_learning_profile,
)

from src.metrics.cohort import (
    build_cohort_metrics,
    validate_cohort_metrics,
    write_cohort_metrics,
)

from src.metrics.risk import (
    build_engagement_trajectory,
    build_risk_metrics,
    validate_risk_metrics,
    write_risk_metrics,
)

from src.metrics.improvement import (
    build_assessment_progression,
    add_assessment_improvement_category,
    validate_assessment_improvement,
    write_assessment_improvement,
)


logger = logging.getLogger(__name__)


def require_passed(
    name: str,
    validation: dict,
) -> None:
    """
    Stop the metrics pipeline when a validation stage fails.
    """

    if validation["status"] != "passed":
        raise ValueError(
            f"{name} validation failed: {validation}"
        )

    logger.info(
        "%s validation passed",
        name,
    )


def main() -> None:
    """
    Run the complete CLAF metrics and analytics engine.
    """

    project_root = Path(__file__).resolve().parents[2]

    setup_logging(
        project_root / "configs" / "logging.yaml"
    )

    clean_dir = project_root / "data" / "clean"
    analytics_dir = project_root / "data" / "analytics"
    metrics_dir = project_root / "data" / "metrics"

    metrics_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ---------------------------------------------------------
    # Input paths
    # ---------------------------------------------------------

    assessments_path = (
        clean_dir / "assessments.parquet"
    )

    student_enrollment_path = (
        analytics_dir / "student_enrollment.parquet"
    )

    assessment_submission_path = (
        analytics_dir / "assessment_submission.parquet"
    )

    vle_activity_path = (
        analytics_dir / "vle_activity.parquet"
    )

    course_presentation_path = (
        analytics_dir / "course_presentation.parquet"
    )

    # ---------------------------------------------------------
    # Output paths
    # ---------------------------------------------------------

    engagement_output_path = (
        metrics_dir / "engagement_metrics.parquet"
    )

    student_week_output_path = (
        metrics_dir / "student_week_engagement.parquet"
    )

    assessment_output_path = (
        metrics_dir / "assessment_metrics.parquet"
    )

    profile_output_path = (
        metrics_dir / "student_learning_profile.parquet"
    )

    cohort_output_path = (
        metrics_dir / "cohort_metrics.parquet"
    )

    risk_output_path = (
        metrics_dir / "risk_metrics.parquet"
    )

    improvement_output_path = (
        metrics_dir / "assessment_improvement.parquet"
    )

    # ---------------------------------------------------------
    # Configuration
    # ---------------------------------------------------------

    with open(
        project_root / "configs" / "kpis.yaml"
    ) as f:
        config = yaml.safe_load(f)

    risk_config = config["risk"]
    improvement_config = config["improvement"]

    logger.info(
        "Starting CLAF metrics and analytics engine"
    )

    # =========================================================
    # 1. Engagement metrics
    # =========================================================

    logger.info(
        "Stage 1: Building engagement metrics"
    )

    engagement_metrics = build_engagement_metrics(
        vle_activity_path
    )

    engagement_validation = (
        validate_engagement_metrics(
            engagement_metrics
        )
    )

    require_passed(
        "Engagement metrics",
        engagement_validation,
    )

    write_engagement_metrics(
        engagement_metrics,
        engagement_output_path,
    )

    # =========================================================
    # 2. Student-week engagement
    # =========================================================

    logger.info(
        "Stage 2: Building student-week engagement"
    )

    observed_weekly_engagement = (
        build_weekly_engagement_metrics(
            vle_activity_path
        )
    )

    student_week_spine = (
        build_student_week_spine(
            student_enrollment_path,
            course_presentation_path,
        )
    )

    student_week_engagement = (
        build_student_week_engagement(
            student_week_spine,
            observed_weekly_engagement,
        )
    )

    student_week_engagement = (
        add_weekly_engagement_change(
            student_week_engagement
        )
    )

    student_week_validation = (
        validate_student_week_engagement(
            student_week_engagement
        )
    )

    require_passed(
        "Student-week engagement",
        student_week_validation,
    )

    write_student_week_engagement(
        student_week_engagement,
        student_week_output_path,
    )

    # =========================================================
    # 3. Assessment metrics
    # =========================================================

    logger.info(
        "Stage 3: Building assessment metrics"
    )

    (
        assessment_submission,
        student_enrollment,
        course_presentation,
    ) = load_assessment_inputs(
        assessment_submission_path,
        student_enrollment_path,
        course_presentation_path,
    )

    assessments = pd.read_parquet(
        assessments_path
    )

    assessment_definitions = (
        build_assessment_definitions(
            assessments
        )
    )

    assessment_opportunities = (
        build_assessment_opportunities(
            student_enrollment,
            assessment_definitions,
            course_presentation,
        )
    )

    assessment_status = (
        attach_assessment_submissions(
            assessment_opportunities,
            assessment_submission,
        )
    )

    assessment_metrics = (
        build_assessment_metrics(
            assessment_status,
            assessment_submission,
        )
    )

    assessment_validation = (
        validate_assessment_metrics(
            assessment_metrics
        )
    )

    require_passed(
        "Assessment metrics",
        assessment_validation,
    )

    write_assessment_metrics(
        assessment_metrics,
        assessment_output_path,
    )

    # =========================================================
    # 4. Student learning profile
    # =========================================================

    logger.info(
        "Stage 4: Building student learning profile"
    )

    student_learning_profile = (
        build_student_learning_profile(
            student_enrollment,
            engagement_metrics,
            assessment_metrics,
        )
    )

    profile_validation = (
        validate_student_learning_profile(
            student_learning_profile
        )
    )

    require_passed(
        "Student learning profile",
        profile_validation,
    )

    write_student_learning_profile(
        student_learning_profile,
        profile_output_path,
    )

    # =========================================================
    # 5. Cohort metrics
    # =========================================================

    logger.info(
        "Stage 5: Building cohort metrics"
    )

    cohort_metrics = build_cohort_metrics(
        student_learning_profile
    )

    cohort_validation = (
        validate_cohort_metrics(
            cohort_metrics
        )
    )

    require_passed(
        "Cohort metrics",
        cohort_validation,
    )

    write_cohort_metrics(
        cohort_metrics,
        cohort_output_path,
    )

    # =========================================================
    # 6. Risk metrics
    # =========================================================

    logger.info(
        "Stage 6: Building risk metrics"
    )

    trajectory_config = risk_config[
        "thresholds"
    ]["trajectory"]

    trajectory_metrics = (
        build_engagement_trajectory(
            student_week_engagement,
            course_presentation,
            observation_progress=trajectory_config[
                "observation_progress"
            ],
            window_weeks=trajectory_config[
                "window_weeks"
            ],
        )
    )

    risk_metrics = build_risk_metrics(
        student_learning_profile,
        cohort_metrics,
        trajectory_metrics,
        risk_config,
    )

    risk_validation = (
        validate_risk_metrics(
            risk_metrics
        )
    )

    require_passed(
        "Risk metrics",
        risk_validation,
    )

    write_risk_metrics(
        risk_metrics,
        risk_output_path,
    )

    # =========================================================
    # 7. Assessment improvement
    # =========================================================

    logger.info(
        "Stage 7: Building assessment improvement"
    )

    assessment_improvement = (
        build_assessment_progression(
            assessment_submission,
            student_enrollment,
            course_presentation,
            improvement_config,
        )
    )

    assessment_improvement = (
        add_assessment_improvement_category(
            assessment_improvement,
            improvement_config,
        )
    )

    improvement_validation = (
        validate_assessment_improvement(
            assessment_improvement
        )
    )

    require_passed(
        "Assessment improvement",
        improvement_validation,
    )

    write_assessment_improvement(
        assessment_improvement,
        improvement_output_path,
    )

    # =========================================================
    # Complete
    # =========================================================

    logger.info(
        "CLAF metrics and analytics engine completed successfully"
    )

    print()
    print("CLAF METRICS ENGINE")
    print("=" * 70)
    print("Status: PASSED")
    print()
    print(
        f"Engagement metrics: "
        f"{len(engagement_metrics):,}"
    )
    print(
        f"Student-week engagement: "
        f"{len(student_week_engagement):,}"
    )
    print(
        f"Assessment metrics: "
        f"{len(assessment_metrics):,}"
    )
    print(
        f"Student learning profiles: "
        f"{len(student_learning_profile):,}"
    )
    print(
        f"Cohort metrics: "
        f"{len(cohort_metrics):,}"
    )
    print(
        f"Risk metrics: "
        f"{len(risk_metrics):,}"
    )
    print(
        f"Assessment improvement: "
        f"{len(assessment_improvement):,}"
    )


if __name__ == "__main__":
    main()