"""Sphinx test configuration."""
import os

from sphinx.application import Sphinx
from sphinx.util import logging

from sphinx_multi_theme.theme import MultiTheme
from sphinx_multi_theme.utils import CONFIG_NAME_INTERNAL_IS_CHILD


copyright = "Robpol86 2022"  # noqa
exclude_patterns = ["_build"]
extensions = ["sphinx_multi_theme.multi_theme"]
if os.environ.get("TEST_IN_SUBPROCESS") != "TRUE":
    extensions.append("conftest_fork_exit_save_child_data")
master_doc = "index"
nitpicky = True
html_theme = MultiTheme(["classic", "traditional", "alabaster"])
version = "0.0.0"


def setup(app: Sphinx):
    """Log value of is_child flag."""

    def callback(app_: Sphinx, *_):
        log = logging.getLogger(__name__)
        config = app_.config
        is_child = config[CONFIG_NAME_INTERNAL_IS_CHILD]
        log.info("callback(): html_theme=%r, is_child=%r", config["html_theme"], is_child)

    app.connect("env-before-read-docs", callback)
