"""Run the CLAF BI semantic layer build pipeline."""

from pathlib import Path

import pandas as pd

from src.bi.semantic_validation import (
    validate_bi_semantic_model,
)

from src.bi.student_dimension import (
    build_student_dimension,
    validate_student_dimension,
    write_student_dimension,
)

from src.bi.course_presentation_dimension import (
    build_course_presentation_dimension,
    validate_course_presentation_dimension,
    write_course_presentation_dimension,
)

from src.bi.student_learning_fact import (
    build_student_learning_fact,
    validate_student_learning_fact,
    write_student_learning_fact,
)

from src.bi.student_week_fact import (
    build_student_week_fact,
    validate_student_week_fact,
    write_student_week_fact,
)



from src.bi.powerbi_export import (
    export_powerbi_tables,
    validate_powerbi_exports,
)

import json
from datetime import datetime, timezone


def require_passed(name: str, validation: dict) -> None:
    """Fail fast if a BI artifact validation does not pass."""

    if not validation.get("passed", False):
        raise RuntimeError(
            f"{name} validation failed: {validation}"
        )


def main() -> None:
    """Build and validate all BI semantic-layer artifacts."""

    analytics_dir = Path("data/analytics")
    metrics_dir = Path("data/metrics")
    bi_dir = Path("data/bi")

    bi_dir.mkdir(parents=True, exist_ok=True)

    print("\nCLAF BI SEMANTIC LAYER")
    print("=" * 70)

    # ------------------------------------------------------------------
    # Source data
    # ------------------------------------------------------------------

    student_profile = pd.read_parquet(
        metrics_dir / "student_learning_profile.parquet"
    )

    cohort_metrics = pd.read_parquet(
        metrics_dir / "cohort_metrics.parquet"
    )

    risk_metrics = pd.read_parquet(
        metrics_dir / "risk_metrics.parquet"
    )

    improvement_metrics = pd.read_parquet(
        metrics_dir / "assessment_improvement.parquet"
    )

    student_week_engagement = pd.read_parquet(
        metrics_dir / "student_week_engagement.parquet"
    )

    course_presentation = pd.read_parquet(
        analytics_dir / "course_presentation.parquet"
    )

    # ------------------------------------------------------------------
    # Student dimension
    # ------------------------------------------------------------------

    dim_student = build_student_dimension(
        student_profile
    )

    student_validation = validate_student_dimension(
        dim_student,
        student_profile,
    )

    require_passed(
        "Student dimension",
        student_validation,
    )

    write_student_dimension(
        dim_student,
        bi_dir / "dim_student.parquet",
    )

    print(
        f"dim_student: "
        f"{len(dim_student):,} rows"
    )

    # ------------------------------------------------------------------
    # Course-presentation dimension
    # ------------------------------------------------------------------

    dim_course = build_course_presentation_dimension(
        course_presentation
    )

    course_validation = (
        validate_course_presentation_dimension(
            dim_course,
            course_presentation,
        )
    )

    require_passed(
        "Course-presentation dimension",
        course_validation,
    )

    write_course_presentation_dimension(
        dim_course,
        bi_dir / "dim_course_presentation.parquet",
    )

    print(
        f"dim_course_presentation: "
        f"{len(dim_course):,} rows"
    )

    # ------------------------------------------------------------------
    # Enrollment-level learning fact
    # ------------------------------------------------------------------

    fact_learning = build_student_learning_fact(
        student_profile,
        cohort_metrics,
        risk_metrics,
        improvement_metrics,
    )

    learning_validation = validate_student_learning_fact(
        fact_learning,
        student_profile,
        dim_student,
        dim_course,
    )

    require_passed(
        "Student learning fact",
        learning_validation,
    )

    write_student_learning_fact(
        fact_learning,
        bi_dir / "fact_student_learning.parquet",
    )

    print(
        f"fact_student_learning: "
        f"{len(fact_learning):,} rows"
    )

    # ------------------------------------------------------------------
    # Weekly engagement fact
    # ------------------------------------------------------------------

    fact_week = build_student_week_fact(
       student_week_engagement,
       dim_course,
    )

    week_validation = validate_student_week_fact(
        fact_week,
        student_week_engagement,
        dim_student,
        dim_course,
    )

    require_passed(
        "Student week fact",
        week_validation,
    )

    write_student_week_fact(
        fact_week,
        bi_dir / "fact_student_week.parquet",
    )

    print(
        f"fact_student_week: "
        f"{len(fact_week):,} rows"
    )

        # ------------------------------------------------------------------
    # Cross-table semantic validation
    # ------------------------------------------------------------------

    semantic_validation = validate_bi_semantic_model(
        dim_student,
        dim_course,
        fact_learning,
        fact_week,
    )

    require_passed(
        "BI semantic model",
        semantic_validation,
    )

    print("\nSemantic validation:")
    print(
        f"  Learning enrollments: "
        f"{semantic_validation['learning_enrollment_count']:,}"
    )
    print(
        f"  Weekly enrollments: "
        f"{semantic_validation['weekly_enrollment_count']:,}"
    )
    print(
        f"  Enrollment-level clicks: "
        f"{semantic_validation['learning_total_clicks']:,}"
    )
    print(
        f"  Weekly participation clicks: "
        f"{semantic_validation['weekly_total_clicks']:,}"
    )
    print(
        f"  Missing improvement evidence: "
        f"{semantic_validation['learning_missing_improvement']:,}"
    )
    print(
        f"  Missing risk classification: "
        f"{semantic_validation['learning_missing_risk_level']:,}"
    )


         # ------------------------------------------------------------------
    # Power BI export layer
    # ------------------------------------------------------------------

    powerbi_dir = Path("data/powerbi")

    export_powerbi_tables(
        bi_dir,
        powerbi_dir,
    )

    export_validation = validate_powerbi_exports(
        bi_dir,
        powerbi_dir,
    )

    require_passed(
        "Power BI export",
        export_validation,
    )

    print("\nPower BI exports:")

    for table_name, result in (
        export_validation["tables"].items()
    ):
        print(
            f"  {table_name}: "
            f"{result['csv_rows']:,} rows, "
            f"{result['csv_columns']} columns, "
            f"{result['csv_size_mb']:.2f} MB"
        )

        # ------------------------------------------------------------------
    # BI validation metadata
    # ------------------------------------------------------------------

    metadata_dir = Path("data/metadata")
    metadata_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    validation_summary = {
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "bi_semantic_layer_ready": True,
        "semantic_validation": semantic_validation,
        "powerbi_export_validation": export_validation,
        "artifacts": {
            "dim_student": {
                "rows": int(len(dim_student)),
                "columns": int(len(dim_student.columns)),
            },
            "dim_course_presentation": {
                "rows": int(len(dim_course)),
                "columns": int(len(dim_course.columns)),
            },
            "fact_student_learning": {
                "rows": int(len(fact_learning)),
                "columns": int(len(fact_learning.columns)),
            },
            "fact_student_week": {
                "rows": int(len(fact_week)),
                "columns": int(len(fact_week.columns)),
            },
        },
    }

    metadata_path = (
        metadata_dir
        / "bi_semantic_validation_summary.json"
    )

    with metadata_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            validation_summary,
            file,
            indent=2,
            default=str,
        )

    print(
        "\nValidation metadata:"
        f"\n  {metadata_path}"
    )

    print("\nBI semantic layer build completed successfully.")

    


if __name__ == "__main__":
    main()