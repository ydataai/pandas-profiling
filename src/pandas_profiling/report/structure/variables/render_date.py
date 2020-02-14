from pandas_profiling.config import config
from pandas_profiling.visualisation.plot import mini_histogram, histogram
from pandas_profiling.report.presentation.core import (
    Image,
    Sequence,
    Table,
    VariableInfo,
)


def render_date(summary):
    # TODO: render common?
    template_variables = {}

    image_format = config["plot"]["image_format"].get(str)

    # Top
    info = VariableInfo(
        summary["varid"], summary["varname"], "Date", summary["warnings"]
    )

    table1 = Table(
        [
            {
                "name": "Distinct count",
                "value": summary["n_unique"],
                "fmt": "fmt",
                "alert": False,
            },
            {
                "name": "Unique (%)",
                "value": summary["p_unique"],
                "fmt": "fmt_percent",
                "alert": False,
            },
            {
                "name": "Missing",
                "value": summary["n_missing"],
                "fmt": "fmt",
                "alert": False,
            },
            {
                "name": "Missing (%)",
                "value": summary["p_missing"],
                "fmt": "fmt_percent",
                "alert": False,
            },
            {
                "name": "Memory size",
                "value": summary["memory_size"],
                "fmt": "fmt_bytesize",
                "alert": False,
            },
        ]
    )

    table2 = Table(
        [
            {"name": "Minimum", "value": summary["min"], "fmt": "fmt", "alert": False},
            {"name": "Maximum", "value": summary["max"], "fmt": "fmt", "alert": False},
        ]
    )

    mini_histo = Image(
        mini_histogram(summary["histogram_data"], summary, summary["histogram_bins"]),
        image_format=image_format,
        alt="Mini histogram",
    )

    template_variables["top"] = Sequence(
        [info, table1, table2, mini_histo], sequence_type="grid"
    )

    # Bottom
    bottom = Sequence(
        [
            Image(
                histogram(
                    summary["histogram_data"], summary, summary["histogram_bins"]
                ),
                image_format=image_format,
                alt="Histogram",
                caption="Histogram",
                name="Histogram",
                anchor_id="{varid}histogram".format(varid=summary["varid"]),
            )
        ],
        sequence_type="tabs",
        anchor_id=summary["varid"],
    )

    template_variables["bottom"] = bottom

    return template_variables
