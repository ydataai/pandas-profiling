import os

import pandas as pd

from ydata_profiling.config import Settings
from ydata_profiling.model.summarizer import PandasProfilingSummarizer, format_summary
from ydata_profiling.model.typeset import ProfilingTypeSet

base_path = os.path.abspath(os.path.dirname(__file__))


def test_summarizer_base_types(config: Settings):
    pps = PandasProfilingSummarizer(typeset=ProfilingTypeSet(config))

    _ = format_summary(pps.summarize(config, pd.Series([1, 2, 3, 4, 5]), "Unsupported"))
    _ = format_summary(pps.summarize(config, pd.Series([1, 2, 3, 4, 5]), "Numeric"))
    _ = format_summary(
        pps.summarize(
            config,
            pd.Series(pd.date_range(start="1/1/2018", end="1/08/2018")),
            "DateTime",
        )
    )
    _ = format_summary(
        pps.summarize(config, pd.Series(["abc", "abc", "abba"]), "Categorical")
    )

    _ = format_summary(
        pps.summarize(config, pd.Series([True, False, True, False, False]), "Boolean")
    )


def test_summarizer_url(config: Settings):
    config.vars.url.active = True
    pps = PandasProfilingSummarizer(typeset=ProfilingTypeSet(config))
    _ = format_summary(
        pps.summarize(config, pd.Series(["https://www.example.com"]), "URL")
    )


def test_summarizer_path(config: Settings):
    config.vars.path.active = True
    pps = PandasProfilingSummarizer(typeset=ProfilingTypeSet(config))
    _ = format_summary(
        pps.summarize(
            config,
            pd.Series(
                [
                    os.path.abspath(
                        base_path
                        + r"../../../src/ydata_profiling/model/typeset_does_not_exist.py"
                    )
                ]
            ),
            "Path",
        )
    )


def test_summarizer_file(config: Settings):
    config.vars.path.active = True
    config.vars.file.active = True
    pps = PandasProfilingSummarizer(typeset=ProfilingTypeSet(config))
    _ = format_summary(
        pps.summarize(
            config,
            pd.Series(
                [
                    os.path.abspath(
                        base_path + r"../../../src/ydata_profiling/model/typeset.py"
                    )
                ]
            ),
            "File",
        )
    )


def test_summarizer_image(config: Settings):
    config.vars.path.active = True
    config.vars.file.active = True
    config.vars.image.active = True
    pps = PandasProfilingSummarizer(typeset=ProfilingTypeSet(config))
    _ = format_summary(
        pps.summarize(
            config,
            pd.Series(
                [os.path.abspath(base_path + r"../../../docs/_static/img/cli.png")]
            ),
            "Image",
        )
    )
