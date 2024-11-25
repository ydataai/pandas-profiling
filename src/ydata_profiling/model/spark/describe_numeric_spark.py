from typing import Tuple

import numpy as np
import pyspark.sql.functions as F
from pyspark.sql import DataFrame

from ydata_profiling.config import Settings
from ydata_profiling.model.summary_algorithms import (
    describe_numeric_1d,
    histogram_compute,
)
from ydata_profiling.model.var_description.default import VarDescription


def numeric_stats_spark(df: DataFrame, summary: VarDescription) -> dict:
    column = df.columns[0]

    expr = [
        F.mean(F.col(column)).alias("mean"),
        F.stddev(F.col(column)).alias("std"),
        F.variance(F.col(column)).alias("variance"),
        F.min(F.col(column)).alias("min"),
        F.max(F.col(column)).alias("max"),
        F.kurtosis(F.col(column)).alias("kurtosis"),
        F.skewness(F.col(column)).alias("skewness"),
        F.sum(F.col(column)).alias("sum"),
    ]
    return df.agg(*expr).first().asDict()


@describe_numeric_1d.register
def describe_numeric_1d_spark(
    config: Settings, df: DataFrame, summary: VarDescription
) -> Tuple[Settings, DataFrame, VarDescription]:
    """Describe a boolean series.

    Args:
        series: The Series to describe.
        summary: The dict containing the series description so far.

    Returns:
        A dict containing calculated series description values.
    """

    stats = numeric_stats_spark(df, summary)
    summary["min"] = stats["min"]
    summary["max"] = stats["max"]
    summary["mean"] = stats["mean"]
    summary["std"] = stats["std"]
    summary["variance"] = stats["variance"]
    summary["skewness"] = stats["skewness"]
    summary["kurtosis"] = stats["kurtosis"]
    summary["sum"] = stats["sum"]

    value_counts = summary.value_counts

    n_infinite = (
        value_counts.where(F.col(df.columns[0]).isin([np.inf, -np.inf]))
        .agg(F.sum(F.col("count")).alias("count"))
        .first()
    )
    if n_infinite is None or n_infinite["count"] is None:
        n_infinite = 0
    else:
        n_infinite = n_infinite["count"]
    summary["n_infinite"] = n_infinite

    n_zeros = value_counts.where(f"{df.columns[0]} = 0").first()
    if n_zeros is None:
        n_zeros = 0
    else:
        n_zeros = n_zeros["count"]
    summary["n_zeros"] = n_zeros

    n_negative = (
        value_counts.where(f"{df.columns[0]} < 0")
        .agg(F.sum(F.col("count")).alias("count"))
        .first()
    )
    if n_negative is None or n_negative["count"] is None:
        n_negative = 0
    else:
        n_negative = n_negative["count"]
    summary["n_negative"] = n_negative

    quantiles = config.vars.num.quantiles
    quantile_threshold = 0.05

    summary.update(
        {
            f"{percentile:.0%}": value
            for percentile, value in zip(
                quantiles,
                df.stat.approxQuantile(
                    f"{df.columns[0]}",
                    quantiles,
                    quantile_threshold,
                ),
            )
        }
    )

    median = summary["50%"]

    summary["mad"] = df.select(
        (F.abs(F.col(f"{df.columns[0]}").cast("int") - median)).alias("abs_dev")
    ).stat.approxQuantile("abs_dev", [0.5], quantile_threshold)[0]

    # FIXME: move to fmt
    summary["p_negative"] = summary["n_negative"] / summary.n
    summary["range"] = summary["max"] - summary["min"]
    summary["iqr"] = summary["75%"] - summary["25%"]
    summary["cv"] = summary["std"] / summary["mean"] if summary["mean"] else np.NaN
    summary["p_zeros"] = summary["n_zeros"] / summary.n
    summary["p_infinite"] = summary["n_infinite"] / summary.n

    # TODO - enable this feature
    # because spark doesn't have an indexing system, there isn't really the idea of monotonic increase/decrease
    # [feature enhancement] we could implement this if the user provides an ordinal column to use for ordering
    # ... https://stackoverflow.com/questions/60221841/how-to-detect-monotonic-decrease-in-pyspark
    summary["monotonic"] = 0

    # this function only displays the top N (see config) values for a histogram.
    # This might be confusing if there are a lot of values of equal magnitude, but we cannot bring all the values to
    # display in pandas display
    # the alternative is to do this in spark natively, but it is not trivial
    infinity_values = [np.inf, -np.inf]
    infinity_index = summary.value_counts_without_nan.index.isin(infinity_values)

    summary.update(
        histogram_compute(
            config,
            summary.value_counts_without_nan[~infinity_index].index.values,
            summary["n_distinct"],
            weights=summary.value_counts_without_nan[~infinity_index].values,
        )
    )

    return config, df, summary
