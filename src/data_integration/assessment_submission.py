from pathlib import Path
import logging

import pandas as pd


logger = logging.getLogger(__name__)


SUBMISSION_KEY = [
    "id_student",
    "id_assessment",
]


def build_assessment_submission(
    student_assessment_path: Path,
    assessments_path: Path,
) -> pd.DataFrame:
    """
    Build the integrated Assessment Submission analytical entity.

    Grain:
        One row per student and assessment.
    """

    student_assessment = pd.read_parquet(
        student_assessment_path
    )

    assessments = pd.read_parquet(
        assessments_path
    )

    logger.info(
        "Building Assessment Submission from %s student-assessment rows "
        "and %s assessment-definition rows",
        len(student_assessment),
        len(assessments),
    )

    assessment_submission = student_assessment.merge(
       assessments,
       on="id_assessment",
       how="inner",
       validate="many_to_one",
    )

    logger.info(
       "Assessment Submission built with %s rows",
       len(assessment_submission),
   )

    return assessment_submission



def write_assessment_submission(
    dataframe: pd.DataFrame,
    output_path: Path,
) -> None:
    """
    Write the integrated Assessment Submission entity to Parquet.
    """

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_parquet(
        output_path,
        index=False,
    )

    logger.info(
        "Assessment Submission dataset written to %s with %s rows",
        output_path,
        len(dataframe),
    )