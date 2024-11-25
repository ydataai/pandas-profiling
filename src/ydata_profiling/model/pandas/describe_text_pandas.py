from typing import Tuple

import pandas as pd

from ydata_profiling.config import Settings
from ydata_profiling.model.pandas.describe_categorical_pandas import (
    length_summary_vc,
    unicode_summary_vc,
    word_summary_vc,
)
from ydata_profiling.model.summary_algorithms import (
    describe_text_1d,
    histogram_compute,
    series_handle_nulls,
    series_hashable,
)
from ydata_profiling.model.var_description.default import VarDescription


@describe_text_1d.register
@series_hashable
@series_handle_nulls
def pandas_describe_text_1d(
    config: Settings,
    series: pd.Series,
    summary: VarDescription,
) -> Tuple[Settings, pd.Series, VarDescription]:
    """Describe string series.

    Args:
        config: report Settings object
        series: The Series to describe.
        summary: The dict containing the series description so far.

    Returns:
        A dict containing calculated series description values.
    """

    series = series.astype(str)

    # Only run if at least 1 non-missing value
    value_counts = summary.value_counts_without_nan
    value_counts.index = value_counts.index.astype(str)

    summary.update({"first_rows": series.head(5)})

    if config.vars.text.length:
        summary.update(length_summary_vc(value_counts))
        summary.update(
            histogram_compute(
                config,
                summary["length_histogram"].index.values,
                len(summary["length_histogram"]),
                name="histogram_length",
                weights=summary["length_histogram"].values,
            )
        )

    if config.vars.text.characters:
        summary.update(unicode_summary_vc(value_counts))

    if config.vars.text.words:
        summary.update(word_summary_vc(value_counts, config.vars.cat.stop_words))

    return config, series, summary
