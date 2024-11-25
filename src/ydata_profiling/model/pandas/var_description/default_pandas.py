from __future__ import annotations

import pandas as pd

from ydata_profiling.config import Settings
from ydata_profiling.model.pandas.var_description.counts_pandas import get_counts_pandas
from ydata_profiling.model.var_description.default import VarDescription


def get_default_pandas_description(
    config: Settings, series: pd.Series, init_dict: dict
) -> VarDescription:
    var_counts = get_counts_pandas(config, series)

    if var_counts.hashable:
        count = var_counts.count
        value_counts = var_counts.value_counts_without_nan
        distinct_count = len(value_counts)
        unique_count = value_counts.where(value_counts == 1).count()

        init_dict.update(
            {
                "n_distinct": distinct_count,
                "p_distinct": distinct_count / count if count > 0 else 0,
                "is_unique": unique_count == count and count > 0,
                "n_unique": unique_count,
                "p_unique": unique_count / count if count > 0 else 0,
            }
        )

    return VarDescription.from_var_counts(var_counts, init_dict)
