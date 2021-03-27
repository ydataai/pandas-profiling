import numpy as np
import pandas as pd
import pytest

from pandas_profiling.model.summary_algorithms import (
    describe_counts,
    describe_generic,
    describe_supported,
)


def test_count_summary_sorted():
    s = pd.Series([1] + [2] * 1000)
    sn, r = describe_counts(s, {})
    assert r["value_counts_without_nan"].index[0] == 2
    assert r["value_counts_without_nan"].index[1] == 1


def test_count_summary_nat():
    s = pd.to_datetime(pd.Series([1, 2] + [np.nan, pd.NaT]))
    sn, r = describe_counts(s, {})
    assert len(r["value_counts_without_nan"].index) == 2


def test_count_summary_category():
    s = pd.Categorical(
        ["Poor", "Neutral"] + [np.nan] * 100,
        categories=["Poor", "Neutral", "Excellent"],
    )
    sn, r = describe_counts(s, {})
    assert len(r["value_counts_without_nan"].index) == 2


@pytest.fixture(scope="class")
def empty_data() -> pd.DataFrame:
    return pd.DataFrame({"A": []})


def test_count_summary_empty_df(empty_data):
    _, result = describe_counts(empty_data["A"], {})
    assert result["n_missing"] == 0
    assert "p_missing" not in result


def test_summary_generic_empty_df(empty_data):
    series, summary = describe_counts(empty_data["A"], {})
    _, result = describe_generic(series, summary)
    assert result["n_missing"] == 0
    assert result["p_missing"] == 0
    assert result["count"] == 0


def test_summary_supported_empty_df(empty_data):
    series, summary = describe_counts(empty_data["A"], {})
    series, summary = describe_generic(series, summary)
    _, result = describe_supported(series, summary)
    assert result["n_distinct"] == 0
    assert result["p_distinct"] == 0
    assert result["n_unique"] == 0
    assert not result["is_unique"]
