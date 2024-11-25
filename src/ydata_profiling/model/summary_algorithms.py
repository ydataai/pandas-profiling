import functools
from typing import Any, Callable, Optional, Tuple, TypeVar

import numpy as np
import pandas as pd
from multimethod import multimethod
from scipy.stats import chisquare

from ydata_profiling.config import Settings
from ydata_profiling.model.var_description.default import VarDescription

T = TypeVar("T")


def func_nullable_series_contains(fn: Callable) -> Callable:
    @functools.wraps(fn)
    def inner(
        config: Settings, series: pd.Series, state: dict, *args, **kwargs
    ) -> bool:
        if series.hasnans:
            series = series.dropna()
            if series.empty:
                return False

        return fn(config, series, state, *args, **kwargs)

    return inner


def histogram_compute(
    config: Settings,
    finite_values: np.ndarray,
    n_unique: int,
    name: str = "histogram",
    weights: Optional[np.ndarray] = None,
) -> dict:
    stats = {}
    if len(finite_values) == 0:
        return {name: []}
    hist_config = config.plot.histogram
    bins_arg = "auto" if hist_config.bins == 0 else min(hist_config.bins, n_unique)
    bins = np.histogram_bin_edges(finite_values, bins=bins_arg)
    if len(bins) > hist_config.max_bins:
        bins = np.histogram_bin_edges(finite_values, bins=hist_config.max_bins)
        weights = weights if weights and len(weights) == hist_config.max_bins else None

    stats[name] = np.histogram(
        finite_values, bins=bins, weights=weights, density=config.plot.histogram.density
    )

    return stats


def chi_square(
    values: Optional[np.ndarray] = None, histogram: Optional[np.ndarray] = None
) -> dict:
    if histogram is None:
        bins = np.histogram_bin_edges(values, bins="auto")
        histogram, _ = np.histogram(values, bins=bins)
    if len(histogram) == 0 or np.sum(histogram) == 0:
        return {"statistic": 0, "pvalue": 0}
    return dict(chisquare(histogram)._asdict())


def series_hashable(
    fn: Callable[
        [Settings, pd.Series, VarDescription],
        Tuple[Settings, pd.Series, VarDescription],
    ]
) -> Callable[
    [Settings, pd.Series, VarDescription], Tuple[Settings, pd.Series, VarDescription]
]:
    @functools.wraps(fn)
    def inner(
        config: Settings, series: pd.Series, summary: VarDescription
    ) -> Tuple[Settings, pd.Series, VarDescription]:
        if not summary.hashable:
            return config, series, summary
        return fn(config, series, summary)

    return inner


def series_handle_nulls(
    fn: Callable[
        [Settings, pd.Series, VarDescription],
        Tuple[Settings, pd.Series, VarDescription],
    ]
) -> Callable[
    [Settings, pd.Series, VarDescription], Tuple[Settings, pd.Series, VarDescription]
]:
    """Decorator for nullable series"""

    @functools.wraps(fn)
    def inner(
        config: Settings, series: pd.Series, summary: VarDescription
    ) -> Tuple[Settings, pd.Series, VarDescription]:
        if series.hasnans:
            series = series.dropna()

        return fn(config, series, summary)

    return inner


def named_aggregate_summary(series: pd.Series, key: str) -> dict:
    summary = {
        f"max_{key}": np.max(series),
        f"mean_{key}": np.mean(series),
        f"median_{key}": np.median(series),
        f"min_{key}": np.min(series),
    }

    return summary


@multimethod
def describe_supported(
    config: Settings, series: Any, series_description: dict
) -> Tuple[Settings, Any, VarDescription]:
    raise NotImplementedError()


@multimethod
def describe_numeric_1d(
    config: Settings, series: Any, summary: VarDescription
) -> Tuple[Settings, Any, VarDescription]:
    raise NotImplementedError()


@multimethod
def describe_text_1d(
    config: Settings, series: Any, summary: VarDescription
) -> Tuple[Settings, Any, VarDescription]:
    raise NotImplementedError()


@multimethod
def describe_date_1d(
    config: Settings, series: Any, summary: VarDescription
) -> Tuple[Settings, Any, VarDescription]:
    raise NotImplementedError()


@multimethod
def describe_categorical_1d(
    config: Settings, series: pd.Series, summary: VarDescription
) -> Tuple[Settings, Any, VarDescription]:
    raise NotImplementedError()


@multimethod
def describe_url_1d(
    config: Settings, series: Any, summary: VarDescription
) -> Tuple[Settings, Any, VarDescription]:
    raise NotImplementedError()


@multimethod
def describe_file_1d(
    config: Settings, series: Any, summary: VarDescription
) -> Tuple[Settings, Any, VarDescription]:
    raise NotImplementedError()


@multimethod
def describe_path_1d(
    config: Settings, series: Any, summary: VarDescription
) -> Tuple[Settings, Any, VarDescription]:
    raise NotImplementedError()


@multimethod
def describe_image_1d(
    config: Settings, series: Any, summary: VarDescription
) -> Tuple[Settings, Any, VarDescription]:
    raise NotImplementedError()


@multimethod
def describe_boolean_1d(
    config: Settings, series: Any, summary: VarDescription
) -> Tuple[Settings, Any, VarDescription]:
    raise NotImplementedError()


@multimethod
def describe_timeseries_1d(
    config: Settings, series: Any, summary: VarDescription
) -> Tuple[Settings, Any, VarDescription]:
    raise NotImplementedError()
