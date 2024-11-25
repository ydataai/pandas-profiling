import numpy as np
import pandas as pd
import pytest

from ydata_profiling.config import Settings
from ydata_profiling.model.summary_algorithms import (
    describe_supported,
    histogram_compute,
)
from ydata_profiling.model.var_description.default import VarDescription


def test_count_summary_sorted(config):
    s = pd.Series([1] + [2] * 1000)
    r: VarDescription
    _, sn, r = describe_supported(config, s, {})
    assert r.value_counts_without_nan.index[0] == 2
    assert r.value_counts_without_nan.index[1] == 1


def test_count_summary_nat(config):
    r: VarDescription
    s = pd.to_datetime(pd.Series([1, 2] + [np.nan, pd.NaT]))
    _, sn, r = describe_supported(config, s, {})
    assert len(r.value_counts_without_nan.index) == 2


def test_count_summary_category(config):
    r: VarDescription
    s = pd.Series(
        pd.Categorical(
            ["Poor", "Neutral"] + [np.nan] * 100,
            categories=["Poor", "Neutral", "Excellent"],
        )
    )
    _, sn, r = describe_supported(config, s, {})
    assert len(r.value_counts_without_nan.index) == 2


@pytest.fixture(scope="class")
def empty_data() -> pd.DataFrame:
    return pd.DataFrame({"A": []})


def test_summary_supported_empty_df(config, empty_data):
    summary: VarDescription
    _, _, summary = describe_supported(config, empty_data["A"], {})
    assert summary.n_missing == 0
    assert summary.n_missing == 0
    assert summary.p_missing == 0
    assert summary.count == 0
    assert summary["n_distinct"] == 0
    assert summary["p_distinct"] == 0
    assert summary["n_unique"] == 0
    assert not summary["is_unique"]


@pytest.fixture
def numpy_array():
    return np.random.choice(list(range(10)), size=1000)


def test_compute_histogram(numpy_array):
    config = Settings()
    n_unique = len(np.unique(numpy_array))
    hist = histogram_compute(config, numpy_array, n_unique)
    assert "histogram" in hist
    assert len(hist["histogram"][0]) == n_unique
    assert len(hist["histogram"][1]) == n_unique + 1
    assert sum(hist["histogram"][0]) == len(numpy_array)

    config.plot.histogram.density = True
    hist = histogram_compute(config, numpy_array, n_unique)
    assert "histogram" in hist
    assert len(hist["histogram"][0]) == n_unique
    assert len(hist["histogram"][1]) == n_unique + 1
    hist_values = hist["histogram"][0] * np.diff(hist["histogram"][1])
    assert sum(hist_values) == pytest.approx(1, 0.1)
