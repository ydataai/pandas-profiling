"""Compute statistical description of datasets."""

import multiprocessing
import multiprocessing.pool
from typing import Tuple

import numpy as np
import pandas as pd
from tqdm import tqdm
from visions import VisionsTypeset

from ydata_profiling.config import Settings
from ydata_profiling.model.summarizer import BaseSummarizer
from ydata_profiling.model.summary import describe_1d, get_series_descriptions
from ydata_profiling.model.typeset import ProfilingTypeSet
from ydata_profiling.utils.dataframe import sort_column_names


def _is_cast_type_defined(typeset: VisionsTypeset, series: str) -> bool:
    return (
        isinstance(typeset, ProfilingTypeSet)
        and typeset.type_schema
        and series in typeset.type_schema
    )


@describe_1d.register
def pandas_describe_1d(
    config: Settings,
    series: pd.Series,
    summarizer: BaseSummarizer,
    typeset: VisionsTypeset,
) -> dict:
    """Describe a series (infer the variable type, then calculate type-specific values).

    Args:
        config: report Settings object
        series: The Series to describe.
        summarizer: Summarizer object
        typeset: Typeset

    Returns:
        A Series containing calculated series description values.
    """

    # Make sure pd.NA is not in the series
    with pd.option_context("future.no_silent_downcasting", True):
        series = series.fillna(np.nan)

    has_cast_type = _is_cast_type_defined(typeset, series.name)
    cast_type = str(typeset.type_schema[series.name]) if has_cast_type else None

    if has_cast_type and not series.isna().all():
        vtype = typeset.type_schema[series.name]

    elif config.infer_dtypes:
        # Infer variable types
        vtype = typeset.infer_type(series)
        series = typeset.cast_to_inferred(series)
    else:
        # Detect variable types from pandas dataframe (df.dtypes).
        # [new dtypes, changed using `astype` function are now considered]
        vtype = typeset.detect_type(series)

    typeset.type_schema[series.name] = vtype
    summary = summarizer.summarize(config, series, dtype=vtype)
    # Cast type is only used on unsupported columns rendering pipeline
    # to indicate the correct variable type when inference is not possible
    summary["cast_type"] = cast_type

    return summary


@get_series_descriptions.register
def pandas_get_series_descriptions(
    config: Settings,
    df: pd.DataFrame,
    summarizer: BaseSummarizer,
    typeset: VisionsTypeset,
    pbar: tqdm,
) -> dict:
    def multiprocess_1d(args: tuple) -> Tuple[str, dict]:
        """Wrapper to process series in parallel.

        Args:
            column: The name of the column.
            series: The series values.

        Returns:
            A tuple with column and the series description.
        """
        column, series = args
        return column, describe_1d(config, series, summarizer, typeset)

    pool_size = config.pool_size

    # Multiprocessing of Describe 1D for each column
    if pool_size <= 0:
        pool_size = multiprocessing.cpu_count()

    args = [(name, series) for name, series in df.items()]
    series_description = {}

    if pool_size == 1:
        for arg in args:
            pbar.set_postfix_str(f"Describe variable:{arg[0]}")
            column, description = multiprocess_1d(arg)
            series_description[column] = description
            pbar.update()
    else:
        # TODO: use `Pool` for Linux-based systems
        with multiprocessing.pool.ThreadPool(pool_size) as executor:
            for i, (column, description) in enumerate(
                executor.imap_unordered(multiprocess_1d, args)
            ):
                pbar.set_postfix_str(f"Describe variable:{column}")
                series_description[column] = description
                pbar.update()

        # Restore the original order
        series_description = {k: series_description[k] for k in df.columns}

    # Mapping from column name to variable type
    series_description = sort_column_names(series_description, config.sort)
    return series_description
