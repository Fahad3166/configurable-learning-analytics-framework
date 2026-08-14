from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

import pandas as pd
import json
import logging



logger = logging.getLogger(__name__)

def calculate_file_hash(
    file_path: Path,
    block_size: int = 1024 * 1024
) -> str:
    """
    Calculate the SHA-256 hash of a file.

    The file is read incrementally so that large files do not need
    to be loaded completely into memory.

    Parameters
    ----------
    file_path : Path
        Path to the source file.

    block_size : int
        Number of bytes read during each iteration.

    Returns
    -------
    str
        SHA-256 hexadecimal digest.
    """

    hash_object = sha256()

    with file_path.open("rb") as file:
        while block := file.read(block_size):
            hash_object.update(block)

    return hash_object.hexdigest()



def inspect_csv_structure(
    file_path: Path,
    large_file: bool = False,
    chunksize: int = 100_000
) -> dict[str, Any]:
    """
    Inspect the structural metadata of a CSV file.

    Captures row count, column count and column names.

    Large files are processed in chunks to avoid loading the
    entire dataset into memory.

    Parameters
    ----------
    file_path : Path
        Path to the CSV file.

    large_file : bool
        Whether the file should be processed in chunks.

    chunksize : int
        Number of rows per chunk for large files.

    Returns
    -------
    dict
        Structural metadata for the CSV file.
    """

    if large_file:
        row_count = 0
        columns = None

        for chunk in pd.read_csv(
            file_path,
            chunksize=chunksize
        ):
            row_count += len(chunk)

            if columns is None:
                columns = list(chunk.columns)

    else:
        dataframe = pd.read_csv(file_path)

        row_count = len(dataframe)
        columns = list(dataframe.columns)

    return {
        "row_count": row_count,
        "column_count": len(columns),
        "columns": columns
    }



def inspect_source_file(
    file_path: Path,
    logical_name: str,
    file_config: dict
) -> dict[str, Any]:
    """
    Capture metadata for one configured source file.

    Parameters
    ----------
    file_path : Path
        Path to the source file.

    logical_name : str
        Logical dataset name defined in configuration.

    file_config : dict
        Configuration for the source file, including options such as
        large_file and chunksize.

    Returns
    -------
    dict
        File-level ingestion metadata.
    """

    if not file_path.exists():
        return {
            "logical_name": logical_name,
            "filename": file_path.name,
            "exists": False,
            "status": "missing"
        }

    file_size_bytes = file_path.stat().st_size

    large_file = file_config.get(
        "large_file",
        False
    )

    chunksize = file_config.get(
        "chunksize",
        100_000
    )

    structure = inspect_csv_structure(
        file_path=file_path,
        large_file=large_file,
        chunksize=chunksize
    )

    expected_columns = file_config.get(
      "expected_columns",
      []
    )

    schema_validation = validate_schema(
      actual_columns=structure["columns"],
      expected_columns=expected_columns
    )

    return {
        "logical_name": logical_name,
        "filename": file_path.name,
        "exists": True,
        "size_bytes": file_size_bytes,
        "size_mb": round(
            file_size_bytes / (1024 ** 2),
            2
        ),
        "sha256": calculate_file_hash(file_path),
        "row_count": structure["row_count"],
        "column_count": structure["column_count"],
        "columns": structure["columns"],
        "schema_valid": schema_validation["schema_valid"],
        "missing_columns": schema_validation["missing_columns"],
        "unexpected_columns": schema_validation["unexpected_columns"],
        "status": "available"
    }



def validate_schema(
    actual_columns: list[str],
    expected_columns: list[str]
) -> dict[str, Any]:
    """
    Compare actual CSV columns with the configured expected schema.

    Returns whether the schema is valid, along with any missing
    or unexpected columns.
    """

    actual_set = set(actual_columns)
    expected_set = set(expected_columns)

    missing_columns = sorted(
        expected_set - actual_set
    )

    unexpected_columns = sorted(
        actual_set - expected_set
    )

    schema_valid = (
        len(missing_columns) == 0
        and len(unexpected_columns) == 0
    )

    return {
        "schema_valid": schema_valid,
        "missing_columns": missing_columns,
        "unexpected_columns": unexpected_columns
    }




def create_manifest(
    source_name: str,
    source_config: dict,
    project_root: Path
) -> dict[str, Any]:
    """
    Build an ingestion manifest for a configured data source.
    """

    source_path = project_root / source_config["base_path"]

    logger.info(
    "Starting ingestion manifest creation for source '%s'",
    source_name
    )

    manifest = {
        "source": source_name,
        "source_type": source_config["source_type"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_path": str(source_config["base_path"]),
        "files": []
    }

    for logical_name, file_config in source_config[
        "expected_files"
    ].items():

        file_path = source_path / file_config["filename"]

        logger.info(
         "Inspecting source file: %s",
        file_config["filename"]
       )

        file_metadata = inspect_source_file(
         file_path=file_path,
         logical_name=logical_name,
         file_config=file_config
        )

        manifest["files"].append(file_metadata)

    all_files_valid = all(
    file_metadata.get("exists", False)
    and file_metadata.get("schema_valid", False)
    for file_metadata in manifest["files"]
    )

    manifest["overall_status"] = (
    "success" if all_files_valid else "failed"
    )  

    logger.info(
    "Completed ingestion manifest creation for source '%s' with status '%s'",
    source_name,
    manifest["overall_status"]
   )

    return manifest


def write_manifest(
    manifest: dict[str, Any],
    output_path: Path
) -> None:
    """
    Write an ingestion manifest to a JSON file.

    Parameters
    ----------
    manifest : dict
        Manifest generated by create_manifest().

    output_path : Path
        Destination JSON file.
    """

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with output_path.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            manifest,
            file,
            indent=2
        )