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


if __name__ == "__main__":
    main()
