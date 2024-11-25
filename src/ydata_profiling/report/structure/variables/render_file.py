from typing import List

from ydata_profiling.config import Settings
from ydata_profiling.model.var_description.default import VarDescription
from ydata_profiling.report.presentation.core import Container, FrequencyTable, Image
from ydata_profiling.report.presentation.core.renderable import Renderable
from ydata_profiling.report.presentation.frequency_table_utils import freq_table
from ydata_profiling.report.structure.variables.render_path import render_path
from ydata_profiling.visualisation.plot import histogram


def render_file(config: Settings, summary: VarDescription) -> dict:
    varid = summary["varid"]

    template_variables = render_path(config, summary)

    # Top
    template_variables["top"].content["items"][0].content["var_type"] = "File"

    n_freq_table_max = config.n_freq_table_max
    image_format = config.plot.image_format

    file_tabs: List[Renderable] = []
    if "file_size" in summary:
        file_tabs.append(
            Image(
                histogram(config, *summary["histogram_file_size"]),
                image_format=image_format,
                alt="Size",
                caption=f"<strong>Histogram with fixed size bins of file sizes (in bytes)</strong> (bins={len(summary['histogram_file_size'][1]) - 1})",
                name="File size",
                anchor_id=f"{varid}file_size_histogram",
            )
        )

    file_dates = {
        "file_created_time": "Created",
        "file_accessed_time": "Accessed",
        "file_modified_time": "Modified",
    }

    for file_date_id, description in file_dates.items():
        if file_date_id in summary:
            file_tabs.append(
                FrequencyTable(
                    freq_table(
                        freqtable=summary[file_date_id].value_counts(),
                        n=summary.n,
                        max_number_to_print=n_freq_table_max,
                    ),
                    name=description,
                    anchor_id=f"{varid}{file_date_id}",
                    redact=False,
                )
            )

    file_tab = Container(
        file_tabs,
        name="File",
        sequence_type="tabs",
        anchor_id=f"{varid}file",
    )

    template_variables["bottom"].content["items"].append(file_tab)

    return template_variables
