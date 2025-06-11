"""Module for handling data operations related to devices"""

import pandas as pd


def fix_building_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fix the building names in the dataframe

    Args:
        df (pd.DataFrame): Dataframe with building names

    Returns:
        pd.DataFrame: Dataframe with fixed building names
    """

    df["building_name"] = df["building_name"].str.lower()
    df["building_name"] = df["building_name"].str.replace(" | ", "_")
    df["building_name"] = df["building_name"].str.replace(" ", "_")
    return df
