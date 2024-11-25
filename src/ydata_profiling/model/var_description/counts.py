from dataclasses import dataclass
from typing import Any, Union


@dataclass
class VarCounts:
    """Data about counts in variable column."""

    n: Union[int, list]
    """Count of rows in the series."""
    count: Union[int, list]
    """Count of not missing rows in the series."""
    n_missing: Union[int, list]
    """Count of missing rows in the series."""
    p_missing: Union[float, list]
    """Proportion of missing rows in the series."""

    hashable: Union[bool, list]
    value_counts_without_nan: Any
    """Counts of values in the series without NaN. Values as index, counts as values."""
    value_counts_index_sorted: Any
    """Sorted counts of values in the series without NaN. Sorted by counts."""
    ordering: Union[bool, list]
    memory_size: Union[int, list]

    value_counts: Any
    """Counts of values in original series type. Values as index, counts as values."""
