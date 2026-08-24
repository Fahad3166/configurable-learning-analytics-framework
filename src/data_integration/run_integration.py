from pathlib import Path
import logging

from src.utils.logging_setup import setup_logging

from src.data_integration.student_enrollment import (
    build_student_enrollment,
    write_student_enrollment,
)
from src.data_integration.assessment_submission import (
    build_assessment_submission,
    write_assessment_submission,
)
from src.data_integration.vle_activity import (
    build_vle_activity,
    write_vle_activity,
)
from src.data_integration.course_presentation import (
    build_course_presentation,
    write_course_presentation,
)
from src.data_integration.analytics_validation import (
    run_analytics_validation,
)


logger = logging.getLogger(__name__)


def main() -> None:
    """
    Run the complete CLAF data integration workflow.
    """

    # ---------------------------------------------------------
    # 1. Initialize logging and resolve directories
    # ---------------------------------------------------------

    setup_logging()

    project_root = Path(__file__).resolve().parents[2]

    clean_dir = (
        project_root
        / "data"
        / "clean"
    )

    analytics_dir = (
        project_root
        / "data"
        / "analytics"
    )

    metadata_dir = (
        project_root
        / "data"
        / "metadata"
    )

    validation_summary_path = (
        metadata_dir
        / "analytics_layer_validation_summary.json"
    )

    analytics_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    metadata_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    logger.info(
        "Starting CLAF data integration pipeline"
    )

    # ---------------------------------------------------------
    # 2. Build Student Enrollment
    # ---------------------------------------------------------

    student_enrollment = build_student_enrollment(
        clean_dir / "student_info.parquet",
        clean_dir / "student_registration.parquet",
    )

    write_student_enrollment(
        student_enrollment,
        analytics_dir / "student_enrollment.parquet",
    )

    logger.info(
        "Completed integration for Student Enrollment"
    )

    # ---------------------------------------------------------
    # 3. Build Assessment Submission
    # ---------------------------------------------------------

    assessment_submission = build_assessment_submission(
        clean_dir / "student_assessment.parquet",
        clean_dir / "assessments.parquet",
    )

    write_assessment_submission(
        assessment_submission,
        analytics_dir / "assessment_submission.parquet",
    )

    logger.info(
        "Completed integration for Assessment Submission"
    )

    # ---------------------------------------------------------
    # 4. Build VLE Activity
    # ---------------------------------------------------------

    vle_activity = build_vle_activity(
        clean_dir / "student_vle.parquet",
    )

    write_vle_activity(
        vle_activity,
        analytics_dir / "vle_activity.parquet",
    )

    logger.info(
        "Completed integration for VLE Activity"
    )

    # ---------------------------------------------------------
    # 5. Build Course Presentation
    # ---------------------------------------------------------

    course_presentation = build_course_presentation(
        clean_dir / "courses.parquet",
    )

    write_course_presentation(
        course_presentation,
        analytics_dir / "course_presentation.parquet",
    )

    logger.info(
        "Completed integration for Course Presentation"
    )

    # ---------------------------------------------------------
    # 6. Validate analytics layer
    # ---------------------------------------------------------

    summary = run_analytics_validation(
        analytics_dir,
        validation_summary_path,
    )

    logger.info(
        "Analytics-layer validation completed with status '%s'",
        summary["overall_status"],
    )

    logger.info(
        "Analytics ready: %s",
        summary["analytics_ready"],
    )

    # ---------------------------------------------------------
    # 7. Complete pipeline
    # ---------------------------------------------------------

    logger.info(
        "CLAF data integration pipeline completed"
    )


if __name__ == "__main__":
    main()