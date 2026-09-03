from pathlib import Path
import logging

import pandas as pd


logger = logging.getLogger(__name__)


STUDENT_ENROLLMENT_KEY = [
    "id_student",
    "code_module",
    "code_presentation",
]

ASSESSMENT_KEY = [
    "id_student",
    "id_assessment",
]

COURSE_PRESENTATION_KEY = [
    "code_module",
    "code_presentation",
]


def load_assessment_inputs(
    assessment_submission_path: Path,
    student_enrollment_path: Path,
    course_presentation_path: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load analytical-layer inputs required by the assessment metrics engine.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
        assessment_submission,
        student_enrollment,
        course_presentation
    """

    assessment_submission = pd.read_parquet(
        assessment_submission_path
    )

    student_enrollment = pd.read_parquet(
        student_enrollment_path
    )

    course_presentation = pd.read_parquet(
        course_presentation_path
    )

    logger.info(
        "Loaded assessment metric inputs: "
        "assessment_submission=%s, "
        "student_enrollment=%s, "
        "course_presentation=%s",
        len(assessment_submission),
        len(student_enrollment),
        len(course_presentation),
    )

    return (
        assessment_submission,
        student_enrollment,
        course_presentation,
    )


def build_assessment_definitions(
    assessments: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build the authoritative assessment definition catalog.

    The clean assessments table is used rather than reconstructing
    definitions from student submissions because assessments with no
    submission records must still remain available for eligibility
    and completion analysis.
    """

    definition_columns = [
        "id_assessment",
        "code_module",
        "code_presentation",
        "assessment_type",
        "date",
        "weight",
    ]

    assessment_definitions = (
        assessments[
            definition_columns
        ]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    duplicate_assessment_ids = (
        assessment_definitions["id_assessment"]
        .duplicated()
        .sum()
    )

    if duplicate_assessment_ids > 0:
        raise ValueError(
            "Assessment definitions contain duplicate "
            "id_assessment values."
        )

    logger.info(
        "Built %s authoritative assessment definitions",
        len(assessment_definitions),
    )

    return assessment_definitions



def build_assessment_opportunities(
    student_enrollment: pd.DataFrame,
    assessment_definitions: pd.DataFrame,
    course_presentation: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build eligible student-assessment opportunities.

    Each enrollment is matched with the assessment definitions for its
    course presentation.

    Eligibility boundary:
    - actual assessment due date when available;
    - module presentation length when the assessment due date is missing.

    Assessments whose eligibility boundary occurs after a student's
    recorded unregistration date are excluded.
    """

    definitions = assessment_definitions.merge(
        course_presentation[
            COURSE_PRESENTATION_KEY
            + ["module_presentation_length"]
        ],
        on=COURSE_PRESENTATION_KEY,
        how="left",
        validate="many_to_one",
    )

    if definitions["module_presentation_length"].isna().any():
        raise ValueError(
            "Assessment definitions contain missing "
            "module presentation lengths."
        )

    # Preserve the real assessment date separately.
    definitions["eligibility_boundary"] = (
        definitions["date"]
        .fillna(definitions["module_presentation_length"])
    )

    opportunities = student_enrollment[
        STUDENT_ENROLLMENT_KEY
        + ["date_unregistration"]
    ].merge(
        definitions,
        on=COURSE_PRESENTATION_KEY,
        how="inner",
        validate="many_to_many",
    )

    eligible_mask = (
        opportunities["date_unregistration"].isna()
        | (
            opportunities["eligibility_boundary"]
            <= opportunities["date_unregistration"]
        )
    )

    opportunities = (
        opportunities.loc[eligible_mask]
        .reset_index(drop=True)
    )

    duplicate_count = opportunities[
        ASSESSMENT_KEY
    ].duplicated().sum()

    if duplicate_count > 0:
        raise ValueError(
            "Eligible assessment opportunities contain "
            "duplicate student-assessment keys."
        )

    logger.info(
        "Built %s eligible student-assessment opportunities",
        len(opportunities),
    )

    return opportunities


def attach_assessment_submissions(
    assessment_opportunities: pd.DataFrame,
    assessment_submission: pd.DataFrame,
) -> pd.DataFrame:
    """
    Attach observed assessment submissions to eligible opportunities.

    The eligible opportunity table remains authoritative. Submissions
    that fall outside the student's eligibility period are not added
    to this table and remain preserved in the analytical source layer.

    A missing date_submitted after the join represents an eligible
    assessment with no observed submission.
    """

    submission_columns = [
        "id_student",
        "id_assessment",
        "date_submitted",
        "is_banked",
        "score",
    ]

    submissions = assessment_submission[
        submission_columns
    ].copy()

    duplicate_submissions = submissions[
        ASSESSMENT_KEY
    ].duplicated().sum()

    if duplicate_submissions > 0:
        raise ValueError(
            "Assessment submissions contain duplicate "
            "student-assessment keys."
        )

    assessment_status = assessment_opportunities.merge(
        submissions,
        on=ASSESSMENT_KEY,
        how="left",
        validate="one_to_one",
    )

    assessment_status["is_submitted"] = (
        assessment_status["date_submitted"].notna()
    )

    assessment_status["is_scored"] = (
        assessment_status["score"].notna()
    )

    logger.info(
        "Attached submissions to %s eligible assessment opportunities",
        len(assessment_status),
    )

    return assessment_status


def build_assessment_completion_metrics(
    assessment_status: pd.DataFrame,
    observed_assessment_ids,
) -> pd.DataFrame:
    """
    Calculate assessment completion metrics at student-enrollment grain.

    Completion is measured only against eligible assessment
    opportunities whose assessment outcomes are observable in the
    dataset.

    An assessment definition is considered observable when its
    id_assessment appears at least once in the assessment submission
    source.

    Structurally unobserved assessment definitions remain preserved in
    the assessment catalog but do not reduce student completion rates.

    A submitted eligible assessment counts as completed even when its
    score is missing.
    """

    observable_status = assessment_status.loc[
        assessment_status["id_assessment"].isin(
            observed_assessment_ids
        )
    ].copy()

    completion_metrics = (
        observable_status
        .groupby(
            STUDENT_ENROLLMENT_KEY,
            as_index=False,
            sort=False,
        )
        .agg(
            eligible_assessment_count=(
                "id_assessment",
                "count",
            ),
            assessment_submission_count=(
                "is_submitted",
                "sum",
            ),
            scored_assessment_count=(
                "is_scored",
                "sum",
            ),
        )
    )

    completion_metrics["assessment_completion_rate"] = (
        completion_metrics["assessment_submission_count"]
        / completion_metrics["eligible_assessment_count"]
    )

    logger.info(
        "Built assessment completion metrics for %s enrollments "
        "using observable assessment definitions",
        len(completion_metrics),
    )

    return completion_metrics



def build_mean_score_metrics(
    assessment_status: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate mean assessment score at student-enrollment grain.

    Only eligible assessments with an available score contribute to
    mean_score. Missing scores are preserved as missing evidence and
    are not interpreted as zero.
    """

    scored = assessment_status.loc[
        assessment_status["is_scored"]
    ].copy()

    mean_score_metrics = (
        scored
        .groupby(
            STUDENT_ENROLLMENT_KEY,
            as_index=False,
            sort=False,
        )
        .agg(
            mean_score=(
                "score",
                "mean",
            ),
        )
    )

    logger.info(
        "Built mean score metrics for %s enrollments",
        len(mean_score_metrics),
    )

    return mean_score_metrics



def build_coursework_weighted_metrics(
    assessment_status: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate weighted coursework performance and score coverage.

    Coursework includes TMA and CMA assessments only.

    Rules:
    - exams are excluded;
    - zero-weight coursework is excluded from weighting;
    - eligible positive coursework weight defines expected evidence;
    - only available scores contribute to weighted performance;
    - missing scores are not interpreted as zero;
    - weighted score uses scored positive coursework weight as its
      denominator;
    - coverage reports how much eligible coursework weight has an
      available score.
    """

    coursework = assessment_status.loc[
        assessment_status["assessment_type"].isin(["TMA", "CMA"])
        & (assessment_status["weight"] > 0)
    ].copy()

    eligible_weight = (
        coursework
        .groupby(
            STUDENT_ENROLLMENT_KEY,
            as_index=False,
            sort=False,
        )
        .agg(
            eligible_coursework_weight=(
                "weight",
                "sum",
            ),
        )
    )

    scored = coursework.loc[
        coursework["is_scored"]
    ].copy()

    scored["weighted_score_component"] = (
        scored["score"] * scored["weight"]
    )

    scored_metrics = (
        scored
        .groupby(
            STUDENT_ENROLLMENT_KEY,
            as_index=False,
            sort=False,
        )
        .agg(
            scored_coursework_weight=(
                "weight",
                "sum",
            ),
            weighted_score_sum=(
                "weighted_score_component",
                "sum",
            ),
        )
    )

    metrics = eligible_weight.merge(
        scored_metrics,
        on=STUDENT_ENROLLMENT_KEY,
        how="left",
        validate="one_to_one",
    )

    metrics["scored_coursework_weight"] = (
        metrics["scored_coursework_weight"]
        .fillna(0)
    )

    metrics["coursework_score_coverage"] = (
        metrics["scored_coursework_weight"]
        / metrics["eligible_coursework_weight"]
    )

    metrics["coursework_weighted_score"] = (
        metrics["weighted_score_sum"]
        / metrics["scored_coursework_weight"]
    )

    metrics = metrics.drop(
        columns=["weighted_score_sum"]
    )

    logger.info(
        "Built coursework weighted metrics for %s enrollments",
        len(metrics),
    )

    return metrics


def build_exam_score_metrics(
    assessment_status: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate exam performance at student-enrollment grain.

    Exams are kept separate from coursework weighting.

    Only eligible exam assessments with an available score contribute
    to exam_score. Missing exam scores are not interpreted as zero.
    """

    scored_exams = assessment_status.loc[
        (assessment_status["assessment_type"] == "Exam")
        & assessment_status["is_scored"]
    ].copy()

    exam_metrics = (
        scored_exams
        .groupby(
            STUDENT_ENROLLMENT_KEY,
            as_index=False,
            sort=False,
        )
        .agg(
            exam_score=(
                "score",
                "mean",
            ),
            scored_exam_count=(
                "id_assessment",
                "count",
            ),
        )
    )

    logger.info(
        "Built exam score metrics for %s enrollments",
        len(exam_metrics),
    )

    return exam_metrics

def build_submission_timeliness_metrics(
    assessment_status: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate assessment submission timeliness at student-enrollment grain.

    Timeliness population:
    - assessment is eligible;
    - assessment was submitted;
    - actual assessment due date is available;
    - assessment is not banked.

    Banked assessments are excluded because their date_submitted value
    represents carried assessment evidence rather than meaningful
    submission timing.

    Assessments without an actual due date are also excluded. The
    presentation-length eligibility fallback is never treated as an
    assessment due date.
    """

    timeliness = assessment_status.loc[
        assessment_status["is_submitted"]
        & assessment_status["date"].notna()
        & (assessment_status["is_banked"] == 0)
    ].copy()

    timeliness["days_from_due"] = (
        timeliness["date_submitted"]
        - timeliness["date"]
    )

    timeliness["is_late"] = (
        timeliness["days_from_due"] > 0
    )

    timeliness["is_on_time"] = (
        timeliness["days_from_due"] <= 0
    )

    metrics = (
        timeliness
        .groupby(
            STUDENT_ENROLLMENT_KEY,
            as_index=False,
            sort=False,
        )
        .agg(
            timeliness_assessment_count=(
                "id_assessment",
                "count",
            ),
            mean_days_from_due=(
                "days_from_due",
                "mean",
            ),
            late_submission_count=(
                "is_late",
                "sum",
            ),
            on_time_submission_count=(
                "is_on_time",
                "sum",
            ),
        )
    )

    metrics["on_time_submission_rate"] = (
        metrics["on_time_submission_count"]
        / metrics["timeliness_assessment_count"]
    )

    logger.info(
        "Built submission timeliness metrics for %s enrollments",
        len(metrics),
    )

    return metrics


def build_assessment_metrics(
    assessment_status: pd.DataFrame,
    assessment_submission: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build the combined assessment metric table at student-enrollment grain.

    The table combines:
    - assessment completion;
    - mean score;
    - weighted coursework performance;
    - coursework score coverage;
    - exam performance;
    - submission timeliness.

    Missing metric values remain missing when the underlying evidence
    required for that metric does not exist.
    """

    observed_assessment_ids = set(
        assessment_submission["id_assessment"].unique()
    )

    metrics = build_assessment_completion_metrics(
        assessment_status,
        observed_assessment_ids,
    )

    mean_score_metrics = build_mean_score_metrics(
        assessment_status
    )

    coursework_metrics = build_coursework_weighted_metrics(
        assessment_status
    )

    exam_metrics = build_exam_score_metrics(
        assessment_status
    )

    timeliness_metrics = build_submission_timeliness_metrics(
        assessment_status
    )

    for metric_table in [
        mean_score_metrics,
        coursework_metrics,
        exam_metrics,
        timeliness_metrics,
    ]:
        metrics = metrics.merge(
            metric_table,
            on=STUDENT_ENROLLMENT_KEY,
            how="left",
            validate="one_to_one",
        )

    logger.info(
        "Built combined assessment metrics for %s enrollments",
        len(metrics),
    )

    return metrics


def validate_assessment_metrics(
    assessment_metrics: pd.DataFrame,
) -> dict:
    """
    Validate the combined assessment metric table.

    Intentional missing values are allowed where a metric cannot be
    calculated because the required evidence does not exist.
    """

    duplicate_key_count = assessment_metrics[
        STUDENT_ENROLLMENT_KEY
    ].duplicated().sum()

    invalid_eligible_count = (
        assessment_metrics["eligible_assessment_count"] <= 0
    ).sum()

    invalid_submission_count = (
        assessment_metrics["assessment_submission_count"]
        > assessment_metrics["eligible_assessment_count"]
    ).sum()

    invalid_scored_count = (
        assessment_metrics["scored_assessment_count"]
        > assessment_metrics["assessment_submission_count"]
    ).sum()

    invalid_completion_rate = (
        assessment_metrics["assessment_completion_rate"].notna()
        & (
            (assessment_metrics["assessment_completion_rate"] < 0)
            | (assessment_metrics["assessment_completion_rate"] > 1)
        )
    ).sum()

    invalid_mean_score = (
        assessment_metrics["mean_score"].notna()
        & (
            (assessment_metrics["mean_score"] < 0)
            | (assessment_metrics["mean_score"] > 100)
        )
    ).sum()

    invalid_weighted_score = (
        assessment_metrics["coursework_weighted_score"].notna()
        & (
            (assessment_metrics["coursework_weighted_score"] < 0)
            | (assessment_metrics["coursework_weighted_score"] > 100)
        )
    ).sum()

    invalid_coursework_coverage = (
        assessment_metrics["coursework_score_coverage"].notna()
        & (
            (assessment_metrics["coursework_score_coverage"] < 0)
            | (assessment_metrics["coursework_score_coverage"] > 1)
        )
    ).sum()

    invalid_exam_score = (
        assessment_metrics["exam_score"].notna()
        & (
            (assessment_metrics["exam_score"] < 0)
            | (assessment_metrics["exam_score"] > 100)
        )
    ).sum()

    invalid_on_time_rate = (
        assessment_metrics["on_time_submission_rate"].notna()
        & (
            (assessment_metrics["on_time_submission_rate"] < 0)
            | (assessment_metrics["on_time_submission_rate"] > 1)
        )
    ).sum()

    invalid_timing_counts = (
        assessment_metrics["timeliness_assessment_count"].notna()
        & (
            assessment_metrics["late_submission_count"]
            + assessment_metrics["on_time_submission_count"]
            != assessment_metrics["timeliness_assessment_count"]
        )
    ).sum()

    checks = {
        "duplicate_key_count": int(duplicate_key_count),
        "invalid_eligible_count": int(invalid_eligible_count),
        "invalid_submission_count": int(invalid_submission_count),
        "invalid_scored_count": int(invalid_scored_count),
        "invalid_completion_rate": int(invalid_completion_rate),
        "invalid_mean_score": int(invalid_mean_score),
        "invalid_weighted_score": int(invalid_weighted_score),
        "invalid_coursework_coverage": int(invalid_coursework_coverage),
        "invalid_exam_score": int(invalid_exam_score),
        "invalid_on_time_rate": int(invalid_on_time_rate),
        "invalid_timing_counts": int(invalid_timing_counts),
    }

    status = (
        "passed"
        if all(value == 0 for value in checks.values())
        else "failed"
    )

    return {
        "status": status,
        "row_count": len(assessment_metrics),
        "checks": checks,
    }


def write_assessment_metrics(
    assessment_metrics: pd.DataFrame,
    output_path: Path,
) -> None:
    """
    Persist validated assessment metrics as Parquet.
    """

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    assessment_metrics.to_parquet(
        output_path,
        index=False,
    )

    logger.info(
        "Wrote %s assessment metric rows to %s",
        len(assessment_metrics),
        output_path,
    )
