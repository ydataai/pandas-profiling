"""Compute statistical description of datasets."""

from typing import Any, Dict

from multimethod import multimethod
from tqdm import tqdm
from visions import VisionsTypeset

from ydata_profiling.config import Settings
from ydata_profiling.model.summarizer import BaseSummarizer
from ydata_profiling.model.var_description.default import VarDescription


@multimethod
def describe_1d(
    config: Settings,
    series: Any,
    summarizer: BaseSummarizer,
    typeset: VisionsTypeset,
) -> VarDescription:
    raise NotImplementedError()


@multimethod
def get_series_descriptions(
    config: Settings,
    df: Any,
    summarizer: BaseSummarizer,
    typeset: VisionsTypeset,
    pbar: tqdm,
) -> Dict[str, VarDescription]:
    raise NotImplementedError()
