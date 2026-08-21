from pathlib import Path
import logging

from src.utils.config_loader import load_yaml_config
from src.utils.logging_setup import setup_logging

from src.data_preprocessing.courses import (
    preprocess_courses,
    write_clean_courses,
)
from src.data_preprocessing.student_info import (
    preprocess_student_info,
    write_clean_student_info,
)
from src.data_preprocessing.student_registration import (
    preprocess_student_registration,
    write_clean_student_registration,
)
from src.data_preprocessing.assessments import (
    preprocess_assessments,
    write_clean_assessments,
)
from src.data_preprocessing.student_assessment import (
    preprocess_student_assessment,
    write_clean_student_assessment,
)
from src.data_preprocessing.vle import (
    preprocess_vle,
    write_clean_vle,
)
from src.data_preprocessing.student_vle import (
    preprocess_student_vle,
    write_clean_student_vle,
)
from src.data_preprocessing.clean_layer_validation import (
    run_clean_layer_validation,
)


logger = logging.getLogger(__name__)


def main() -> None:
    """
    Run the complete CLAF preprocessing workflow.
    """

    # ---------------------------------------------------------
    # 1. Initialize logging and configuration
    # ---------------------------------------------------------

    setup_logging()

    project_root = Path(__file__).resolve().parents[2]

    config = load_yaml_config(
        project_root / "configs" / "config.yaml"
    )

    preprocessing_rules = load_yaml_config(
        project_root / "configs" / "preprocessing_rules.yaml"
    )

    logger.info(
        "Starting CLAF preprocessing pipeline"
    )

    logger.info(
        "Loaded preprocessing configuration for %s tables",
        len(preprocessing_rules)
    )

    # ---------------------------------------------------------
    # 2. Resolve pipeline directories
    # ---------------------------------------------------------

    raw_dir = (
        project_root
        / config["sources"]["oulad"]["base_path"]
    )

    clean_dir = (
        project_root
        / config["data"]["clean_dir"]
    )

    metadata_dir = (
        project_root
        / config["data"]["metadata_dir"]
    )

    validation_summary_path = (
        metadata_dir
        / "clean_layer_validation_summary.json"
    )

    clean_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    metadata_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # ---------------------------------------------------------
    # 3. Preprocess courses
    # ---------------------------------------------------------

    courses_rules = preprocessing_rules["courses"]

    courses_df = preprocess_courses(
        raw_dir / courses_rules["source_file"],
        courses_rules
    )

    write_clean_courses(
        courses_df,
        clean_dir / courses_rules["output_file"]
    )

    logger.info(
        "Completed preprocessing for courses"
    )

    # ---------------------------------------------------------
    # 4. Preprocess studentInfo
    # ---------------------------------------------------------

    student_info_rules = preprocessing_rules[
        "student_info"
    ]

    student_info_df = preprocess_student_info(
        raw_dir / student_info_rules["source_file"],
        student_info_rules
    )

    write_clean_student_info(
        student_info_df,
        clean_dir / student_info_rules["output_file"]
    )

    logger.info(
        "Completed preprocessing for student_info"
    )

    # ---------------------------------------------------------
    # 5. Preprocess studentRegistration
    # ---------------------------------------------------------

    student_registration_rules = preprocessing_rules[
        "student_registration"
    ]

    student_registration_df = preprocess_student_registration(
        raw_dir / student_registration_rules["source_file"],
        student_registration_rules
    )

    write_clean_student_registration(
        student_registration_df,
        clean_dir / student_registration_rules["output_file"]
    )

    logger.info(
        "Completed preprocessing for student_registration"
    )

    # ---------------------------------------------------------
    # 6. Preprocess assessments
    # ---------------------------------------------------------

    assessments_rules = preprocessing_rules[
        "assessments"
    ]

    assessments_df = preprocess_assessments(
        raw_dir / assessments_rules["source_file"],
        assessments_rules
    )

    write_clean_assessments(
        assessments_df,
        clean_dir / assessments_rules["output_file"]
    )

    logger.info(
        "Completed preprocessing for assessments"
    )

    # ---------------------------------------------------------
    # 7. Preprocess studentAssessment
    # ---------------------------------------------------------

    student_assessment_rules = preprocessing_rules[
        "student_assessment"
    ]

    student_assessment_df = preprocess_student_assessment(
        raw_dir / student_assessment_rules["source_file"],
        student_assessment_rules
    )

    write_clean_student_assessment(
        student_assessment_df,
        clean_dir / student_assessment_rules["output_file"]
    )

    logger.info(
        "Completed preprocessing for student_assessment"
    )

    # ---------------------------------------------------------
    # 8. Preprocess VLE metadata
    # ---------------------------------------------------------

    vle_rules = preprocessing_rules["vle"]

    vle_df = preprocess_vle(
        raw_dir / vle_rules["source_file"],
        vle_rules
    )

    write_clean_vle(
        vle_df,
        clean_dir / vle_rules["output_file"]
    )

    logger.info(
        "Completed preprocessing for vle"
    )

    # ---------------------------------------------------------
    # 9. Preprocess studentVle
    # ---------------------------------------------------------

    student_vle_rules = preprocessing_rules[
        "student_vle"
    ]

    student_vle_df = preprocess_student_vle(
        raw_dir / student_vle_rules["source_file"],
        student_vle_rules
    )

    write_clean_student_vle(
        student_vle_df,
        clean_dir / student_vle_rules["output_file"]
    )

    logger.info(
        "Completed preprocessing for student_vle"
    )

    # ---------------------------------------------------------
    # 10. Validate complete clean layer
    # ---------------------------------------------------------

    summary = run_clean_layer_validation(
        clean_dir=clean_dir,
        config=preprocessing_rules,
        output_path=validation_summary_path
    )

    logger.info(
        "Clean-layer validation completed with status '%s'",
        summary["overall_status"]
    )

    logger.info(
        "Integration ready: %s",
        summary["integration_ready"]
    )

    # ---------------------------------------------------------
    # 11. Complete pipeline
    # ---------------------------------------------------------

    logger.info(
        "CLAF preprocessing pipeline completed"
    )


if __name__ == "__main__":
    main()