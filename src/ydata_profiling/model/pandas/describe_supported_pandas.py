from typing import Tuple

import pandas as pd

from ydata_profiling.config import Settings
from ydata_profiling.model.pandas.var_description.default_pandas import (
    get_default_pandas_description,
)
from ydata_profiling.model.summary_algorithms import describe_supported
from ydata_profiling.model.var_description.default import VarDescription


@describe_supported.register
def pandas_describe_supported(
    config: Settings, series: pd.Series, description: dict
) -> Tuple[Settings, pd.Series, VarDescription]:
    """Describe a supported series.

    Args:
        config: report Settings object
        series: The Series to describe.
        series_description: The dict containing the series description so far.

    Returns:
        A dict containing calculated series description values.
    """

    series_description = get_default_pandas_description(config, series, description)

    return config, series, series_description
