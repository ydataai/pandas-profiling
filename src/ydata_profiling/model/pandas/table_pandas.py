from collections import Counter
from typing import Dict

import pandas as pd

from ydata_profiling.config import Settings
from ydata_profiling.model.table import get_table_stats
from ydata_profiling.model.var_description.default import VarDescription


@get_table_stats.register
def pandas_get_table_stats(
    config: Settings, df: pd.DataFrame, variable_stats: Dict[str, VarDescription]
) -> dict:
    """General statistics for the DataFrame.

    Args:
        config: report Settings object
        df: The DataFrame to describe.
        variable_stats: Previously calculated statistic on the DataFrame.

    Returns:
        A dictionary that contains the table statistics.
    """
    n = len(df) if not df.empty else 0

    memory_size = df.memory_usage(deep=config.memory_deep).sum()
    record_size = float(memory_size) / n if n > 0 else 0

    table_stats = {
        "n": n,
        "n_var": len(df.columns),
        "memory_size": memory_size,
        "record_size": record_size,
        "n_cells_missing": 0,
        "n_vars_with_missing": 0,
        "n_vars_all_missing": 0,
    }

    for series_summary in variable_stats.values():
        if series_summary.n_missing > 0:
            table_stats["n_vars_with_missing"] += 1
            table_stats["n_cells_missing"] += series_summary.n_missing
            if series_summary.n_missing == n:
                table_stats["n_vars_all_missing"] += 1

    table_stats["p_cells_missing"] = (
        table_stats["n_cells_missing"] / (table_stats["n"] * table_stats["n_var"])
        if table_stats["n"] > 0 and table_stats["n_var"] > 0
        else 0
    )

    # Variable type counts
    table_stats.update(
        {"types": dict(Counter([v["type"] for v in variable_stats.values()]))}
    )

    return table_stats
