from ydata_profiling.config import Settings
from ydata_profiling.model.var_description.default import VarDescription
from ydata_profiling.report.formatters import fmt, fmt_bytesize, fmt_percent
from ydata_profiling.report.presentation.core import (
    Container,
    FrequencyTable,
    FrequencyTableSmall,
    Table,
    VariableInfo,
)
from ydata_profiling.report.presentation.frequency_table_utils import freq_table
from ydata_profiling.report.structure.variables.render_common import render_common


def render_url(config: Settings, summary: VarDescription) -> dict:
    varid = summary["varid"]
    n_freq_table_max = config.n_freq_table_max

    n_obs_cat = config.vars.cat.n_obs
    redact = config.vars.cat.redact

    template_variables = render_common(config, summary)

    keys = ["scheme", "netloc", "path", "query", "fragment"]
    for url_part in keys:
        template_variables[f"freqtable_{url_part}"] = freq_table(
            freqtable=summary[f"{url_part}_counts"],
            n=summary.n,
            max_number_to_print=n_freq_table_max,
        )

    full_frequency_table = FrequencyTable(
        template_variables["freq_table_rows"],
        name="Full",
        anchor_id=f"{varid}full_frequency",
        redact=redact,
    )
    scheme_frequency_table = FrequencyTable(
        template_variables["freqtable_scheme"],
        name="Scheme",
        anchor_id=f"{varid}scheme_frequency",
        redact=redact,
    )
    netloc_frequency_table = FrequencyTable(
        template_variables["freqtable_netloc"],
        name="Netloc",
        anchor_id=f"{varid}netloc_frequency",
        redact=redact,
    )
    path_frequency_table = FrequencyTable(
        template_variables["freqtable_path"],
        name="Path",
        anchor_id=f"{varid}path_frequency",
        redact=redact,
    )
    query_frequency_table = FrequencyTable(
        template_variables["freqtable_query"],
        name="Query",
        anchor_id=f"{varid}query_frequency",
        redact=redact,
    )
    fragment_frequency_table = FrequencyTable(
        template_variables["freqtable_fragment"],
        name="Fragment",
        anchor_id=f"{varid}fragment_frequency",
        redact=redact,
    )

    items = [
        full_frequency_table,
        scheme_frequency_table,
        netloc_frequency_table,
        path_frequency_table,
        query_frequency_table,
        fragment_frequency_table,
    ]
    template_variables["bottom"] = Container(
        items, sequence_type="tabs", name="url stats", anchor_id=f"{varid}urlstats"
    )

    # Element composition
    info = VariableInfo(
        summary["varid"],
        summary["varname"],
        "URL",
        summary["alerts"],
        summary["description"],
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
            max_number_to_print=n_obs_cat,
        ),
        redact=redact,
    )

    template_variables["top"] = Container([info, table, fqm], sequence_type="grid")

    return template_variables
