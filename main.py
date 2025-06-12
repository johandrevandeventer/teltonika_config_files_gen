"""Main script"""

from utils.files import files
from config import config
from data import data


def main():
    devices_details_path = files.get_devices_details_path(
        config.DEVICES_DETAILS_FILE_NAME
    )

    df = files.read_excel_file(devices_details_path, "Details")

    df = data.fix_building_names(df)

    original_config_file_path = files.get_original_config_path(
        config.ORIGINAL_CONFIG_FILE_NAME
    )

    config_files_path = files.get_config_files_path("config_files")

    print("config_files_path:", config_files_path)

    files.create_config_files(df, config_files_path, original_config_file_path)


if __name__ == "__main__":
    main()
