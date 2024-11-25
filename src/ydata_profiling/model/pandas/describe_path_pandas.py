import os
from typing import Tuple

import pandas as pd

from ydata_profiling.config import Settings
from ydata_profiling.model.summary_algorithms import describe_path_1d
from ydata_profiling.model.var_description.default import VarDescription


def path_summary(series: pd.Series) -> dict:
    """

    Args:
        series: series to summarize

    Returns:

    """

    # TODO: optimize using value counts
    summary = {
        "common_prefix": (
            os.path.commonprefix(series.values.tolist()) or "No common prefix"
        ),
        "stem_counts": series.map(lambda x: os.path.splitext(x)[0]).value_counts(),
        "suffix_counts": series.map(lambda x: os.path.splitext(x)[1]).value_counts(),
        "name_counts": series.map(lambda x: os.path.basename(x)).value_counts(),
        "parent_counts": series.map(lambda x: os.path.dirname(x)).value_counts(),
        "anchor_counts": series.map(lambda x: os.path.splitdrive(x)[0]).value_counts(),
    }

    summary["n_stem_unique"] = len(summary["stem_counts"])
    summary["n_suffix_unique"] = len(summary["suffix_counts"])
    summary["n_name_unique"] = len(summary["name_counts"])
    summary["n_parent_unique"] = len(summary["parent_counts"])
    summary["n_anchor_unique"] = len(summary["anchor_counts"])

    return summary


@describe_path_1d.register
def pandas_describe_path_1d(
    config: Settings, series: pd.Series, summary: VarDescription
) -> Tuple[Settings, pd.Series, VarDescription]:
    """Describe a path series.

    Args:
        config: report Settings object
        series: The Series to describe.
        summary: The dict containing the series description so far.

    Returns:
        A dict containing calculated series description values.
    """

    # Make sure we deal with strings (Issue #100)
    if series.hasnans:
        raise ValueError("May not contain NaNs")
    if not hasattr(series, "str"):
        raise ValueError("series should have .str accessor")

    summary.update(path_summary(series))

    return config, series, summary
