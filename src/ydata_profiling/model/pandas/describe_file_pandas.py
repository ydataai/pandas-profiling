import os
from datetime import datetime
from typing import Tuple

import pandas as pd

from ydata_profiling.config import Settings
from ydata_profiling.model.summary_algorithms import describe_file_1d, histogram_compute
from ydata_profiling.model.var_description.default import VarDescription


def file_summary(series: pd.Series) -> dict:
    """

    Args:
        series: series to summarize

    Returns:

    """

    # Transform
    stats = series.map(lambda x: os.stat(x))

    def convert_datetime(x: float) -> str:
        return datetime.fromtimestamp(x).strftime("%Y-%m-%d %H:%M:%S")

    # Transform some more
    summary = {
        "file_size": stats.map(lambda x: x.st_size),
        "file_created_time": stats.map(lambda x: x.st_ctime).map(convert_datetime),
        "file_accessed_time": stats.map(lambda x: x.st_atime).map(convert_datetime),
        "file_modified_time": stats.map(lambda x: x.st_mtime).map(convert_datetime),
    }
    return summary


@describe_file_1d.register
def pandas_describe_file_1d(
    config: Settings, series: pd.Series, summary: VarDescription
) -> Tuple[Settings, pd.Series, VarDescription]:
    if series.hasnans:
        raise ValueError("May not contain NaNs")
    if not hasattr(series, "str"):
        raise ValueError("series should have .str accessor")

    summary.update(file_summary(series))
    summary.update(
        histogram_compute(
            config,
            summary["file_size"],
            summary["file_size"].nunique(),
            name="histogram_file_size",
        )
    )

    return config, series, summary
