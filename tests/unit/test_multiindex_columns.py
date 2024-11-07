import pandas as pd
import pytest

from ydata_profiling import ProfileReport


@pytest.fixture()
def df():
    df = pd.DataFrame(
        {
            ("foo", "one"): [1, 2, 3],
            ("bar", "two"): [4, 5, 6],
        }
    )
    return df


def test_multiindex_columns(df: pd.DataFrame):
    profile_report = ProfileReport(df, title="Test Report", progress_bar=False)
    assert len(profile_report.to_html()) > 0
