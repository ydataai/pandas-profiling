from pyspark.sql import DataFrame

from ydata_profiling.config import Settings
from ydata_profiling.model.var_description.counts import VarCounts


def get_counts_spark(config: Settings, series: DataFrame) -> VarCounts:
    """Get a VarCounts object for a spark series."""
    length = series.count()

    value_counts = series.groupBy(series.columns).count()
    value_counts = value_counts.sort("count", ascending=False).persist()
    value_counts_index_sorted = value_counts.sort(series.columns[0], ascending=True)

    n_missing = value_counts.where(value_counts[series.columns[0]].isNull()).first()
    if n_missing is None:
        n_missing = 0
    else:
        n_missing = n_missing["count"]

    # FIXME: reduce to top-n and bottom-n
    value_counts_index_sorted = (
        value_counts_index_sorted.limit(200)
        .toPandas()
        .set_index(series.columns[0], drop=True)
        .squeeze(axis="columns")
    )

    # this is necessary as freqtables requires value_counts_without_nan
    # to be a pandas series. However, if we try to get everything into
    # pandas we will definitly crash the server
    value_counts_without_nan = (
        value_counts.dropna()
        .limit(200)
        .toPandas()
        .set_index(series.columns[0], drop=True)
        .squeeze(axis="columns")
    )

    # FIXME: This is not correct, but used to fulfil render expectations
    # @chanedwin
    memory_size = 0

    return VarCounts(
        hashable=False,
        value_counts_without_nan=value_counts_without_nan,
        value_counts_index_sorted=value_counts_index_sorted,
        ordering=False,
        n_missing=n_missing,
        n=length,
        p_missing=n_missing / length,
        count=length - n_missing,
        memory_size=memory_size,
        value_counts=value_counts.persist(),
    )
