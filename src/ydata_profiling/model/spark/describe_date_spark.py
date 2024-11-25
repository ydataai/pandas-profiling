from typing import Tuple

import pyspark.sql.functions as F
from numpy import array
from pyspark.sql import DataFrame

from ydata_profiling.config import Settings
from ydata_profiling.model.summary_algorithms import describe_date_1d
from ydata_profiling.model.var_description.default import VarDescription


def date_stats_spark(df: DataFrame, summary: dict) -> dict:
    column = df.columns[0]

    expr = [
        F.min(F.col(column)).alias("min"),
        F.max(F.col(column)).alias("max"),
    ]

    return df.agg(*expr).first().asDict()


@describe_date_1d.register
def describe_date_1d_spark(
    config: Settings, df: DataFrame, summary: VarDescription
) -> Tuple[Settings, DataFrame, VarDescription]:
    """Describe a date series.

    Args:
        series: The Series to describe.
        summary: The dict containing the series description so far.

    Returns:
        A dict containing calculated series description values.
    """
    col_name = df.columns[0]
    stats = date_stats_spark(df, summary)

    summary.update({"min": stats["min"], "max": stats["max"]})

    summary["range"] = summary["max"] - summary["min"]

    # Convert date to numeric so we can compute the histogram
    df = df.withColumn(col_name, F.unix_timestamp(df[col_name]))

    # Get the number of bins
    bins = config.plot.histogram.bins
    bins_arg = "auto" if bins == 0 else min(bins, summary["n_distinct"])

    # Run the histogram
    bin_edges, hist = df.select(col_name).rdd.flatMap(lambda x: x).histogram(bins_arg)

    summary.update({"histogram": (array(hist), array(bin_edges))})
    return config, df, summary
