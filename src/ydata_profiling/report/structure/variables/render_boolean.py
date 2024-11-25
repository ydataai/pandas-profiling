from typing import List

from ydata_profiling.config import Settings
from ydata_profiling.model.var_description.default import VarDescription
from ydata_profiling.report.formatters import fmt, fmt_bytesize, fmt_percent
from ydata_profiling.report.presentation.core import (
    Container,
    FrequencyTable,
    FrequencyTableSmall,
    Image,
    Table,
    VariableInfo,
)
from ydata_profiling.report.presentation.core.renderable import Renderable
from ydata_profiling.report.presentation.frequency_table_utils import freq_table
from ydata_profiling.report.structure.variables.render_common import render_common
from ydata_profiling.visualisation.plot import cat_frequency_plot


def render_boolean(config: Settings, summary: VarDescription) -> dict:
    varid = summary["varid"]
    n_obs_bool = config.vars.bool.n_obs
    image_format = config.plot.image_format

    # Prepare variables
    template_variables = render_common(config, summary)

    # Element composition
    info = VariableInfo(
        anchor_id=summary["varid"],
        alerts=summary["alerts"],
        var_type="Boolean",
        var_name=summary["varname"],
        description=summary["description"],
        style=config.html.style,
    )

    table = Table(
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
                "name": "Memory size",
                "value": fmt_bytesize(summary.memory_size),
                "alert": False,
            },
        ],
        style=config.html.style,
    )

    fqm = FrequencyTableSmall(
        freq_table(
            freqtable=summary.value_counts_without_nan,
            n=summary.n,
            max_number_to_print=n_obs_bool,
        ),
        redact=False,
    )

    template_variables["top"] = Container([info, table, fqm], sequence_type="grid")

    items: List[Renderable] = [
        FrequencyTable(
            template_variables["freq_table_rows"],
            name="Common Values (Table)",
            anchor_id=f"{varid}frequency_table",
            redact=False,
        )
    ]

    show = config.plot.cat_freq.show
    max_unique = config.plot.cat_freq.max_unique

    if show and (max_unique > 0):
        if isinstance(summary.value_counts_without_nan, list):
            items.append(
                Container(
                    [
                        Image(
                            cat_frequency_plot(
                                config,
                                s,
                            ),
                            image_format=image_format,
                            alt=config.html.style._labels[idx],
                            name=config.html.style._labels[idx],
                            anchor_id=f"{varid}cat_frequency_plot_{idx}",
                        )
                        for idx, s in enumerate(summary.value_counts_without_nan)
                    ],
                    anchor_id=f"{varid}cat_frequency_plot",
                    name="Common Values (Plot)",
                    sequence_type="batch_grid",
                    batch_size=len(config.html.style._labels),
                )
            )
        else:
            items.append(
                Image(
                    cat_frequency_plot(config, summary.value_counts_without_nan),
                    image_format=image_format,
                    alt="Common Values (Plot)",
                    name="Common Values (Plot)",
                    anchor_id=f"{varid}cat_frequency_plot",
                )
            )

    template_variables["bottom"] = Container(
        items, sequence_type="tabs", anchor_id=f"{varid}bottom"
    )

    return template_variables
