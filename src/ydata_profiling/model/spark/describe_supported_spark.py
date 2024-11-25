from typing import Tuple

from pyspark.sql import DataFrame

from ydata_profiling.config import Settings
from ydata_profiling.model.spark.var_description.default_spark import (
    get_default_spark_description,
)
from ydata_profiling.model.summary_algorithms import describe_supported
from ydata_profiling.model.var_description.default import VarDescription


@describe_supported.register
def describe_supported_spark(
    config: Settings, series: DataFrame, summary: dict
) -> Tuple[Settings, DataFrame, VarDescription]:
    """Describe a supported series.
    Args:
        series: The Series to describe.
        series_description: The dict containing the series description so far.
    Returns:
        A dict containing calculated series description values.
    """

    series_description = get_default_spark_description(config, series, summary)

    return config, series, series_description
