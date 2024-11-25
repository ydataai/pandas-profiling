from __future__ import annotations

from collections import abc
from dataclasses import dataclass
from typing import Any, Iterator

from ydata_profiling.model.var_description.counts import VarCounts


@dataclass
class VarDescription(VarCounts):
    """Default description for one data column.
    Extends VarCounts class with information about distinct and unique values."""

    var_specific: dict

    def __getitem__(self, item: str):
        """Make the object subscriptable."""
        return self.var_specific[item]

    def __setitem__(self, key: str, value: Any):
        """Make the object subscriptable."""
        self.var_specific[key] = value

    def update(self, _dict: dict) -> None:
        """To support old dict like interface."""
        self.var_specific.update(_dict)

    def items(self) -> abc.ItemsView:
        """To support old dict like interface."""
        return self.var_specific.items()

    def get(self, key: str, default: Any = None) -> Any:
        """To support old dict like interface."""
        return self.var_specific.get(key, default)

    def pop(self, key: str, default: Any = None) -> Any:
        """To support old dict like interface."""
        return self.var_specific.pop(key, default)

    def __iter__(self) -> Iterator:
        """To support old dict like interface."""
        return self.var_specific.__iter__()

    @classmethod
    def from_var_counts(cls, var_counts: VarCounts, init_dict: dict) -> VarDescription:
        """Get a default description from a VarCounts object."""
        return VarDescription(
            n=var_counts.n,
            count=var_counts.count,
            n_missing=var_counts.n_missing,
            p_missing=var_counts.p_missing,
            hashable=var_counts.hashable,
            memory_size=var_counts.memory_size,
            ordering=var_counts.ordering,
            var_specific=init_dict,
            value_counts_index_sorted=var_counts.value_counts_index_sorted,
            value_counts_without_nan=var_counts.value_counts_without_nan,
            value_counts=var_counts.value_counts,
        )
