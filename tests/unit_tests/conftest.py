"""pytest fixtures."""
import os
from typing import Dict

import coverage
from coverage.config import CoverageConfig
from coverage.plugin_support import Plugins


class CoverageConfigOverrides(coverage.CoveragePlugin):
    """Override coverage configuration."""

    def configure(self, config: CoverageConfig):
        """Override configuration.

        :param config: Coverage config.
        """
        if os.name == "nt":
            config.set_option("report:fail_under", 0.0)  # Disable on Windows due to lack of os.fork().


def coverage_init(reg: Plugins, _: Dict):
    """Coverage plugin entrypoint (via pyproject.toml).

    :param reg: Plugin registration entrypoint.
    :param _: Unused.
    """
    reg.add_configurer(CoverageConfigOverrides())
