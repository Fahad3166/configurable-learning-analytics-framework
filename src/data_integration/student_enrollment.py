from pathlib import Path
import logging

import pandas as pd


logger = logging.getLogger(__name__)


ENROLLMENT_KEY = [
    "id_student",
    "code_module",
    "code_presentation",
]


def build_student_enrollment(
    student_info_path: Path,
    student_registration_path: Path,
) -> pd.DataFrame:
    """
    Build the integrated Student Enrollment analytical entity.

    Grain:
        One row per student, module, and presentation.
    """

    student_info = pd.read_parquet(
        student_info_path
    )

    student_registration = pd.read_parquet(
        student_registration_path
    )

    logger.info(
        "Building Student Enrollment from %s student-info rows "
        "and %s registration rows",
        len(student_info),
        len(student_registration),
    )

    student_enrollment = student_info.merge(
        student_registration,
        on=ENROLLMENT_KEY,
        how="inner",
        validate="one_to_one",
    )

    logger.info(
        "Student Enrollment built with %s rows",
        len(student_enrollment),
    )

    return student_enrollment


def write_student_enrollment(
    dataframe: pd.DataFrame,
    output_path: Path,
) -> None:
    """
    Write the integrated Student Enrollment entity to Parquet.
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
        "Student Enrollment dataset written to %s with %s rows",
        output_path,
        len(dataframe),
    )