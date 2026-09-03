"""Export CLAF BI semantic-layer tables for Power BI consumption."""

from pathlib import Path

import pandas as pd


EXPORT_FILES = {
    "dim_student": "dim_student.csv",
    "dim_course_presentation": "dim_course_presentation.csv",
    "fact_student_learning": "fact_student_learning.csv",
    "fact_student_week": "fact_student_week.csv",
}


def export_powerbi_tables(
    bi_dir: Path,
    powerbi_dir: Path,
) -> dict:
    """Export BI semantic-layer Parquet tables to CSV for Power BI."""

    bi_dir = Path(bi_dir)
    powerbi_dir = Path(powerbi_dir)

    powerbi_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    results = {}

    for table_name, csv_filename in EXPORT_FILES.items():

        parquet_path = bi_dir / f"{table_name}.parquet"
        csv_path = powerbi_dir / csv_filename

        if not parquet_path.exists():
            raise FileNotFoundError(
                f"Missing BI source table: {parquet_path}"
            )

        df = pd.read_parquet(parquet_path)

        df.to_csv(
            csv_path,
            index=False,
        )

        results[table_name] = {
            "source_rows": int(len(df)),
            "source_columns": int(len(df.columns)),
            "output_path": str(csv_path),
        }

    return results


def validate_powerbi_exports(
    bi_dir: Path,
    powerbi_dir: Path,
) -> dict:
    """Validate CSV exports against the canonical BI Parquet tables."""

    bi_dir = Path(bi_dir)
    powerbi_dir = Path(powerbi_dir)

    table_results = {}
    overall_passed = True

    for table_name, csv_filename in EXPORT_FILES.items():

        parquet_path = bi_dir / f"{table_name}.parquet"
        csv_path = powerbi_dir / csv_filename

        if not parquet_path.exists():
            raise FileNotFoundError(
                f"Missing BI source table: {parquet_path}"
            )

        if not csv_path.exists():
            raise FileNotFoundError(
                f"Missing Power BI export: {csv_path}"
            )

        parquet_df = pd.read_parquet(parquet_path)
        csv_df = pd.read_csv(csv_path)

        row_count_match = (
            len(parquet_df)
            == len(csv_df)
        )

        column_count_match = (
            len(parquet_df.columns)
            == len(csv_df.columns)
        )

        column_order_match = (
            list(parquet_df.columns)
            == list(csv_df.columns)
        )

        passed = all(
            [
                row_count_match,
                column_count_match,
                column_order_match,
            ]
        )

        table_results[table_name] = {
            "passed": passed,
            "parquet_rows": int(len(parquet_df)),
            "csv_rows": int(len(csv_df)),
            "parquet_columns": int(
                len(parquet_df.columns)
            ),
            "csv_columns": int(
                len(csv_df.columns)
            ),
            "row_count_match": row_count_match,
            "column_count_match": column_count_match,
            "column_order_match": column_order_match,
            "csv_size_mb": round(
                csv_path.stat().st_size
                / (1024 * 1024),
                2,
            ),
        }

        if not passed:
            overall_passed = False

    return {
        "passed": overall_passed,
        "tables": table_results,
    }