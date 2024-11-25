from ydata_profiling.config import Settings
from ydata_profiling.model.var_description.default import VarDescription
from ydata_profiling.report.formatters import (
    fmt,
    fmt_bytesize,
    fmt_monotonic,
    fmt_numeric,
    fmt_percent,
    fmt_timespan_timedelta,
)
from ydata_profiling.report.presentation.core import (
    Container,
    FrequencyTable,
    Image,
    Table,
    VariableInfo,
)
from ydata_profiling.report.structure.variables.render_common import render_common
from ydata_profiling.visualisation.plot import (
    histogram,
    mini_ts_plot,
    plot_acf_pacf,
    plot_timeseries_gap_analysis,
)


def _render_gap_tab(config: Settings, summary: dict) -> Container:
    gap_stats = [
        {
            "name": "number of gaps",
            "value": fmt_numeric(
                summary["gap_stats"]["n_gaps"], precision=config.report.precision
            ),
        },
        {
            "name": "min",
            "value": fmt_timespan_timedelta(
                summary["gap_stats"]["min"], precision=config.report.precision
            ),
        },
        {
            "name": "max",
            "value": fmt_timespan_timedelta(
                summary["gap_stats"]["max"], precision=config.report.precision
            ),
        },
        {
            "name": "mean",
            "value": fmt_timespan_timedelta(
                summary["gap_stats"]["mean"], precision=config.report.precision
            ),
        },
        {
            "name": "std",
            "value": fmt_timespan_timedelta(
                summary["gap_stats"]["std"], precision=config.report.precision
            ),
        },
    ]

    gap_table = Table(
        gap_stats,
        name="Gap statistics",
        style=config.html.style,
    )

    gap_plot = Image(
        plot_timeseries_gap_analysis(
            config, summary["gap_stats"]["series"], summary["gap_stats"]["gaps"]
        ),
        image_format=config.plot.image_format,
        alt="Gap plot",
        name="",
        anchor_id=f"{summary['varid']}_gap_plot",
    )
    return Container(
        [gap_table, gap_plot],
        image_format=config.plot.image_format,
        sequence_type="grid",
        name="Gap analysis",
        anchor_id=f"{summary['varid']}_gap_analysis",
    )


def render_timeseries(config: Settings, summary: VarDescription) -> dict:
    varid = summary["varid"]
    template_variables = render_common(config, summary)
    image_format = config.plot.image_format
    name = "Numeric time series"

    # Top
    info = VariableInfo(
        summary["varid"],
        summary["varname"],
        name,
        summary["alerts"],
        summary["description"],
        style=config.html.style,
    )

    table1 = Table(
        [
            {
                "name": "Distinct",
                "value": fmt(summary["n_distinct"]),
                "alert": "n_distinct" in summary["alert_fields"],
            },
            {
                "name": "Distinct (%)",
                "value": fmt_percent(summary["p_distinct"]),
                "alert": "p_distinct" in summary["alert_fields"],
            },
            {
                "name": "Missing",
                "value": fmt(summary.n_missing),
                "alert": "n_missing" in summary["alert_fields"],
            },
            {
                "name": "Missing (%)",
                "value": fmt_percent(summary.p_missing),
                "alert": "p_missing" in summary["alert_fields"],
            },
            {
                "name": "Infinite",
                "value": fmt(summary["n_infinite"]),
                "alert": "n_infinite" in summary["alert_fields"],
            },
            {
                "name": "Infinite (%)",
                "value": fmt_percent(summary["p_infinite"]),
                "alert": "p_infinite" in summary["alert_fields"],
            },
        ],
        style=config.html.style,
    )

    table2 = Table(
        [
            {
                "name": "Mean",
                "value": fmt_numeric(
                    summary["mean"], precision=config.report.precision
                ),
                "alert": False,
            },
            {
                "name": "Minimum",
                "value": fmt_numeric(summary["min"], precision=config.report.precision),
                "alert": False,
            },
            {
                "name": "Maximum",
                "value": fmt_numeric(summary["max"], precision=config.report.precision),
                "alert": False,
            },
            {
                "name": "Zeros",
                "value": fmt(summary["n_zeros"]),
                "alert": "n_zeros" in summary["alert_fields"],
            },
            {
                "name": "Zeros (%)",
                "value": fmt_percent(summary["p_zeros"]),
                "alert": "p_zeros" in summary["alert_fields"],
            },
            {
                "name": "Memory size",
                "value": fmt_bytesize(summary.memory_size),
                "alert": False,
            },
        ],
        style=config.html.style,
    )

    mini_plot = Image(
        mini_ts_plot(config, summary["series"]),
        image_format=image_format,
        alt="Mini TS plot",
    )

    template_variables["top"] = Container(
        [info, table1, table2, mini_plot], sequence_type="grid"
    )

    quantile_statistics = Table(
        [
            {
                "name": "Minimum",
                "value": fmt_numeric(summary["min"], precision=config.report.precision),
            },
            {
                "name": "5-th percentile",
                "value": fmt_numeric(summary["5%"], precision=config.report.precision),
            },
            {
                "name": "Q1",
                "value": fmt_numeric(summary["25%"], precision=config.report.precision),
            },
            {
                "name": "median",
                "value": fmt_numeric(summary["50%"], precision=config.report.precision),
            },
            {
                "name": "Q3",
                "value": fmt_numeric(summary["75%"], precision=config.report.precision),
            },
            {
                "name": "95-th percentile",
                "value": fmt_numeric(summary["95%"], precision=config.report.precision),
            },
            {
                "name": "Maximum",
                "value": fmt_numeric(summary["max"], precision=config.report.precision),
            },
            {
                "name": "Range",
                "value": fmt_numeric(
                    summary["range"], precision=config.report.precision
                ),
            },
            {
                "name": "Interquartile range (IQR)",
                "value": fmt_numeric(summary["iqr"], precision=config.report.precision),
            },
        ],
        name="Quantile statistics",
        style=config.html.style,
    )

    descriptive_statistics = Table(
        [
            {
                "name": "Standard deviation",
                "value": fmt_numeric(summary["std"], precision=config.report.precision),
            },
            {
                "name": "Coefficient of variation (CV)",
                "value": fmt_numeric(summary["cv"], precision=config.report.precision),
            },
            {
                "name": "Kurtosis",
                "value": fmt_numeric(
                    summary["kurtosis"], precision=config.report.precision
                ),
            },
            {
                "name": "Mean",
                "value": fmt_numeric(
                    summary["mean"], precision=config.report.precision
                ),
            },
            {
                "name": "Median Absolute Deviation (MAD)",
                "value": fmt_numeric(summary["mad"], precision=config.report.precision),
            },
            {
                "name": "Skewness",
                "value": fmt_numeric(
                    summary["skewness"], precision=config.report.precision
                ),
                "class": "alert" if "skewness" in summary["alert_fields"] else "",
            },
            {
                "name": "Sum",
                "value": fmt_numeric(summary["sum"], precision=config.report.precision),
            },
            {
                "name": "Variance",
                "value": fmt_numeric(
                    summary["variance"], precision=config.report.precision
                ),
            },
            {
                "name": "Monotonicity",
                "value": fmt_monotonic(summary["monotonic"]),
            },
            {
                "name": "Augmented Dickey-Fuller test p-value",
                "value": fmt_numeric(summary["addfuller"]),
            },
        ],
        name="Descriptive statistics",
        style=config.html.style,
    )

    statistics = Container(
        [quantile_statistics, descriptive_statistics],
        anchor_id=f"{varid}statistics",
        name="Statistics",
        sequence_type="grid",
    )

    if isinstance(summary["histogram"], list):
        hist_data = histogram(
            config,
            [x[0] for x in summary["histogram"]],
            [x[1] for x in summary["histogram"]],
        )
        hist_caption = f"<strong>Histogram with fixed size bins</strong> (bins={len(summary['histogram'][0][1]) - 1})"
    else:
        hist_data = histogram(config, *summary["histogram"])
        hist_caption = f"<strong>Histogram with fixed size bins</strong> (bins={len(summary['histogram'][1]) - 1})"

    hist = Image(
        hist_data,
        image_format=image_format,
        alt="Histogram",
        caption=hist_caption,
        name="Histogram",
        anchor_id=f"{varid}histogram",
    )

    fq = FrequencyTable(
        template_variables["freq_table_rows"],
        name="Common values",
        anchor_id=f"{varid}common_values",
        redact=False,
    )

    evs = Container(
        [
            FrequencyTable(
                template_variables["firstn_expanded"],
                name=f"Minimum {config.n_extreme_obs} values",
                anchor_id=f"{varid}firstn",
                redact=False,
            ),
            FrequencyTable(
                template_variables["lastn_expanded"],
                name=f"Maximum {config.n_extreme_obs} values",
                anchor_id=f"{varid}lastn",
                redact=False,
            ),
        ],
        sequence_type="tabs",
        name="Extreme values",
        anchor_id=f"{varid}extreme_values",
    )

    acf_pacf = Image(
        plot_acf_pacf(config, summary["series"]),
        image_format=image_format,
        alt="Autocorrelation",
        caption="<strong>ACF and PACF</strong>",
        name="Autocorrelation",
        anchor_id=f"{varid}acf_pacf",
    )

    ts_plot = Image(
        mini_ts_plot(config, summary["series"], figsize=(7, 3)),
        image_format=image_format,
        alt="Time-series plot",
        name="Time-series",
        anchor_id=f"{varid}_ts_plot",
    )

    ts_gap = _render_gap_tab(config, summary)

    template_variables["bottom"] = Container(
        [statistics, hist, ts_plot, ts_gap, fq, evs, acf_pacf],
        sequence_type="tabs",
        anchor_id=f"{varid}bottom",
    )

    return template_variables
