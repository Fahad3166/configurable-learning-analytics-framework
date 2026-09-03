from pathlib import Path
import logging

from src.utils.logging_setup import setup_logging
from src.metrics.engagement import (
    build_engagement_metrics,
    validate_engagement_metrics,
    write_engagement_metrics,
    build_weekly_engagement_metrics,
    build_continuous_weekly_engagement,
    add_weekly_engagement_change,
    validate_weekly_engagement_metrics,
    write_weekly_engagement_metrics,
)


logger = logging.getLogger(__name__)


def main() -> None:
    """
    Run the CLAF engagement metrics pipeline.
    """

    project_root = Path(__file__).resolve().parents[2]

    setup_logging(
        project_root / "configs" / "logging.yaml"
    )

    analytics_dir = project_root / "data" / "analytics"
    metrics_dir = project_root / "data" / "metrics"

    vle_activity_path = (
        analytics_dir / "vle_activity.parquet"
    )

    course_presentation_path = (
        analytics_dir / "course_presentation.parquet"
    )

    engagement_output_path = (
        metrics_dir / "engagement_metrics.parquet"
    )

    weekly_output_path = (
        metrics_dir / "weekly_engagement_metrics.parquet"
    )

    logger.info(
        "Starting CLAF engagement metrics pipeline"
    )

    # Student-level engagement metrics
    engagement_metrics = build_engagement_metrics(
        vle_activity_path
    )

    engagement_validation = validate_engagement_metrics(
        engagement_metrics
    )

    if engagement_validation["status"] != "passed":
        raise ValueError(
            "Student-level engagement validation failed: "
            f"{engagement_validation}"
        )

    write_engagement_metrics(
        engagement_metrics,
        engagement_output_path,
    )

    logger.info(
        "Student-level engagement validation status: %s",
        engagement_validation["status"],
    )

    # Weekly engagement metrics
    observed_weekly_metrics = (
        build_weekly_engagement_metrics(
            vle_activity_path
        )
    )

    continuous_weekly_metrics = (
        build_continuous_weekly_engagement(
            observed_weekly_metrics,
            course_presentation_path,
        )
    )

    weekly_metrics = add_weekly_engagement_change(
        continuous_weekly_metrics
    )

    weekly_validation = (
        validate_weekly_engagement_metrics(
            weekly_metrics
        )
    )

    if weekly_validation["status"] != "passed":
        raise ValueError(
            "Weekly engagement validation failed: "
            f"{weekly_validation}"
        )

    write_weekly_engagement_metrics(
        weekly_metrics,
        weekly_output_path,
    )

    logger.info(
        "Weekly engagement validation status: %s",
        weekly_validation["status"],
    )

    logger.info(
        "CLAF engagement metrics pipeline completed"
    )


if __name__ == "__main__":
    main()