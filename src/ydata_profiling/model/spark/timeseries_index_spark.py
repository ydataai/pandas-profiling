"""Compute statistical description of datasets."""

from pyspark.sql import DataFrame

from ydata_profiling.config import Settings
from ydata_profiling.model.timeseries_index import get_time_index_description


@get_time_index_description.register
def spark_get_time_index_description(
    config: Settings,
    df: DataFrame,
    table_stats: dict,
) -> dict:
    return {}
