from ydata_profiling.config import Settings
from ydata_profiling.model.var_description.default import VarDescription
from ydata_profiling.report.formatters import fmt, fmt_numeric
from ydata_profiling.report.presentation.core import Container, FrequencyTable, Table
from ydata_profiling.report.presentation.frequency_table_utils import freq_table
from ydata_profiling.report.structure.variables.render_categorical import (
    render_categorical,
)


def render_path(config: Settings, summary: VarDescription) -> dict:
    varid = summary["varid"]
    n_freq_table_max = config.n_freq_table_max
    redact = config.vars.cat.redact

    template_variables = render_categorical(config, summary)

    keys = ["name", "parent", "suffix", "stem", "anchor"]
    for path_part in keys:
        template_variables[f"freqtable_{path_part}"] = freq_table(
            freqtable=summary[f"{path_part}_counts"],
            n=summary.n,
            max_number_to_print=n_freq_table_max,
        )

    # Top
    template_variables["top"].content["items"][0].content["var_type"] = "Path"

    # Bottom
    path_overview_tab = Container(
        [
            Table(
                [
                    {
                        "name": "Common prefix",
                        "value": fmt(summary["common_prefix"]),
                        "alert": False,
                    },
                    {
                        "name": "Unique stems",
                        "value": fmt_numeric(
                            summary["n_stem_unique"], precision=config.report.precision
                        ),
                        "alert": False,
                    },
                    {
                        "name": "Unique names",
                        "value": fmt_numeric(
                            summary["n_name_unique"], precision=config.report.precision
                        ),
                        "alert": False,
                    },
                    {
                        "name": "Unique extensions",
                        "value": fmt_numeric(
                            summary["n_suffix_unique"],
                            precision=config.report.precision,
                        ),
                        "alert": False,
                    },
                    {
                        "name": "Unique directories",
                        "value": fmt_numeric(
                            summary["n_parent_unique"],
                            precision=config.report.precision,
                        ),
                        "alert": False,
                    },
                    {
                        "name": "Unique anchors",
                        "value": fmt_numeric(
                            summary["n_anchor_unique"],
                            precision=config.report.precision,
                        ),
                        "alert": False,
                    },
                ],
                style=config.html.style,
            )
        ],
        anchor_id=f"{varid}tbl",
        name="Overview",
        sequence_type="list",
    )

    path_items = [
        path_overview_tab,
        FrequencyTable(
            template_variables["freq_table_rows"],
            name="Full",
            anchor_id=f"{varid}full_frequency",
            redact=redact,
        ),
        FrequencyTable(
            template_variables["freqtable_stem"],
            name="Stem",
            anchor_id=f"{varid}stem_frequency",
            redact=redact,
        ),
        FrequencyTable(
            template_variables["freqtable_name"],
            name="Name",
            anchor_id=f"{varid}name_frequency",
            redact=redact,
        ),
        FrequencyTable(
            template_variables["freqtable_suffix"],
            name="Extension",
            anchor_id=f"{varid}suffix_frequency",
            redact=redact,
        ),
        FrequencyTable(
            template_variables["freqtable_parent"],
            name="Parent",
            anchor_id=f"{varid}parent_frequency",
            redact=redact,
        ),
        FrequencyTable(
            template_variables["freqtable_anchor"],
            name="Anchor",
            anchor_id=f"{varid}anchor_frequency",
            redact=redact,
        ),
    ]

    path_tab = Container(
        path_items,
        name="Path",
        sequence_type="tabs",
        anchor_id=f"{varid}path",
    )

    template_variables["bottom"].content["items"].append(path_tab)

    return template_variables
