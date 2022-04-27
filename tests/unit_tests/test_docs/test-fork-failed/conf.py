"""Sphinx test configuration."""
import os

from sphinx.application import Sphinx
from sphinx.errors import SphinxError

from sphinx_multi_theme.theme import MultiTheme


exclude_patterns = ["_build"]
extensions = ["sphinx_multi_theme.multi_theme"]
master_doc = "index"
nitpicky = True
html_theme = MultiTheme(["classic", "traditional", "alabaster"])


def setup(app: Sphinx):
    """Cause failure."""

    def callback_env_updated(*_):
        if os.environ.get("TEST_ENV_UPDATED_CAUSE_EXC") == "TRUE":
            raise SphinxError("TEST_ENV_UPDATED_CAUSE_EXC")

    def callback_after_fork_child(*_):
        if os.environ.get("TEST_EXIT_STATUS_CAUSE_EXC") == "TRUE":
            raise SphinxError("TEST_EXIT_STATUS_CAUSE_EXC")

    app.connect("multi-theme-after-fork-child", callback_after_fork_child)
    app.connect("env-updated", callback_env_updated)
