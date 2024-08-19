"""
Test for issue 1631:
https://github.com/ydataai/ydata-profiling/issues/1631
"""
import pandas as pd

from ydata_profiling import ProfileReport


def test_issue1631(test_output_dir):
    data = {
        "value": [1, 2, 3, 4],
        "datetime": [
            "2022-10-01 00:10:00",
            "2022-10-02 00:20:00",
            "2022-10-03 00:30:00",
            "2022-10-04 00:40:00",
        ],
    }
    df = pd.DataFrame(data)
    df["datetime"] = pd.to_datetime(df["datetime"], errors="raise")
    df.set_index("datetime", inplace=True)
    profile = ProfileReport(df, tsmode=True, type_schema={"value": "timeseries"})
    output_file = test_output_dir / "issue1631.html"
    profile.to_file(output_file)

    assert output_file.exists()
