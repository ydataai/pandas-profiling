"""Plot functions for the profiling report."""
import copy
from typing import Any, Callable, List, Optional, Tuple, Union

import matplotlib
import numpy as np
import pandas as pd
import seaborn as sns
import seaborn.objects as so
from matplotlib import pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.colors import Colormap, LinearSegmentedColormap, ListedColormap, rgb2hex
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter
from pandas_profiling.config import Settings
from pandas_profiling.model.description_plot import (
    CategoricPlotDescription,
    TextPlotDescription,
)
from pandas_profiling.utils.common import convert_timestamp_to_datetime
from pandas_profiling.visualisation.context import manage_matplotlib_context
from pandas_profiling.visualisation.utils import plot_360_n0sc0pe
from PIL import ImageColor
from seaborn._core.plot import Plotter
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from typeguard import typechecked
from wordcloud import WordCloud

FIG_SIZE = (6, 4)
MINI_FIG_SIZE = (3, 2.25)


def format_fn(tick_val: int, tick_pos: Any) -> str:
    return convert_timestamp_to_datetime(tick_val).strftime("%Y-%m-%d %H:%M:%S")


"""
because both visualizations have attribute color.

I'm able co color bars, or the text, but not both at once.
"""


def supervised_plot(func):
    def inner(config: Settings, desc_plot: CategoricPlotDescription, mini: bool):
        if not desc_plot.is_supervised():
            raise ValueError(
                "Plot description is not supervised. '{}'".format(
                    desc_plot.data_col_name
                )
            )
        return func(config, desc_plot, mini)

    return inner


@supervised_plot
def _plot_cat_log_odds_ratio(
    config: Settings, desc_plot: CategoricPlotDescription, mini: bool
) -> Plotter:
    """Create log odds ratio plot for categorical column.

    Args:
        config (Setting): Config of report. Used for colors.
        desc_plot (CategoricPlotDescription):
            Plot description, with prepared log2 odds ratio DataFrame.
        mini (bool): Index, if plot is normal size, or mini.

    Returns:
        Plotter: Generated plot.
    """
    _text_position = {"left": "left", "right": "right"}
    color = config.html.style.primary_colors[2]
    p = (
        so.Plot(
            desc_plot.log_odds,
            x=desc_plot.log_odds_col_name,
            y=desc_plot.data_col_name,
        )
        .add(so.Bar(alpha=1, color=color))
        .add(
            so.Text(
                {"fontweight": "bold", "clip_on": False}, color="black", halign="left"
            ),
            text=desc_plot.log_odds_col_name,
        )
        .scale(x=so.Continuous().tick(count=0))
        .theme({"axes.facecolor": "w"})
    )
    if mini:
        p = p.layout(size=MINI_FIG_SIZE).label(title="", x="", y="")
    else:
        p = p.layout(size=FIG_SIZE).label(title="Log2 odds ratio", x="", y="")

    return p.plot(pyplot=True)


def _plot_cat_dist_supervised(
    config: Settings, desc_plot: CategoricPlotDescription, mini: bool
) -> Plotter:
    """Create distribution categorical plot for supervised report.

    Args:
        config (Setting): Config of report. Used for colors.
        desc_plot (CategoricPlotDescription):
            Plot description, with prepared distribution DataFrame.
        mini (bool): Index, if plot is normal size, or mini.

    Returns:
        Plotter: Generated plot.
    """
    if not desc_plot.target_description:
        raise ValueError(
            "Target description not found in '{}'".format(desc_plot.data_col_name)
        )

    color_positive = config.html.style.primary_colors[1]
    color_negative = config.html.style.primary_color

    p = so.Plot(
        desc_plot.distribution,
        x=desc_plot.count_col_name,
        y=desc_plot.data_col_name,
        color=desc_plot.target_col_name,
    )
    # supervised plot
    if desc_plot.is_supervised():
        p = (
            p.add(so.Bar(alpha=1), so.Dodge(), legend=False)
            .add(
                so.Text({"fontweight": "bold", "clip_on": False}, halign="left"),
                so.Dodge(by=["color"]),
                text=desc_plot.count_col_name,
            )
            .scale(
                color={
                    desc_plot.p_target_value: color_positive,
                    desc_plot.n_target_value: color_negative,
                },
            )
        )
    # target plot (same plot without dodge and with different color mapping)
    else:
        colors = {}
        for value in desc_plot.target_description.positive_values:
            colors[value] = color_positive
        for value in desc_plot.target_description.negative_values:
            colors[value] = color_negative

        p = (
            p.add(so.Bar(alpha=1), legend=False)
            .add(
                so.Text({"fontweight": "bold", "clip_on": False}, halign="left"),
                text=desc_plot.count_col_name,
            )
            .scale(color=colors)
        )

    p = p.scale(
        x=so.Continuous().tick(count=0),
    ).theme({"axes.facecolor": "w"})

    if mini:
        p = p.layout(size=MINI_FIG_SIZE).label(title="", x="", y="")
    else:
        p = p.layout(size=FIG_SIZE).label(title="Distribution", x="", y="")

    return p.plot(pyplot=True)


def _plot_cat_dist_unsupervised(
    config: Settings, desc_plot: CategoricPlotDescription, mini: bool
) -> Plotter:
    """Create distribution categorical plot for unsupervised report.

    Args:
        config (Setting): Config of report. Used for colors.
        desc_plot (CategoricPlotDescription):
            Plot description, with prepared distribution DataFrame.
        mini (bool): Index, if plot is normal size, or mini.

    Returns:
        Plotter: Generated plot.
    """
    p = (
        so.Plot(
            desc_plot.distribution,
            x=desc_plot.count_col_name,
            y=desc_plot.data_col_name,
        )
        .add(so.Bar(alpha=1, color=config.html.style.primary_color), legend=False)
        .add(
            so.Text({"fontweight": "bold", "clip_on": False}, halign="left"),
            text=desc_plot.count_col_name,
        )
    )

    p = p.scale(
        x=so.Continuous().tick(count=0),
    ).theme({"axes.facecolor": "w"})

    if mini:
        p = p.layout(size=MINI_FIG_SIZE).label(title="", x="", y="")
    else:
        p = p.layout(size=FIG_SIZE).label(title="Distribution", x="", y="")

    return p.plot(pyplot=True)


@supervised_plot
def _plot_hist_log_odds_ratio(
    config: Settings, desc_plot: CategoricPlotDescription, mini: bool
) -> Plotter:
    """Create log2 odds ratio graph for numeric variable.

    Args:
        config (Setting): Config of report. Used for colors.
        desc_plot (CategoricPlotDescription):
            Plot description, with prepared log2 odds ratio DataFrame.
        mini (bool): Index, if plot is normal size, or mini.

    Returns:
        Plotter: Generated plot.
    """
    color = config.html.style.primary_colors[2]

    p = (
        so.Plot(
            desc_plot.log_odds,
            x=desc_plot.data_col_name,
            y=desc_plot.log_odds_col_name,
        )
        .add(so.Bar(alpha=1, color=color))
        .add(
            so.Text(
                {"fontweight": "bold", "clip_on": False},
                valign="bottom",
                color="black",
            ),
            text="log_odds",
        )
    )
    p = p.scale(y=so.Continuous().tick(count=0)).theme({"axes.facecolor": "w"})

    if mini:
        p = p.layout(size=MINI_FIG_SIZE).label(title="", x="", y="")
    else:
        p = p.layout(size=FIG_SIZE).label(title="Log2 odds ratio", x="", y="")

    return p.plot(pyplot=True)


def _plot_hist_dist(
    config: Settings, desc_plot: CategoricPlotDescription, mini: bool
) -> Plotter:
    """Plot distribution of numeric variable.

    Args:
        config (Setting): Config of report. Used for colors.
        desc_plot (CategoricPlotDescription):
            Plot description, with prepared distribution DataFrame.
        mini (bool): Index, if plot is normal size, or mini.

    Returns:
        Plotter: Generated plot.
    """
    color_positive = config.html.style.primary_colors[1]
    color_negative = config.html.style.primary_color
    p = so.Plot(
        desc_plot.distribution,
        x=desc_plot.data_col_name,
        y=desc_plot.count_col_name,
        color=desc_plot.target_col_name,
    )
    # supervised
    if desc_plot.is_supervised():
        p = (
            p.add(so.Bar(alpha=1), so.Dodge(), legend=False)
            .add(
                so.Text(
                    {"fontweight": "bold", "clip_on": False, "rotation": 45},
                    valign="bottom",
                    halign="center",
                ),
                so.Dodge(by=["color"]),
                text=desc_plot.count_col_name,
            )
            .scale(
                color={
                    desc_plot.p_target_value: color_positive,
                    desc_plot.n_target_value: color_negative,
                },
            )
        )

    # unsupervised
    else:
        p = p.add(so.Bars(alpha=1, color=config.html.style.primary_color))
        p = p.scale(x=so.Continuous().tick())

    p = p.scale(
        y=so.Continuous().tick(count=0),
    ).theme({"axes.facecolor": "w"})

    if mini:
        p = p.layout(size=MINI_FIG_SIZE).label(title="", x="", y="")
    else:
        p = p.layout(size=FIG_SIZE).label(title="Distribution", x="", y="")

    return p.plot(pyplot=True)


def _plot_word_cloud(
    config: Settings, plot_description: TextPlotDescription, mini: bool
) -> plt.Figure:
    """Plot word cloud for string variable.

    Args:
        config (Setting): Config of report. Used for colors.
        desc_plot (CategoricPlotDescription):
            Plot description, with prepared words DataFrame.
        mini (bool): Index, if plot is normal size, or mini.

    Returns:
        Plotter: Generated plot.
    """
    positive_color = ImageColor.getcolor(config.html.style.primary_colors[1], "RGB")
    negative_color = ImageColor.getcolor(config.html.style.primary_color, "RGB")

    def target_color_func(
        word, font_size, position, orientation, random_state=None, **kwargs
    ):
        """Generate color for word. For unsupervised profile, return default color.
        For supervised profile, return weighted color from positive and negative count.
        """
        # color for unsupervised plot
        if not plot_description.target_description:
            return config.html.style.primary_color
        positive_count = int(
            plot_description.words_counts.loc[word, plot_description.positive_col_name]
        )
        negative_count = int(
            plot_description.words_counts.loc[word, plot_description.negative_col_name]
        )
        _pos = np.multiply(positive_count, positive_color)
        _neg = np.multiply(negative_count, negative_color)
        return tuple((_pos + _neg) // (positive_count + negative_count))

    word_dict = plot_description.words_counts[plot_description.count_col_name].to_dict()
    wordcloud = WordCloud(
        background_color="white", random_state=123, max_words=100
    ).generate_from_frequencies(word_dict)
    wordcloud.recolor(color_func=target_color_func)

    if mini:
        plt.figure(figsize=MINI_FIG_SIZE)
    else:
        plt.figure(figsize=FIG_SIZE)

    plot = plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    return plot


def _plot_histogram(
    config: Settings,
    series: np.ndarray,
    bins: Union[int, np.ndarray],
    figsize: tuple = (6, 4),
    date: bool = False,
    hide_yaxis: bool = False,
) -> plt.Figure:
    """Plot a histogram from the data and return the AxesSubplot object.

    Args:
        config: the Settings object
        series: The data to plot
        bins: number of bins (int for equal size, ndarray for variable size)
        figsize: The size of the figure (width, height) in inches, default (6,4)
        date: is the x-axis of date type

    Returns:
        The histogram plot.
    """
    # we have precomputed the histograms...
    if isinstance(bins, list):
        n_labels = len(config.html.style._labels)
        fig, ax = plt.subplots(
            nrows=n_labels, ncols=1, sharex=True, sharey=True, figsize=(6, 6)
        )

        for idx in range(n_labels):
            plot = ax[idx]

            diff = np.diff(bins[idx])
            plot.bar(
                bins[idx][:-1] + diff / 2,  # type: ignore
                series[idx],
                diff,
                facecolor=config.html.style.primary_colors[idx],
            )

            if date:
                plot.xaxis.set_major_formatter(FuncFormatter(format_fn))

            if not config.plot.histogram.x_axis_labels:
                plot.set_xticklabels([])

            if hide_yaxis:
                plot.yaxis.set_visible(False)

        if not config.plot.histogram.x_axis_labels:
            fig.xticklabels([])

        if not hide_yaxis:
            fig.supylabel("Frequency")
    else:
        fig = plt.figure(figsize=figsize)
        plot = fig.add_subplot(111)
        if not hide_yaxis:
            plot.set_ylabel("Frequency")
        else:
            plot.axes.get_yaxis().set_visible(False)

        diff = np.diff(bins)
        plot.bar(
            bins[:-1] + diff / 2,  # type: ignore
            series,
            diff,
            facecolor=config.html.style.primary_colors[0],
        )

        if date:
            plot.xaxis.set_major_formatter(FuncFormatter(format_fn))

        if not config.plot.histogram.x_axis_labels:
            plot.set_xticklabels([])

    return plot


@manage_matplotlib_context()
def plot_cat_dist(
    config: Settings, plot_description: CategoricPlotDescription, mini: bool = False
) -> str:
    """Plot categorical distribution."""
    if plot_description.target_description:
        plot = _plot_cat_dist_supervised(config, plot_description, mini)
    else:
        plot = _plot_cat_dist_unsupervised(config, plot_description, mini)
    return plot_360_n0sc0pe(config)


@manage_matplotlib_context()
def plot_cat_log_odds(
    config: Settings, plot_description: CategoricPlotDescription, mini: bool = False
) -> str:
    """Plot categorical log odds graph."""
    plot = _plot_cat_log_odds_ratio(config, plot_description, mini)
    return plot_360_n0sc0pe(config)


@manage_matplotlib_context()
def plot_hist_dist(
    config: Settings, plot_description: CategoricPlotDescription, mini: bool = False
) -> str:
    """Plot histogram for continuos data."""
    if plot_description.target_description:
        plot = _plot_cat_dist_supervised(config, plot_description, mini)
    else:
        plot = _plot_hist_dist(config, plot_description, mini)
    return plot_360_n0sc0pe(config)


@manage_matplotlib_context()
def plot_hist_log_odds(
    config: Settings, plot_description: CategoricPlotDescription, mini: bool = False
) -> str:
    """Plot continuous log odds graph."""
    if plot_description.is_supervised():
        plot = _plot_cat_log_odds_ratio(config, plot_description, mini)
    else:
        plot = _plot_hist_log_odds_ratio(config, plot_description, mini)
    return plot_360_n0sc0pe(config)


@manage_matplotlib_context()
def plot_word_cloud(
    config: Settings, plot_description: TextPlotDescription, mini: bool = False
) -> str:
    """Plot word cloud for text column."""
    plot = _plot_word_cloud(config, plot_description, mini)
    return plot_360_n0sc0pe(config)


@manage_matplotlib_context()
def histogram(
    config: Settings,
    series: np.ndarray,
    bins: Union[int, np.ndarray],
    date: bool = False,
) -> str:
    """Plot an histogram of the data.

    Args:
        config: Settings
        series: The data to plot.
        bins: number of bins (int for equal size, ndarray for variable size)
        date: is histogram of date(time)?

    Returns:
      The resulting histogram encoded as a string.

    """
    plot = _plot_histogram(config, series, bins, date=date)
    plot.xaxis.set_tick_params(rotation=90 if date else 45)
    plot.figure.tight_layout()
    return plot_360_n0sc0pe(config)


@manage_matplotlib_context()
def mini_histogram(
    config: Settings,
    series: np.ndarray,
    bins: Union[int, np.ndarray],
    date: bool = False,
) -> str:
    """Plot a small (mini) histogram of the data.

    Args:
      config: Settings
      series: The data to plot.
      bins: number of bins (int for equal size, ndarray for variable size)

    Returns:
      The resulting mini histogram encoded as a string.
    """
    plot = _plot_histogram(
        config, series, bins, figsize=(3, 2.25), date=date, hide_yaxis=True
    )
    plot.set_facecolor("w")

    for tick in plot.xaxis.get_major_ticks():
        tick.label1.set_fontsize(6 if date else 8)
    plot.xaxis.set_tick_params(rotation=90 if date else 45)
    plot.figure.tight_layout()

    return plot_360_n0sc0pe(config)


def get_cmap_half(
    cmap: Union[Colormap, LinearSegmentedColormap, ListedColormap]
) -> LinearSegmentedColormap:
    """Get the upper half of the color map

    Args:
        cmap: the color map

    Returns:
        A new color map based on the upper half of another color map

    References:
        https://stackoverflow.com/a/24746399/470433
    """
    # Evaluate an existing colormap from 0.5 (midpoint) to 1 (upper end)
    colors = cmap(np.linspace(0.5, 1, cmap.N // 2))

    # Create a new colormap from those colors
    return LinearSegmentedColormap.from_list("cmap_half", colors)


def get_correlation_font_size(n_labels: int) -> Optional[int]:
    """Dynamic label font sizes in correlation plots

    Args:
        n_labels: the number of labels

    Returns:
        A font size or None for the default font size
    """
    if n_labels > 100:
        font_size = 4
    elif n_labels > 80:
        font_size = 5
    elif n_labels > 50:
        font_size = 6
    elif n_labels > 40:
        font_size = 8
    else:
        return None
    return font_size


@manage_matplotlib_context()
def correlation_matrix(config: Settings, data: pd.DataFrame, vmin: int = -1) -> str:
    """Plot image of a matrix correlation.

    Args:
      config: Settings
      data: The matrix correlation to plot.
      vmin: Minimum value of value range.

    Returns:
      The resulting correlation matrix encoded as a string.
    """
    fig_cor, axes_cor = plt.subplots()

    cmap = plt.get_cmap(config.plot.correlation.cmap)
    if vmin == 0:
        cmap = get_cmap_half(cmap)
    cmap = copy.copy(cmap)
    cmap.set_bad(config.plot.correlation.bad)

    labels = data.columns
    matrix_image = axes_cor.imshow(
        data, vmin=vmin, vmax=1, interpolation="nearest", cmap=cmap
    )
    plt.colorbar(matrix_image)

    if data.isnull().values.any():
        legend_elements = [Patch(facecolor=cmap(np.nan), label="invalid\ncoefficient")]

        plt.legend(
            handles=legend_elements,
            loc="upper right",
            handleheight=2.5,
        )

    axes_cor.set_xticks(np.arange(0, data.shape[0], float(data.shape[0]) / len(labels)))
    axes_cor.set_yticks(np.arange(0, data.shape[1], float(data.shape[1]) / len(labels)))

    font_size = get_correlation_font_size(len(labels))
    axes_cor.set_xticklabels(labels, rotation=90, fontsize=font_size)
    axes_cor.set_yticklabels(labels, fontsize=font_size)
    plt.subplots_adjust(bottom=0.2)

    return plot_360_n0sc0pe(config)


@manage_matplotlib_context()
def scatter_complex(config: Settings, series: pd.Series) -> str:
    """Scatter plot (or hexbin plot) from a series of complex values

    Examples:
        >>> complex_series = pd.Series([complex(1, 3), complex(3, 1)])
        >>> scatter_complex(complex_series)

    Args:
        config: Settings
        series: the Series

    Returns:
        A string containing (a reference to) the image
    """
    plt.ylabel("Imaginary")
    plt.xlabel("Real")

    color = config.html.style.primary_colors[0]

    if len(series) > config.plot.scatter_threshold:
        cmap = sns.light_palette(color, as_cmap=True)
        plt.hexbin(series.real, series.imag, cmap=cmap)
    else:
        plt.scatter(series.real, series.imag, color=color)

    return plot_360_n0sc0pe(config)


@manage_matplotlib_context()
def scatter_series(
    config: Settings, series: pd.Series, x_label: str = "Width", y_label: str = "Height"
) -> str:
    """Scatter plot (or hexbin plot) from one series of sequences with length 2

    Examples:
        >>> scatter_series(file_sizes, "Width", "Height")

    Args:
        config: report Settings object
        series: the Series
        x_label: the label on the x-axis
        y_label: the label on the y-axis

    Returns:
        A string containing (a reference to) the image
    """
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    color = config.html.style.primary_colors[0]

    data = zip(*series.tolist())
    if len(series) > config.plot.scatter_threshold:
        cmap = sns.light_palette(color, as_cmap=True)
        plt.hexbin(*data, cmap=cmap)
    else:
        plt.scatter(*data, color=color)
    return plot_360_n0sc0pe(config)


@manage_matplotlib_context()
def scatter_pairwise(
    config: Settings, series1: pd.Series, series2: pd.Series, x_label: str, y_label: str
) -> str:
    """Scatter plot (or hexbin plot) from two series

    Examples:
        >>> widths = pd.Series([800, 1024])
        >>> heights = pd.Series([600, 768])
        >>> scatter_series(widths, heights, "Width", "Height")

    Args:
        config: Settings
        series1: the series corresponding to the x-axis
        series2: the series corresponding to the y-axis
        x_label: the label on the x-axis
        y_label: the label on the y-axis

    Returns:
        A string containing (a reference to) the image
    """
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    color = config.html.style.primary_colors[0]

    indices = (series1.notna()) & (series2.notna())
    if len(series1) > config.plot.scatter_threshold:
        cmap = sns.light_palette(color, as_cmap=True)
        plt.hexbin(series1[indices], series2[indices], gridsize=15, cmap=cmap)
    else:
        plt.scatter(series1[indices], series2[indices], color=color)
    return plot_360_n0sc0pe(config)


def _plot_stacked_barh(
    data: pd.Series,
    colors: List,
) -> Tuple[plt.Axes, matplotlib.legend.Legend]:
    """Plot a stacked horizontal bar chart to show category frequency.
    Works for boolean and categorical features.

    Args:
        data (pd.Series): category frequencies with category names as index
        colors (list): list of colors in a valid matplotlib format

    Returns:
        ax: Stacked bar plot (matplotlib.axes)
        legend: Legend handler (matplotlib)
    """
    # Use the pd.Series indices as category names
    labels = data.index.values.astype(str)

    # Plot
    _, ax = plt.subplots(figsize=(7, 2))
    ax.axis("off")

    ax.set_xlim(0, np.sum(data))
    ax.set_ylim(0.4, 1.6)

    starts = 0
    for x, label, color in zip(data, labels, colors):
        # Add a rectangle to the stacked barh chart
        rects = ax.barh(y=1, width=x, height=1, left=starts, label=label, color=color)

        # Label color depends on the darkness of the rectangle
        r, g, b, _ = rects[0].get_facecolor()
        text_color = "white" if r * g * b < 0.5 else "darkgrey"

        # If the new bar is big enough write the label
        pc_of_total = x / data.sum() * 100
        # Requires matplotlib >= 3.4.0
        if pc_of_total > 8 and hasattr(ax, "bar_label"):
            display_txt = f"{pc_of_total:.1f}%\n({x})"
            ax.bar_label(
                rects,
                labels=[display_txt],
                label_type="center",
                color=text_color,
                fontsize="x-large",
                fontweight="bold",
            )

        starts += x

    legend = ax.legend(
        ncol=1, bbox_to_anchor=(0, 0), fontsize="xx-large", loc="upper left"
    )

    return ax, legend


def _plot_pie_chart(
    data: pd.Series,
    colors: List,
) -> Tuple[plt.Axes, matplotlib.legend.Legend]:
    """Plot a pie chart to show category frequency.
    Works for boolean and categorical features.

    Args:
        data (pd.Series): category frequencies with category names as index
        colors (list): list of colors in a valid matplotlib format

    Returns:
        ax: pie chart (matplotlib.axes)
        legend: Legend handler (matplotlib)
    """

    def make_autopct(values: pd.Series) -> Callable:
        def my_autopct(pct: float) -> str:
            total = np.sum(values)
            val = int(round(pct * total / 100.0))
            return f"{pct:.1f}%  ({val:d})"

        return my_autopct

    _, ax = plt.subplots(figsize=(4, 4))
    wedges, _, _ = plt.pie(
        data,
        autopct=make_autopct(data),
        textprops={"color": "w"},
        colors=colors,
    )
    legend = plt.legend(
        wedges,
        data.index.values,
        fontsize="large",
        bbox_to_anchor=(0, 0),
        loc="upper left",
    )

    return ax, legend


@manage_matplotlib_context()
def cat_frequency_plot(
    config: Settings,
    data: pd.Series,
) -> str:
    """Generate category frequency plot to show category frequency.
    Works for boolean and categorical features.

    Modify colors by setting 'config.plot.cat_freq.colors' to a
    list of valid matplotib colors:
    https://matplotlib.org/stable/tutorials/colors/colors.html

    Args:
        config (Settings): a profile report config
        data (pd.Series): category frequencies with category names as index

    Returns:
        str: encoded category frequency plot encoded
    """
    # Get colors, if not defined, use matplotlib defaults
    colors = config.plot.cat_freq.colors
    if colors is None:
        # Get matplotlib defaults
        colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    # If there are more categories than colors, loop through the colors again
    if len(colors) < len(data):
        multiplier = int(len(data) / len(colors)) + 1
        colors = multiplier * colors  # repeat colors as required
        colors = colors[0 : len(data)]  # select the exact number of colors required

    # Create the plot
    plot_type = config.plot.cat_freq.type
    if plot_type == "bar":
        if isinstance(data, list):
            for v in data:
                plot, legend = _plot_stacked_barh(v, colors)
        else:
            plot, legend = _plot_stacked_barh(data, colors)

    elif plot_type == "pie":
        plot, legend = _plot_pie_chart(data, colors)

    else:
        msg = (
            f"'{plot_type}' is not a valid plot type! "
            "Expected values are ['bar', 'pie']"
        )
        msg
        raise ValueError(msg)

    return plot_360_n0sc0pe(
        config,
        bbox_extra_artists=[
            legend,
        ],
        bbox_inches="tight",
    )


def create_comparison_color_list(config: Settings) -> List[str]:
    colors = config.html.style.primary_colors
    labels = config.html.style._labels

    if colors < labels:
        init = colors[0]
        end = colors[1] if len(colors) >= 2 else "#000000"
        cmap = LinearSegmentedColormap.from_list("ts_leg", [init, end], len(labels))
        colors = [rgb2hex(cmap(i)) for i in range(cmap.N)]
    return colors


def _plot_timeseries(
    config: Settings,
    series: Union[list, pd.Series],
    figsize: tuple = (6, 4),
) -> matplotlib.figure.Figure:
    """Plot an line plot from the data and return the AxesSubplot object.
    Args:
        series: The data to plot
        figsize: The size of the figure (width, height) in inches, default (6,4)
    Returns:
        The TimeSeries lineplot.
    """
    fig = plt.figure(figsize=figsize)
    plot = fig.add_subplot(111)

    if isinstance(series, list):
        labels = config.html.style._labels
        colors = create_comparison_color_list(config)

        for serie, color, label in zip(series, colors, labels):
            serie.plot(color=color, label=label)

    else:
        series.plot(color=config.html.style.primary_colors[0])

    return plot


@manage_matplotlib_context()
def mini_ts_plot(config: Settings, series: Union[list, pd.Series]) -> str:
    """Plot an time-series plot of the data.
    Args:
      series: The data to plot.
    Returns:
      The resulting timeseries plot encoded as a string.
    """
    plot = _plot_timeseries(config, series, figsize=(3, 2.25))
    plot.xaxis.set_tick_params(rotation=45)
    plt.rc("ytick", labelsize=3)

    for tick in plot.xaxis.get_major_ticks():
        if isinstance(series.index, pd.DatetimeIndex):
            tick.label1.set_fontsize(6)
        else:
            tick.label1.set_fontsize(8)
    plot.figure.tight_layout()
    return plot_360_n0sc0pe(config)


def _get_ts_lag(config: Settings, series: pd.Series) -> int:
    lag = config.vars.timeseries.pacf_acf_lag
    max_lag_size = (len(series) // 2) - 1
    return np.min([lag, max_lag_size])


def _plot_acf_pacf(
    config: Settings, series: pd.Series, figsize: tuple = (15, 5)
) -> str:
    color = config.html.style.primary_colors[0]

    lag = _get_ts_lag(config, series)
    _, axes = plt.subplots(nrows=1, ncols=2, figsize=figsize)

    plot_acf(
        series.dropna(),
        lags=lag,
        ax=axes[0],
        title="ACF",
        fft=True,
        color=color,
        vlines_kwargs={"colors": color},
    )
    plot_pacf(
        series.dropna(),
        lags=lag,
        ax=axes[1],
        title="PACF",
        method="ywm",
        color=color,
        vlines_kwargs={"colors": color},
    )

    for ax in axes:
        for item in ax.collections:
            if type(item) == PolyCollection:
                item.set_facecolor(color)

    return plot_360_n0sc0pe(config)


def _plot_acf_pacf_comparison(
    config: Settings, series: List[pd.Series], figsize: tuple = (15, 5)
) -> str:
    colors = config.html.style.primary_colors
    n_labels = len(config.html.style._labels)
    colors = create_comparison_color_list(config)

    _, axes = plt.subplots(nrows=n_labels, ncols=2, figsize=figsize)
    is_first = True
    for serie, (acf_axis, pacf_axis), color in zip(series, axes, colors):
        lag = _get_ts_lag(config, serie)

        plot_acf(
            serie.dropna(),
            lags=lag,
            ax=acf_axis,
            title="ACF" if is_first else "",
            fft=True,
            color=color,
            vlines_kwargs={"colors": color},
        )
        plot_pacf(
            serie.dropna(),
            lags=lag,
            ax=pacf_axis,
            title="PACF" if is_first else "",
            method="ywm",
            color=color,
            vlines_kwargs={"colors": color},
        )
        is_first = False

    for row, color in zip(axes, colors):
        for ax in row:
            for item in ax.collections:
                if isinstance(item, PolyCollection):
                    item.set_facecolor(color)

    return plot_360_n0sc0pe(config)


@manage_matplotlib_context()
def plot_acf_pacf(
    config: Settings, series: Union[list, pd.Series], figsize: tuple = (15, 5)
) -> str:
    if isinstance(series, list):
        return _plot_acf_pacf_comparison(config, series, figsize)
    else:
        return _plot_acf_pacf(config, series, figsize)


def _prepare_heatmap_data(
    dataframe: pd.DataFrame,
    entity_column: str,
    sortby: Optional[Union[str, list]] = None,
    max_entities: int = 5,
    selected_entities: Optional[List[str]] = None,
) -> pd.DataFrame:
    if sortby is None:
        sortbykey = "_index"
        df = dataframe[entity_column].copy().reset_index()
        df.columns = [sortbykey, entity_column]

    else:
        if isinstance(sortby, str):
            sortby = [sortby]
        cols = [entity_column, *sortby]
        df = dataframe[cols].copy()
        sortbykey = sortby[0]

    if df[sortbykey].dtype == "O":
        try:
            df[sortbykey] = pd.to_datetime(df[sortbykey])
        except Exception as ex:
            raise ValueError(
                f"column {sortbykey} dtype {df[sortbykey].dtype} is not supported."
            ) from ex
    nbins = np.min([50, df[sortbykey].nunique()])

    df["__bins"] = pd.cut(
        df[sortbykey], bins=nbins, include_lowest=True, labels=range(nbins)
    )

    df = df.groupby([entity_column, "__bins"])[sortbykey].count()
    df = df.reset_index().pivot(entity_column, "__bins", sortbykey).T
    if selected_entities:
        df = df[selected_entities].T
    else:
        df = df.T[:max_entities]

    return df


def _create_timeseries_heatmap(
    df: pd.DataFrame,
    figsize: Tuple[int, int] = (12, 5),
    color: str = "#337ab7",
) -> plt.Axes:
    _, ax = plt.subplots(figsize=figsize)
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        "report", ["white", color], N=64
    )
    pc = ax.pcolormesh(df, edgecolors=ax.get_facecolor(), linewidth=0.25, cmap=cmap)
    pc.set_clim(0, np.nanmax(df))
    ax.set_yticks([x + 0.5 for x in range(len(df))])
    ax.set_yticklabels(df.index)
    ax.set_xticks([])
    ax.set_xlabel("Time")
    ax.invert_yaxis()
    return ax


@typechecked
def timeseries_heatmap(
    dataframe: pd.DataFrame,
    entity_column: str,
    sortby: Optional[Union[str, list]] = None,
    max_entities: int = 5,
    selected_entities: Optional[List[str]] = None,
    figsize: Tuple[int, int] = (12, 5),
    color: str = "#337ab7",
) -> plt.Axes:
    """Generate a multi entity timeseries heatmap based on a pandas DataFrame.

    Args:
        dataframe: the pandas DataFrame
        entity_column: name of the entities column
        sortby: column that define the timesteps (only dates and numerical variables are supported)
        max_entities: max entities that will be displayed
        selected_entities: Optional list of entities to be displayed (overules max_entities)
        figsize: The size of the figure (width, height) in inches, default (10,5)
        color: the primary color, default '#337ab7'
    Returns:
        The TimeSeries heatmap.
    """
    df = _prepare_heatmap_data(
        dataframe, entity_column, sortby, max_entities, selected_entities
    )
    ax = _create_timeseries_heatmap(df, figsize, color)
    ax.set_aspect(1)
    return ax


def _set_visibility(
    axis: matplotlib.axis.Axis, tick_mark: str = "none"
) -> matplotlib.axis.Axis:
    for anchor in ["top", "right", "bottom", "left"]:
        axis.spines[anchor].set_visible(False)
    axis.xaxis.set_ticks_position(tick_mark)
    axis.yaxis.set_ticks_position(tick_mark)
    return axis


def missing_bar(
    data: pd.DataFrame,
    figsize: Tuple[float, float] = (25, 10),
    fontsize: float = 16,
    labels: bool = True,
    color: Tuple[float, ...] = (0.41, 0.41, 0.41),
    label_rotation: int = 45,
) -> matplotlib.axis.Axis:
    """
    A bar chart visualization of the missing data.

    Inspired by https://github.com/ResidentMario/missingno

    Args:
        data: The input DataFrame.
        figsize: The size of the figure to display.
        fontsize: The figure's font size. This default to 16.
        labels: Whether or not to display the column names. Would need to be turned off on particularly large
            displays. Defaults to True.
        color: The color of the filled columns. Default to the RGB multiple `(0.25, 0.25, 0.25)`.
        label_rotation: What angle to rotate the text labels to. Defaults to 45 degrees.
    Returns:
        The plot axis.
    """
    null_counts = len(data) - data.isnull().sum()
    values = null_counts.values
    null_counts = null_counts / len(data)

    if len(values) <= 50:
        ax0 = null_counts.plot.bar(figsize=figsize, fontsize=fontsize, color=color)
        ax0.set_xticklabels(
            ax0.get_xticklabels(),
            ha="right",
            fontsize=fontsize,
            rotation=label_rotation,
        )

        ax1 = ax0.twiny()
        ax1.set_xticks(ax0.get_xticks())
        ax1.set_xlim(ax0.get_xlim())
        ax1.set_xticklabels(
            values, ha="left", fontsize=fontsize, rotation=label_rotation
        )
    else:
        ax0 = null_counts.plot.barh(figsize=figsize, fontsize=fontsize, color=color)
        ylabels = ax0.get_yticklabels() if labels else []
        ax0.set_yticklabels(ylabels, fontsize=fontsize)

        ax1 = ax0.twinx()
        ax1.set_yticks(ax0.get_yticks())
        ax1.set_ylim(ax0.get_ylim())
        ax1.set_yticklabels(values, fontsize=fontsize)

    for ax in [ax0, ax1]:
        ax = _set_visibility(ax)

    return ax0


def missing_matrix(
    data: pd.DataFrame,
    figsize: Tuple[float, float] = (25, 10),
    color: Tuple[float, ...] = (0.41, 0.41, 0.41),
    fontsize: float = 16,
    labels: bool = True,
    label_rotation: int = 45,
) -> matplotlib.axis.Axis:
    """
    A matrix visualization of missing data.

    Inspired by https://github.com/ResidentMario/missingno

    Args:
        data: The input DataFrame.
        figsize: The size of the figure to display.
        fontsize: The figure's font size. Default to 16.
        labels: Whether or not to display the column names when there is more than 50 columns.
        label_rotation: What angle to rotate the text labels to. Defaults to 45 degrees.
        color: The color of the filled columns. Default is `(0.41, 0.41, 0.41)`.
    Returns:
        The plot axis.
    """
    height, width = data.shape

    notnull = data.notnull().values
    missing_grid = np.zeros((height, width, 3), dtype=np.float32)

    missing_grid[notnull] = color
    missing_grid[~notnull] = [1, 1, 1]

    _, ax = plt.subplots(1, 1, figsize=figsize)

    # Create the missing matrix plot.
    ax.imshow(missing_grid, interpolation="none")
    ax.set_aspect("auto")
    ax.grid(False)
    ax.xaxis.tick_top()

    ha = "left"
    ax.set_xticks(list(range(0, width)))
    ax.set_xticklabels(
        list(data.columns), rotation=label_rotation, ha=ha, fontsize=fontsize
    )
    ax.set_yticks([0, height - 1])
    ax.set_yticklabels([1, height], fontsize=fontsize)

    separators = [x + 0.5 for x in range(0, width - 1)]
    for point in separators:
        ax.axvline(point, linestyle="-", color="white")

    if not labels and width > 50:
        ax.set_xticklabels([])

    ax = _set_visibility(ax)
    return ax


def missing_heatmap(
    data: pd.DataFrame,
    figsize: Tuple[float, float] = (20, 12),
    fontsize: float = 16,
    labels: bool = True,
    label_rotation: int = 45,
    cmap: str = "RdBu",
    normalized_cmap: bool = True,
    cbar: bool = True,
    ax: matplotlib.axis.Axis = None,
) -> matplotlib.axis.Axis:
    """
    Presents a `seaborn` heatmap visualization of missing data correlation.
    Note that this visualization has no special support for large datasets.

    Inspired by https://github.com/ResidentMario/missingno

    Args:
        data: The input DataFrame.
        figsize: The size of the figure to display. Defaults to (20, 12).
        fontsize: The figure's font size.
        labels: Whether or not to label each matrix entry with its correlation (default is True).
        label_rotation: What angle to rotate the text labels to. Defaults to 45 degrees.
        cmap: Which colormap to use. Defaults to `RdBu`.
        normalized_cmap: Use a normalized colormap threshold or not. Defaults to True
    Returns:
        The plot axis.
    """
    _, ax = plt.subplots(1, 1, figsize=figsize)

    # Remove completely filled or completely empty variables.
    columns = [i for i, n in enumerate(np.var(data.isnull(), axis="rows")) if n > 0]
    data = data.iloc[:, columns]

    # Create and mask the correlation matrix. Construct the base heatmap.
    corr_mat = data.isnull().corr()
    mask = np.zeros_like(corr_mat)
    mask[np.triu_indices_from(mask)] = True
    norm_args = {"vmin": -1, "vmax": 1} if normalized_cmap else {}

    if labels:
        sns.heatmap(
            corr_mat,
            mask=mask,
            cmap=cmap,
            ax=ax,
            cbar=cbar,
            annot=True,
            annot_kws={"size": fontsize - 2},
            **norm_args,
        )
    else:
        sns.heatmap(corr_mat, mask=mask, cmap=cmap, ax=ax, cbar=cbar, **norm_args)

    # Apply visual corrections and modifications.
    ax.xaxis.tick_bottom()
    ax.set_xticklabels(
        ax.xaxis.get_majorticklabels(),
        rotation=label_rotation,
        ha="right",
        fontsize=fontsize,
    )
    ax.set_yticklabels(ax.yaxis.get_majorticklabels(), rotation=0, fontsize=fontsize)
    ax = _set_visibility(ax)
    ax.patch.set_visible(False)

    for text in ax.texts:
        t = float(text.get_text())
        if 0.95 <= t < 1:
            text.set_text("<1")
        elif -1 < t <= -0.95:
            text.set_text(">-1")
        elif t == 1:
            text.set_text("1")
        elif t == -1:
            text.set_text("-1")
        elif -0.05 < t < 0.05:
            text.set_text("")
        else:
            text.set_text(round(t, 1))

    return ax
