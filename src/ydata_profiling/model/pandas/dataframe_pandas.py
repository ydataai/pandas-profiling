import warnings

import pandas as pd

from ydata_profiling.config import Settings
from ydata_profiling.model.dataframe import check_dataframe, preprocess
from ydata_profiling.utils.dataframe import rename_index


@check_dataframe.register
def pandas_check_dataframe(df: pd.DataFrame) -> None:
    if not isinstance(df, pd.DataFrame):
        warnings.warn("df is not of type pandas.DataFrame")


@preprocess.register
def pandas_preprocess(config: Settings, df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess the dataframe

    - Appends the index to the dataframe when it contains information
    - Rename the "index" column to "df_index", if exists
    - Convert the DataFrame's columns to str

    Args:
        config: report Settings object
        df: the pandas DataFrame

    Returns:
        The preprocessed DataFrame
    """
    # Rename reserved column names
    df = rename_index(df)

    # Ensure that columns are strings
    df.columns = df.columns.map(str)
    return df
