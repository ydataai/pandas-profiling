from typing import Tuple

from pyspark.sql import DataFrame

from ydata_profiling.config import Settings
from ydata_profiling.model.summary_algorithms import describe_boolean_1d
from ydata_profiling.model.var_description.default import VarDescription


@describe_boolean_1d.register
def describe_boolean_1d_spark(
    config: Settings, df: DataFrame, summary: VarDescription
) -> Tuple[Settings, DataFrame, VarDescription]:
    """Describe a boolean series.

    Args:
        series: The Series to describe.
        summary: The dict containing the series description so far.

    Returns:
        A dict containing calculated series description values.
    """

    value_counts = summary.value_counts

    # get the most common boolean value and its frequency
    top = value_counts.first()
    summary.update({"top": top[0], "freq": top[1]})

    return config, df, summary
