import pandas as pd

from ydata_profiling.config import Settings
from ydata_profiling.model.var_description.counts import VarCounts


def get_counts_pandas(config: Settings, series: pd.Series) -> VarCounts:
    """Get a VarCounts object for a pandas series."""
    length = len(series)

    try:
        value_counts_with_nan = series.value_counts(dropna=False)
        _ = set(value_counts_with_nan.index)
        hashable = True
    except:  # noqa: E722
        hashable = False

    value_counts_without_nan = None
    value_counts_index_sorted = None
    if hashable:
        value_counts_with_nan = value_counts_with_nan[value_counts_with_nan > 0]

        null_index = value_counts_with_nan.index.isnull()
        if null_index.any():
            n_missing = value_counts_with_nan[null_index].sum()
            value_counts_without_nan = value_counts_with_nan[~null_index]
        else:
            n_missing = 0
            value_counts_without_nan = value_counts_with_nan

        try:
            value_counts_index_sorted = value_counts_without_nan.sort_index(
                ascending=True
            )
            ordering = True
        except TypeError:
            ordering = False
    else:
        n_missing = series.isna().sum()
        ordering = False

    return VarCounts(
        hashable=hashable,
        value_counts_without_nan=value_counts_without_nan,
        value_counts_index_sorted=value_counts_index_sorted,
        ordering=ordering,
        n_missing=n_missing,
        n=length,
        p_missing=series.isna().sum() / length if length > 0 else 0,
        count=length - series.isna().sum(),
        memory_size=series.memory_usage(deep=config.memory_deep),
        value_counts=None,
    )
