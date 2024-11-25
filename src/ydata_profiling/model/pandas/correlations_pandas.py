"""Correlations between variables."""

import itertools
import warnings
from typing import Callable, Dict, Optional

import numpy as np
import pandas as pd
from scipy import stats

from ydata_profiling.config import Settings
from ydata_profiling.model.correlations import (
    Auto,
    Cramers,
    Kendall,
    Pearson,
    PhiK,
    Spearman,
)
from ydata_profiling.model.pandas.discretize_pandas import (
    DiscretizationType,
    Discretizer,
)
from ydata_profiling.model.var_description.default import VarDescription


@Spearman.compute.register(Settings, pd.DataFrame, dict)
def pandas_spearman_compute(
    config: Settings, df: pd.DataFrame, summary: dict
) -> Optional[pd.DataFrame]:
    df_aux = df.select_dtypes(include="number").copy()
    return df_aux.corr(method="spearman")


@Pearson.compute.register(Settings, pd.DataFrame, dict)
def pandas_pearson_compute(
    config: Settings, df: pd.DataFrame, summary: dict
) -> Optional[pd.DataFrame]:
    df_aux = df.select_dtypes(include="number").copy()
    return df_aux.corr(method="pearson")


@Kendall.compute.register(Settings, pd.DataFrame, dict)
def pandas_kendall_compute(
    config: Settings, df: pd.DataFrame, summary: dict
) -> Optional[pd.DataFrame]:
    df_aux = df.select_dtypes(include="number").copy()
    return df_aux.corr(method="kendall")


def _cramers_corrected_stat(confusion_matrix: pd.DataFrame, correction: bool) -> float:
    """Calculate the Cramer's V corrected stat for two variables.

    Args:
        confusion_matrix: Crosstab between two variables.
        correction: Should the correction be applied?

    Returns:
        The Cramer's V corrected stat for the two variables.
    """
    # handles empty crosstab
    if confusion_matrix.empty:
        return 0

    chi2 = stats.chi2_contingency(confusion_matrix, correction=correction)[0]
    n = confusion_matrix.sum().sum()
    phi2 = chi2 / n
    r = confusion_matrix.shape[0]
    k = confusion_matrix.shape[1] if len(confusion_matrix.shape) > 1 else 1

    # Deal with NaNs later on
    with np.errstate(divide="ignore", invalid="ignore"):
        phi2corr = max(0.0, phi2 - ((k - 1.0) * (r - 1.0)) / (n - 1.0))
        rcorr = r - ((r - 1.0) ** 2.0) / (n - 1.0)
        kcorr = k - ((k - 1.0) ** 2.0) / (n - 1.0)
        rkcorr = min((kcorr - 1.0), (rcorr - 1.0))
        if rkcorr == 0.0:
            corr = 1.0
        else:
            corr = np.sqrt(phi2corr / rkcorr)
    return corr


def _pairwise_spearman(col_1: pd.Series, col_2: pd.Series) -> float:
    return col_1.corr(col_2, method="spearman")


def _pairwise_cramers(col_1: pd.Series, col_2: pd.Series) -> float:
    return _cramers_corrected_stat(pd.crosstab(col_1, col_2), correction=True)


@Cramers.compute.register(Settings, pd.DataFrame, Dict[str, VarDescription])
def pandas_cramers_compute(
    config: Settings, df: pd.DataFrame, summary: Dict[str, VarDescription]
) -> Optional[pd.DataFrame]:
    threshold = config.categorical_maximum_correlation_distinct

    # `index` and `columns` must not be a set since Pandas 1.5,
    # so convert it to a list. The order of the list is arbitrary.
    categoricals = list(
        {
            key
            for key, value in summary.items()
            if value["type"] in {"Categorical", "Boolean"}
            and 1 < value["n_distinct"] <= threshold
        }
    )

    if len(categoricals) <= 1:
        return None

    categoricals = sorted(categoricals)
    matrix = np.zeros((len(categoricals), len(categoricals)))
    np.fill_diagonal(matrix, 1.0)
    correlation_matrix = pd.DataFrame(
        matrix,
        index=categoricals,
        columns=categoricals,
    )

    for name1, name2 in itertools.combinations(categoricals, 2):
        confusion_matrix = pd.crosstab(df[name1], df[name2])
        if confusion_matrix.empty:
            correlation_matrix.loc[name2, name1] = np.nan
        else:
            correlation_matrix.loc[name2, name1] = _cramers_corrected_stat(
                confusion_matrix, correction=True
            )
        correlation_matrix.loc[name1, name2] = correlation_matrix.loc[name2, name1]
    return correlation_matrix


@PhiK.compute.register(Settings, pd.DataFrame, Dict[str, VarDescription])
def pandas_phik_compute(
    config: Settings, df: pd.DataFrame, summary: Dict[str, VarDescription]
) -> Optional[pd.DataFrame]:
    df_cols_dict = {i: list(df.columns).index(i) for i in df.columns}

    intcols = {
        key
        for key, value in summary.items()
        # DateTime currently excluded
        # In some use cases, it makes sense to convert it to interval
        # See https://github.com/KaveIO/PhiK/issues/7
        if value["type"] == "Numeric" and 1 < value["n_distinct"]
    }

    selcols = {
        key
        for key, value in summary.items()
        if value["type"] != "Unsupported"
        and 1 < value["n_distinct"] <= config.categorical_maximum_correlation_distinct
    }
    selcols = selcols.union(intcols)
    selected_cols = sorted(selcols, key=lambda i: df_cols_dict[i])

    if len(selected_cols) <= 1:
        return None

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from phik import phik_matrix

        correlation = phik_matrix(df[selected_cols], interval_cols=list(intcols))

    return correlation


@Auto.compute.register(Settings, pd.DataFrame, Dict[str, VarDescription])
def pandas_auto_compute(
    config: Settings, df: pd.DataFrame, summary: Dict[str, VarDescription]
) -> Optional[pd.DataFrame]:
    threshold = config.categorical_maximum_correlation_distinct
    numerical_columns = [
        key
        for key, value in summary.items()
        if value["type"] in {"Numeric", "TimeSeries"} and value["n_distinct"] > 1
    ]
    categorical_columns = [
        key
        for key, value in summary.items()
        if value["type"] in {"Categorical", "Boolean"}
        and 1 < value["n_distinct"] <= threshold
    ]

    if len(numerical_columns + categorical_columns) <= 1:
        return None

    df_discretized = Discretizer(
        DiscretizationType.UNIFORM, n_bins=config.correlations["auto"].n_bins
    ).discretize_dataframe(df)
    columns_tested = sorted(numerical_columns + categorical_columns)

    correlation_matrix = pd.DataFrame(
        np.ones((len(columns_tested), len(columns_tested))),
        index=columns_tested,
        columns=columns_tested,
    )
    for col_1_name, col_2_name in itertools.combinations(columns_tested, 2):
        method = (
            _pairwise_spearman
            if any(elem in categorical_columns for elem in [col_1_name, col_2_name])
            is False
            else _pairwise_cramers
        )

        def f(col_name: str, method: Callable) -> pd.Series:
            return (
                df_discretized
                if col_name in numerical_columns and method is _pairwise_cramers
                else df
            )

        score = method(
            f(col_1_name, method)[col_1_name], f(col_2_name, method)[col_2_name]
        )
        (
            correlation_matrix.loc[col_1_name, col_2_name],
            correlation_matrix.loc[col_2_name, col_1_name],
        ) = (score, score)

    return correlation_matrix
