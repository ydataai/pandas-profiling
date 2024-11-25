from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd

from ydata_profiling.model.var_description.default import VarDescription
from ydata_profiling.utils.compat import pandas_version_info

if pandas_version_info() >= (1, 5):
    from pandas.core.arrays.integer import IntegerDtype
else:
    from pandas.core.arrays.integer import _IntegerDtype as IntegerDtype

from ydata_profiling.config import Settings
from ydata_profiling.model.summary_algorithms import (
    chi_square,
    describe_numeric_1d,
    histogram_compute,
    series_handle_nulls,
    series_hashable,
)


def mad(arr: np.ndarray) -> np.ndarray:
    """Median Absolute Deviation: a "Robust" version of standard deviation.
    Indices variability of the sample.
    https://en.wikipedia.org/wiki/Median_absolute_deviation
    """
    return np.median(np.abs(arr - np.median(arr)))


def numeric_stats_pandas(series: pd.Series) -> Dict[str, Any]:
    return {
        "mean": series.mean(),
        "std": series.std(),
        "variance": series.var(),
        "min": series.min(),
        "max": series.max(),
        # Unbiased kurtosis obtained using Fisher's definition (kurtosis of normal == 0.0). Normalized by N-1.
        "kurtosis": series.kurt(),
        # Unbiased skew normalized by N-1
        "skewness": series.skew(),
        "sum": series.sum(),
    }


def numeric_stats_numpy(
    present_values: np.ndarray, series: pd.Series, series_description: VarDescription
) -> Dict[str, Any]:
    vc = series_description.value_counts_without_nan
    index_values = vc.index.values

    # FIXME: can be performance optimized by using weights in std, var, kurt and skew...
    if len(index_values):
        return {
            "mean": np.average(index_values, weights=vc.values),
            "std": np.std(present_values, ddof=1),
            "variance": np.var(present_values, ddof=1),
            "min": np.min(index_values),
            "max": np.max(index_values),
            # Unbiased kurtosis obtained using Fisher's definition (kurtosis of normal == 0.0). Normalized by N-1.
            "kurtosis": series.kurt(),
            # Unbiased skew normalized by N-1
            "skewness": series.skew(),
            "sum": np.dot(index_values, vc.values),
        }
    else:  # Empty numerical series
        return {
            "mean": np.nan,
            "std": 0.0,
            "variance": 0.0,
            "min": np.nan,
            "max": np.nan,
            "kurtosis": 0.0,
            "skewness": 0.0,
            "sum": 0,
        }


@describe_numeric_1d.register
@series_hashable
@series_handle_nulls
def pandas_describe_numeric_1d(
    config: Settings, series: pd.Series, summary: VarDescription
) -> Tuple[Settings, pd.Series, VarDescription]:
    """Describe a numeric series.

    Args:
        config: report Settings object
        series: The Series to describe.
        summary: The dict containing the series description so far.

    Returns:
        A dict containing calculated series description values.
    """

    chi_squared_threshold = config.vars.num.chi_squared_threshold
    quantiles = config.vars.num.quantiles

    value_counts = summary.value_counts_without_nan

    negative_index = value_counts.index < 0
    summary["n_negative"] = value_counts.loc[negative_index].sum()
    summary["p_negative"] = summary["n_negative"] / summary.n

    infinity_values = [np.inf, -np.inf]
    infinity_index = value_counts.index.isin(infinity_values)
    summary["n_infinite"] = value_counts.loc[infinity_index].sum()

    summary["n_zeros"] = 0
    if 0 in value_counts.index:
        summary["n_zeros"] = value_counts.loc[0]

    stats = summary

    if isinstance(series.dtype, IntegerDtype):
        stats.update(numeric_stats_pandas(series))
        present_values = series.astype(str(series.dtype).lower())
        finite_values = present_values
    else:
        present_values = series.values
        finite_values = present_values[np.isfinite(present_values)]
        stats.update(numeric_stats_numpy(present_values, series, summary))

    stats.update(
        {
            "mad": mad(present_values),
        }
    )

    if chi_squared_threshold > 0.0:
        stats["chi_squared"] = chi_square(finite_values)

    stats["range"] = stats["max"] - stats["min"]
    stats.update(
        {
            f"{percentile:.0%}": value
            for percentile, value in series.quantile(quantiles).to_dict().items()
        }
    )
    stats["iqr"] = stats["75%"] - stats["25%"]

    stats["cv"] = stats["std"] / stats["mean"] if stats["mean"] else np.NaN
    stats["p_zeros"] = stats["n_zeros"] / summary.n
    stats["p_infinite"] = summary["n_infinite"] / summary.n

    stats["monotonic_increase"] = series.is_monotonic_increasing
    stats["monotonic_decrease"] = series.is_monotonic_decreasing

    stats["monotonic_increase_strict"] = (
        stats["monotonic_increase"] and series.is_unique
    )
    stats["monotonic_decrease_strict"] = (
        stats["monotonic_decrease"] and series.is_unique
    )
    if summary["monotonic_increase_strict"]:
        stats["monotonic"] = 2
    elif summary["monotonic_decrease_strict"]:
        stats["monotonic"] = -2
    elif summary["monotonic_increase"]:
        stats["monotonic"] = 1
    elif summary["monotonic_decrease"]:
        stats["monotonic"] = -1
    else:
        stats["monotonic"] = 0

    if len(value_counts[~infinity_index].index.values) > 0:
        stats.update(
            histogram_compute(
                config,
                value_counts[~infinity_index].index.values,
                summary["n_distinct"],
                weights=value_counts[~infinity_index].values,
            )
        )

    return config, series, stats
