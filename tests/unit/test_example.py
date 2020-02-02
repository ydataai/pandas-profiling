import sys

import pandas as pd
import numpy as np

from pandas_profiling import ProfileReport


def test_example(get_data_file, test_output_dir):
    file_name = get_data_file(
        "meteorites.csv",
        "https://data.nasa.gov/api/views/gh4g-9sfh/rows.csv?accessType=DOWNLOAD",
    )

    df = pd.read_csv(file_name)
    # Note: Pandas does not support dates before 1880, so we ignore these for this analysis
    df["year"] = pd.to_datetime(df["year"], errors="coerce")

    # Example: Constant variable
    df["source"] = "NASA"

    # Example: Boolean variable
    df["boolean"] = np.random.choice([True, False], df.shape[0])

    # Example: Mixed with base types
    df["mixed"] = np.random.choice([1, "A"], df.shape[0])

    # Example: Highly correlated variables
    df["reclat_city"] = df["reclat"] + np.random.normal(scale=5, size=(len(df)))

    # Example: Duplicate observations
    duplicates_to_add = pd.DataFrame(df.iloc[0:10])
    duplicates_to_add["name"] += " copy"

    df = df.append(duplicates_to_add, ignore_index=True)

    output_file = test_output_dir / "profile.html"
    profile = ProfileReport(
        df, title="NASA Meteorites", samples={"head": 5, "tail": 5}, sort="ascending"
    )
    profile.to_file(output_file=output_file)
    assert (test_output_dir / "profile.html").exists(), "Output file does not exist"
    assert (
        type(profile.get_description()) == dict
        and len(profile.get_description().items()) == 7
    ), "Unexpected result"
    if sys.version_info[1] >= 6:
        assert list(profile.get_description()["variables"].keys()) == [
            "boolean",
            "fall",
            "GeoLocation",
            "id",
            "mass (g)",
            "mixed",
            "name",
            "nametype",
            "recclass",
            "reclat",
            "reclat_city",
            "reclong",
            "source",
            "year",
        ], "Ascending sort did not work"
