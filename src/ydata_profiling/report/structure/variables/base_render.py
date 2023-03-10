from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict

from ydata_profiling.config import Settings
from ydata_profiling.report.presentation.core.variable_info import VariableInfo
from ydata_profiling.report.structure.variables import render_common


@dataclass
class BaseRenderVariable(metaclass=ABCMeta):
    config: Settings
    summary: Dict[str, Any]

    def _get_info(self) -> VariableInfo:
        """Return rendered basic info about variable."""
        return VariableInfo(
            anchor_id=self.summary["varid"],
            var_name=self.summary["varname"],
            var_type=self.summary["type"],
            alerts=self.summary["alerts"],
            description=self.summary["description"],
            style=self.config.html.style,
        )

    @abstractmethod
    def _get_top(self):
        """Return top section of rendered variable."""
        pass

    @abstractmethod
    def _get_bottom(self):
        """Return bottom section of rendered variable."""
        pass

    def render(self):
        """Return template for variable prot."""
        template_variables = {}
        template_variables["top"] = self._get_top()
        template_variables["bottom"] = self._get_bottom()
        return template_variables

    pass
