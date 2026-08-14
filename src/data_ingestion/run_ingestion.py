from pathlib import Path
import sys

from src.data_ingestion.manifest import (
    create_manifest,
    write_manifest,
)
from src.utils.config_loader import load_yaml_config
from src.utils.logging_setup import setup_logging



def main() -> None:
    """
    Run the CLAF ingestion workflow.
    """

    setup_logging()

    config = load_yaml_config(
        "configs/config.yaml"
    )

    project_root = Path.cwd()

    source_name = "oulad"
    source_config = config["sources"][source_name]

    manifest = create_manifest(
        source_name=source_name,
        source_config=source_config,
        project_root=project_root
    )
    output_path = (
    Path(config["data"]["metadata_dir"])
    / config["ingestion"]["metadata_output"]["filename"]
    )

    write_manifest(
    manifest=manifest,
    output_path=output_path

    )

    if manifest["overall_status"] != "success":
      sys.exit(1)

if __name__ == "__main__":
 main()
