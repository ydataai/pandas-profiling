from typing import Tuple
from urllib.parse import urlsplit

import pandas as pd

from ydata_profiling.config import Settings
from ydata_profiling.model.summary_algorithms import describe_url_1d
from ydata_profiling.model.var_description.default import VarDescription


def url_summary(series: pd.Series) -> dict:
    """

    Args:
        series: series to summarize

    Returns:

    """
    summary = {
        "scheme_counts": series.map(lambda x: x.scheme).value_counts(),
        "netloc_counts": series.map(lambda x: x.netloc).value_counts(),
        "path_counts": series.map(lambda x: x.path).value_counts(),
        "query_counts": series.map(lambda x: x.query).value_counts(),
        "fragment_counts": series.map(lambda x: x.fragment).value_counts(),
    }

    return summary


@describe_url_1d.register
def pandas_describe_url_1d(
    config: Settings, series: pd.Series, summary: VarDescription
) -> Tuple[Settings, pd.Series, VarDescription]:
    """Describe a url series.

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

    # Transform
    series = series.apply(urlsplit)

    # Update
    summary.update(url_summary(series))

    return config, series, summary
