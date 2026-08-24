from pathlib import Path
import logging

import pandas as pd


logger = logging.getLogger(__name__)


VLE_ACTIVITY_GRAIN = [
    "id_student",
    "code_module",
    "code_presentation",
    "date",
]


def build_vle_activity(
    student_vle_path: Path,
) -> pd.DataFrame:
    """
    Build the VLE Activity analytical entity.

    Grain:
        One row per student, module, presentation, and activity day.
    """

    student_vle = pd.read_parquet(
        student_vle_path
    )

    logger.info(
        "Building VLE Activity from %s source interaction rows",
        len(student_vle),
    )

    vle_activity = (
    student_vle
    .groupby(
        VLE_ACTIVITY_GRAIN,
        as_index=False,
        sort=False,
    )["sum_click"]
    .sum()
    .rename(
        columns={
            "sum_click": "daily_clicks"
        }
    )
)

    logger.info(
    "VLE Activity built with %s daily rows",
    len(vle_activity),
    )

    return vle_activity


def write_vle_activity(
    dataframe: pd.DataFrame,
    output_path: Path,
) -> None:
    """
    Write the integrated VLE Activity entity to Parquet.
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
        "VLE Activity dataset written to %s with %s rows",
        output_path,
        len(dataframe),
    )