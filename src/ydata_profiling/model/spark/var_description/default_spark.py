from __future__ import annotations

from pyspark.sql import DataFrame

from ydata_profiling.config import Settings
from ydata_profiling.model.spark.var_description.counts_spark import get_counts_spark
from ydata_profiling.model.var_description.default import VarDescription


def get_default_spark_description(
    config: Settings, series: DataFrame, init_dict: dict
) -> VarDescription:
    var_counts = get_counts_spark(config, series)

    count = var_counts.count
    n_distinct = var_counts.value_counts.count()

    p_distinct = n_distinct / count if count > 0 else 0

    n_unique = var_counts.value_counts.where("count == 1").count()
    is_unique = n_unique == count
    p_unique = n_unique / count  if count > 0 else 0

    init_dict.update(
        {
            "n_distinct": n_distinct,
            "p_distinct": p_distinct,
            "is_unique": is_unique,
            "n_unique": n_unique,
            "p_unique": p_unique,
        }
    )

    return VarDescription(
        n=var_counts.n,
        count=var_counts.count,
        n_missing=var_counts.n_missing,
        p_missing=var_counts.p_missing,
        hashable=var_counts.hashable,
        memory_size=var_counts.memory_size,
        ordering=var_counts.ordering,
        value_counts_index_sorted=var_counts.value_counts_index_sorted,
        value_counts_without_nan=var_counts.value_counts_without_nan,
        value_counts=var_counts.value_counts,
        var_specific=init_dict,
    )
