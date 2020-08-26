"""
Test for issue 523:
https://github.com/pandas-profiling/pandas-profiling/issues/XXX
"""
import pandas as pd
import pytest

from pandas_profiling import ProfileReport


@pytest.mark.skipif(
    int(pd.__version__.split(".")[0]) < 1, reason="requires pandas 1 or higher"
)
def test_issue523():
    # https://github.com/pandas-dev/pandas/issues/33803

    data = [
        1871248,
        12522551,
        1489260,
        6657093,
        pd.NA,
        pd.NA,
        pd.NA,
        pd.NA,
        pd.NA,
        1489260,
        pd.NA,
        2468576,
    ]
    df = pd.DataFrame({"col": data}, dtype=pd.Int64Dtype())

    profile_report = ProfileReport(df, title="Test Report")
    assert len(profile_report.to_html()) > 0
