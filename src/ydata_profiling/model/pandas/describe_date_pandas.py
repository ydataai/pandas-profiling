from typing import Tuple

import numpy as np
import pandas as pd

from ydata_profiling.config import Settings
from ydata_profiling.model.summary_algorithms import (
    chi_square,
    describe_date_1d,
    histogram_compute,
    series_handle_nulls,
    series_hashable,
)
from ydata_profiling.model.var_description.default import VarDescription


@describe_date_1d.register
@series_hashable
@series_handle_nulls
def pandas_describe_date_1d(
    config: Settings, series: pd.Series, summary: VarDescription
) -> Tuple[Settings, pd.Series, VarDescription]:
    """Describe a date series.

    Args:
        config: report Settings object
        series: The Series to describe.
        summary: The dict containing the series description so far.

    Returns:
        A dict containing calculated series description values.
    """
    if summary.value_counts_without_nan.empty:
        values = series.values
        summary.update(
            {
                "min": pd.NaT,
                "max": pd.NaT,
                "range": 0,
            }
        )
    else:
        summary.update(
            {
                "min": pd.Timestamp.to_pydatetime(series.min()),
                "max": pd.Timestamp.to_pydatetime(series.max()),
            }
        )

        summary["range"] = summary["max"] - summary["min"]

        values = series.values.astype(np.int64) // 10**9

    if config.vars.num.chi_squared_threshold > 0.0:
        summary["chi_squared"] = chi_square(values)

    summary.update(histogram_compute(config, values, summary["n_distinct"]))
    return config, values, summary
