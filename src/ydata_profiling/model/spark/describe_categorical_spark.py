from typing import Tuple

from pyspark.sql import DataFrame

from ydata_profiling.config import Settings
from ydata_profiling.model.summary_algorithms import describe_categorical_1d
from ydata_profiling.model.var_description.default import VarDescription


@describe_categorical_1d.register
def describe_categorical_1d_spark(
    config: Settings, df: DataFrame, summary: VarDescription
) -> Tuple[Settings, DataFrame, VarDescription]:
    """Describe a categorical series.

    Args:
        series: The Series to describe.
        summary: The dict containing the series description so far.

    Returns:
        A dict containing calculated series description values.
    """

    # FIXME: cat description
    redact = config.vars.cat.redact
    if not redact:
        summary["first_rows"] = df.limit(5).toPandas().squeeze("columns")

    return config, df, summary
