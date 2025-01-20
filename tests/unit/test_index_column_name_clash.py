import pandas as pd
import pytest

from ydata_profiling import ProfileReport


@pytest.fixture()
def df():
    df = pd.DataFrame(
        {
            "foo": [1, 2, 3],
        },
        index=pd.Index([1, 2, 3], name="foo"),
    )
    return df


def test_index_column_name_clash(df: pd.DataFrame):
    profile_report = ProfileReport(df, title="Test Report", progress_bar=False)
    assert len(profile_report.to_html()) > 0
