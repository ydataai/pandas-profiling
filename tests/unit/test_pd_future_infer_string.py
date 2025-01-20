import pandas as pd
import pytest

from ydata_profiling import ProfileReport


@pytest.fixture()
def df():
    df = pd.DataFrame(
        {
            "foo": [1, 2, 3],
            "bar": ["", "", ""],
        }
    )
    return df


def test_pd_future_infer_string(df: pd.DataFrame):
    with pd.option_context("future.infer_string", True):
        profile_report = ProfileReport(df, title="Test Report", progress_bar=False)
        assert len(profile_report.to_html()) > 0
