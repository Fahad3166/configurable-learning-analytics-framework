from pathlib import Path
import logging

import pandas as pd


logger = logging.getLogger(__name__)


COURSE_PRESENTATION_KEY = [
    "code_module",
    "code_presentation",
]


def build_course_presentation(
    courses_path: Path,
) -> pd.DataFrame:
    """
    Build the Course Presentation analytical entity.

    Grain:
        One row per module and presentation.
    """

    courses = pd.read_parquet(
        courses_path
    )

    logger.info(
        "Building Course Presentation from %s course rows",
        len(courses),
    )


    course_presentation = courses.copy()

    duplicate_keys = course_presentation.duplicated(
       subset=COURSE_PRESENTATION_KEY
       ).sum()

    if duplicate_keys > 0:
        raise ValueError(
           "Duplicate Course Presentation keys found: "
            f"{duplicate_keys}"
       )



    logger.info(
         "Course Presentation built with %s rows",
        len(course_presentation),
    )

    return course_presentation



def write_course_presentation(
    dataframe: pd.DataFrame,
    output_path: Path,
) -> None:
    """
    Write the Course Presentation analytical entity to Parquet.
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
        "Course Presentation dataset written to %s with %s rows",
        output_path,
        len(dataframe),
    )