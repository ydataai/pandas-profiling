import functools

import numpy as np
import pandas as pd
from pandas.api import types as pdt
from visions.backends.pandas.series_utils import series_handle_nulls

from pandas_profiling.config import config


def is_nullable(series, state) -> bool:
    return series.count() > 0


def try_func(fn):
    @functools.wraps(fn)
    def inner(series: pd.Series, *args, **kwargs) -> bool:
        try:
            return fn(series, *args, **kwargs)
        except:  # noqa: E722
            return False

    return inner


def get_boolean_map():
    bool_map = {}
    for true_value, false_value in config["vars"]["bool"]["mappings"].get(list):
        bool_map[true_value] = True
        bool_map[false_value] = False
    return bool_map


PP_bool_map = get_boolean_map()


def string_is_bool(series, state) -> bool:
    @series_handle_nulls
    @try_func
    def tester(s: pd.Series, state: dict) -> bool:
        return s.str.lower().isin(PP_bool_map.keys()).all()

    if pdt.is_categorical_dtype(series):
        return False

    return tester(series, state)


def string_to_bool(series, state):
    return series.str.lower().map(PP_bool_map)


def numeric_is_category(series, state):
    n_unique = series.nunique()
    threshold = config["vars"]["num"]["low_categorical_threshold"].get(int)
    return 1 <= n_unique <= threshold


def to_category(series, state):
    hasnans = series.hasnans
    val = series.astype(str)
    if hasnans:
        val = val.replace("nan", np.nan)

    if int(pd.__version__.split(".")[0]) >= 1:
        val = val.astype("string")
    return val


@series_handle_nulls
def series_is_string(series: pd.Series, state: dict) -> bool:
    if not all(isinstance(v, str) for v in series.values[0:5]):
        return False
    try:
        return (series.astype(str).values == series.values).all()
    except (TypeError, ValueError):
        return False


@series_handle_nulls
def category_is_numeric(series, state):
    if pdt.is_bool_dtype(series) or object_is_bool(series, state):
        return False

    try:
        _ = series.astype(float)
        r = pd.to_numeric(series, errors="coerce")
        if r.hasnans and r.count() == 0:
            return False
    except:  # noqa: E722
        return False

    return not numeric_is_category(series, state)


def category_to_numeric(series, state):
    return pd.to_numeric(series, errors="coerce")


hasnan_bool_name = "boolean" if int(pd.__version__.split(".")[0]) >= 1 else "Bool"


def to_bool(series: pd.Series) -> pd.Series:
    dtype = hasnan_bool_name if series.hasnans else bool
    return series.astype(dtype)


@series_handle_nulls
def object_is_bool(series: pd.Series, state) -> bool:
    if pdt.is_object_dtype(series):
        bool_set = {True, False}
        try:
            ret = all(item in bool_set for item in series)
        except:  # noqa: E722
            ret = False

        return ret
    return False
