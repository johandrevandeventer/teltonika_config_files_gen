"""Utility functions for file handling."""

from pathlib import Path
from typing import List, Tuple

import pandas as pd
import shutil
import tarfile


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


def get_config_files_path(dir_name: str) -> Path:
    """
    Get the path to the directory containing configuration files.

    Args:
        dir_name (str): The name of the directory.

    Returns:
        Path: The path to the directory containing configuration files.
    """
    cwd = Path.cwd()
    return cwd / "resources" / dir_name


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
        file.name for file in output_dir.glob("*.tar.gz") if file.is_file()
    ]

    new_file_list = []
    replaced_file_list = []
    missing_file_list = []

    for _, row in df.iterrows():
        building_name = row["building_name"]
        datasource_url = row["datasource_url"]

        if pd.isna(datasource_url):
            print(f"Skipping {building_name} as it has no datasource url")
            continue

        building_name = building_name.replace("(", "").replace(")", "")

        file_name = f"{building_name}.tar.gz"
        new_file_list.append(file_name)

        file_path = output_dir / file_name

        if file_name in config_file_list:
            file_path.unlink()
            replaced_file_list.append(file_name)

        try:
            shutil.copy(original_config_file_path, file_path)
        except FileNotFoundError as e:
            raise ProcessingError(f"Could not copy file to {file_path}") from e

        temp_dir = output_dir / f"temp_{building_name}"

        try:
            with tarfile.open(file_path, "r:gz") as tar:
                tar.extractall(temp_dir)
        except FileNotFoundError as e:
            raise ProcessingError(f"File {file_name} does not exist.") from e

        file_path_to_edit = temp_dir / "etc" / "config" / "data_sender"

        try:
            with open(file_path_to_edit, "r", encoding="utf-8") as file:
                lines = file.readlines()
        except FileNotFoundError:
            print(f"File {file_path_to_edit} does not exist.")
            continue

        target_host = "option http_host 'https://www'"
        new_host = f"option http_host '{datasource_url}'"

        host_replaced = False

        for i, line in enumerate(lines, 1):
            if target_host in line and not host_replaced:
                lines[i - 1] = line.replace(target_host, new_host)
                host_replaced = True

            if host_replaced:
                break

        try:
            with open(file_path_to_edit, "w", encoding="utf-8") as file:
                file.writelines(lines)
        except FileNotFoundError:
            print(f"File {file_path_to_edit} does not exist.")
            continue

        try:
            with tarfile.open(file_path, "w:gz") as tar:
                for root in temp_dir.iterdir():
                    if root.is_dir():
                        for dirs in root.iterdir():
                            if dirs.is_dir():
                                arcname = dirs.relative_to(temp_dir)
                                tar.add(dirs, arcname=arcname)
                            else:
                                arcname = dirs.relative_to(temp_dir)
                                tar.add(dirs, arcname=arcname)
                    else:
                        arcname = root.relative_to(temp_dir)
                        tar.add(root, arcname=arcname)
        except FileNotFoundError:
            print(f"File {file_path} does not exist.")
            continue

        shutil.rmtree(temp_dir)

    for file in config_file_list:
        if file not in new_file_list:
            missing_file_list.append(file)

    print(f"New files created: {new_file_list}")
    print(f"Files replaced: {replaced_file_list}")
    print(f"Missing files: {missing_file_list}")
