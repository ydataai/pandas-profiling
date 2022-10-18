"""
Test for issue 545:
https://github.com/pandas-profiling/pandas-profiling/issues/545
"""

import pandas as pd
import pytest

from pandas_profiling import ProfileReport


def pandas_version():
    return tuple(int(s) for s in pd.__version__.split("."))


@pytest.mark.skipif(
    pandas_version() <= (1, 1, 0), reason="requires pandas 1.1.1 or higher"
)
def test_issue545(get_data_file):
    file_name = get_data_file(
        "sample_eda_df.pkl",
        "https://github.com/justinsola/justinsola.github.com/raw/master/files/sample_eda_df.pkl",
    )

    sample_eda_df = pd.read_pickle(str(file_name))
    sample_profile = ProfileReport(
        sample_eda_df,
        title="Sample Profiling Report",
        explorative=True,
        pool_size=1,
        progress_bar=False,
    )
    assert len(sample_profile.to_html()) > 0
