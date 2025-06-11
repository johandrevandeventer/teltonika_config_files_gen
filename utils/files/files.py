"""Utility functions for file handling."""

from pathlib import Path
from typing import List, Tuple

import pandas as pd


class ProcessingError(Exception):
    """Exception raised for errors in the input."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def get_devices_details_path(file_name: str) -> Path:
    """
    Get the path to the devices details file.

    Args:
        file_name (str): The name of the file.
    Returns:
        Path: The path to the devices details file.
    """
    cwd = Path.cwd()
    return cwd / "resources" / "details" / file_name


def read_excel_file(file_path: Path, sheet_name: str) -> pd.DataFrame:
    """
    Read an excel file and return a pandas dataframe

    Args:
        file_path (Path): Path to the excel file
        sheet_name (str): Name of the sheet to read from

    Returns:
        pd.DataFrame: Dataframe of the excel sheet
    """

    df = pd.read_excel(file_path, sheet_name=sheet_name)
    return df


def get_original_config_path(file_name: str) -> Path:
    """
    Get the path to the original configuration file.

    Args:
        file_name (str): The name of the configuration file.

    Returns:
        Path: The path to the original configuration file.
    """
    cwd = Path.cwd()
    return cwd / "resources" / "original_config" / file_name


def create_config_files(
    df: pd.DataFrame, output_dir: Path, original_config_file_path: Path
) -> None:
    """
    Create configuration files from the dataframe.

    Args:
        df (pd.DataFrame): Dataframe with device details.
        output_dir (Path): Directory to save the configuration files.
    """

    if (
        original_config_file_path.suffix != ".gz"
        and original_config_file_path.stem.endswith(".tar")
    ):
        raise ProcessingError("The original config file is not a .tar.gz file")

    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    config_file_list = [
        directory.name for directory in output_dir.iterdir() if directory.is_dir()
    ]

    new_directory_list = []
    current_directory_list = []
    missing_directories = []

    for _, row in df.iterrows():
        building_name = row["building_name"]
        datasource_url = row["datasource_url"]

        if pd.isna(datasource_url):
            print(f"Skipping {building_name} as it has no datasource url")
            continue
