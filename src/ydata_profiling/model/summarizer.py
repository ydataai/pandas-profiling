from dataclasses import asdict
from typing import Any, Callable, Dict, List, Type, Union

import numpy as np
import pandas as pd
from visions import VisionsBaseType, VisionsTypeset

from ydata_profiling.config import Settings
from ydata_profiling.model import BaseDescription
from ydata_profiling.model.handler import Handler
from ydata_profiling.model.summary_algorithms import (
    describe_boolean_1d,
    describe_categorical_1d,
    describe_date_1d,
    describe_file_1d,
    describe_image_1d,
    describe_numeric_1d,
    describe_path_1d,
    describe_supported,
    describe_text_1d,
    describe_timeseries_1d,
    describe_url_1d,
)
from ydata_profiling.model.var_description.default import VarDescription


class BaseSummarizer(Handler):
    """A base summarizer

    Can be used to define custom summarizations
    """

    def summarize(
        self, config: Settings, series: pd.Series, dtype: Type[VisionsBaseType]
    ) -> VarDescription:
        """

        Returns:
            object:
        """
        _, _, summary = self.handle(str(dtype), config, series, {"type": str(dtype)})
        return summary


class PandasProfilingSummarizer(BaseSummarizer):
    """The default Pandas Profiling summarizer"""

    def __init__(self, typeset: VisionsTypeset, *args, **kwargs):
        summary_map: Dict[str, List[Callable]] = {
            "Unsupported": [
                describe_supported,
            ],
            "Numeric": [
                describe_numeric_1d,
            ],
            "DateTime": [
                describe_date_1d,
            ],
            "Text": [
                describe_text_1d,
            ],
            "Categorical": [
                describe_categorical_1d,
            ],
            "Boolean": [
                describe_boolean_1d,
            ],
            "URL": [
                describe_url_1d,
            ],
            "Path": [
                describe_path_1d,
            ],
            "File": [
                describe_file_1d,
            ],
            "Image": [
                describe_image_1d,
            ],
            "TimeSeries": [
                describe_timeseries_1d,
            ],
        }
        super().__init__(summary_map, typeset, *args, **kwargs)


def format_summary(summary: Union[BaseDescription, VarDescription, dict]) -> dict:
    """Prepare summary for export to json file.

    Args:
        summary (Union[BaseDescription, dict]): summary to export

    Returns:
        dict: summary as dict
    """

    def fmt(v: Any) -> Any:
        if isinstance(v, dict):
            return {k: fmt(va) for k, va in v.items()}
        else:
            if isinstance(v, pd.Series):
                return fmt(v.to_dict())
            elif (
                isinstance(v, tuple)
                and len(v) == 2
                and all(isinstance(x, np.ndarray) for x in v)
            ):
                return {"counts": v[0].tolist(), "bin_edges": v[1].tolist()}
            else:
                return v

    if isinstance(summary, BaseDescription):
        summary = asdict(summary)

    summary = {k: fmt(v) for k, v in summary.items()}
    return summary


def _redact_column(column: Dict[str, Any]) -> Dict[str, Any]:
    def redact_key(data: Dict[str, Any]) -> Dict[str, Any]:
        return {f"REDACTED_{i}": v for i, (_, v) in enumerate(data.items())}

    def redact_value(data: Dict[str, Any]) -> Dict[str, Any]:
        return {k: f"REDACTED_{i}" for i, (k, _) in enumerate(data.items())}

    keys_to_redact = [
        "block_alias_char_counts",
        "block_alias_values",
        "category_alias_char_counts",
        "category_alias_values",
        "character_counts",
        "script_char_counts",
        "value_counts_index_sorted",
        "value_counts_without_nan",
        "word_counts",
    ]

    values_to_redact = ["first_rows"]

    for field in keys_to_redact:
        if field not in column:
            continue
        is_dict = (isinstance(v, dict) for v in column[field].values())
        if any(is_dict):
            column[field] = {k: redact_key(v) for k, v in column[field].items()}
        else:
            column[field] = redact_key(column[field])

    for field in values_to_redact:
        if field not in column:
            continue
        is_dict = (isinstance(v, dict) for v in column[field].values())
        if any(is_dict):
            column[field] = {k: redact_value(v) for k, v in column[field].items()}
        else:
            column[field] = redact_value(column[field])

    return column


def redact_summary(summary: dict, config: Settings) -> dict:
    """Redact summary to export to json file.

    Args:
        summary (dict): summary to redact

    Returns:
        dict: redacted summary
    """
    for _, col in summary["variables"].items():
        if (config.vars.cat.redact and col["type"] == "Categorical") or (
            config.vars.text.redact and col["type"] == "Text"
        ):
            col = _redact_column(col)

    return summary
