from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from pandas import Timedelta

from ydata_profiling.model.var_description.default import VarDescription


@dataclass
class BaseAnalysis:
    """Description of base analysis module of report.
    Overall info about report.

    Attributes
        title (str): Title of report.
        date_start (Union[datetime, List[datetime]]): Start of generating description.
        date_end (Union[datetime, List[datetime]]): End of generating description.
    """

    title: str
    date_start: Union[datetime, List[datetime]]
    date_end: Union[datetime, List[datetime]]

    def __init__(self, title: str, date_start: datetime, date_end: datetime) -> None:
        self.title = title
        self.date_start = date_start
        self.date_end = date_end

    @property
    def duration(self) -> Union[timedelta, List[timedelta]]:
        if isinstance(self.date_start, datetime) and isinstance(
            self.date_end, datetime
        ):
            return self.date_end - self.date_start
        if isinstance(self.date_start, list) and isinstance(self.date_end, list):
            return [
                self.date_end[i] - self.date_start[i]
                for i in range(len(self.date_start))
            ]
        else:
            raise TypeError()


@dataclass
class TimeIndexAnalysis:
    """Description of timeseries index analysis module of report.

    Attributes:
        n_series (Union[int, List[int]): Number of time series identified in the dataset.
        length (Union[int, List[int]): Number of data points in the time series.
        start (Any): Starting point of the time series.
        end (Any): Ending point of the time series.
        period (Union[float, List[float]): Average interval between data points in the time series.
        frequency (Union[Optional[str], List[Optional[str]]): A string alias given to useful common time series frequencies, e.g. H - hours.
    """

    n_series: Union[int, List[int]]
    length: Union[int, List[int]]
    start: Any
    end: Any
    period: Union[float, List[float], Timedelta, List[Timedelta]]
    frequency: Union[Optional[str], List[Optional[str]]]

    def __init__(
        self,
        n_series: int,
        length: int,
        start: Any,
        end: Any,
        period: float,
        frequency: Optional[str] = None,
    ) -> None:
        self.n_series = n_series
        self.length = length
        self.start = start
        self.end = end
        self.period = period
        self.frequency = frequency


@dataclass
class BaseDescription:
    """Description of DataFrame.

    Attributes:
        analysis (BaseAnalysis): Base info about report. Title, start time and end time of description generating.
        time_index_analysis (Optional[TimeIndexAnalysis]): Description of timeseries index analysis module of report.
        table (Any): DataFrame statistic. Base information about DataFrame.
        variables (Dict[str, Any]): Description of variables (columns) of DataFrame. Key is column name, value is description dictionary.
        scatter (Any): Pairwise scatter for all variables. Plot interactions between variables.
        correlations (Dict[str, Any]): Prepare correlation matrix for DataFrame
        missing (Dict[str, Any]): Describe missing values.
        alerts (Any): Take alerts from all modules (variables, scatter, correlations), and group them.
        package (Dict[str, Any]): Contains version of pandas profiling and config.
        sample (Any): Sample of data.
        duplicates (Any): Description of duplicates.
    """

    analysis: BaseAnalysis
    time_index_analysis: Optional[TimeIndexAnalysis]
    table: Any
    variables: Dict[str, VarDescription]
    scatter: Any
    correlations: Dict[str, Any]
    missing: Dict[str, Any]
    alerts: Any
    package: Dict[str, Any]
    sample: Any
    duplicates: Any
