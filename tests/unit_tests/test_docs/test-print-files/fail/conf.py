"""Sphinx test configuration."""
import os

from sphinx.application import Sphinx
from sphinx.errors import SphinxError

from sphinx_multi_theme.theme import MultiTheme


exclude_patterns = ["_build"]
extensions = ["sphinx_multi_theme.multi_theme"]
master_doc = "index"
nitpicky = True
html_theme = MultiTheme(["classic"])
multi_theme_print_files = True
multi_theme_print_files_style = "dash"


def setup(app: Sphinx):
    """Cause failure."""

    def callback(*_):
        if os.environ.get("TEST_PRINT_FILES_CAUSE_EXC") == "TRUE":
            raise SphinxError("TEST_PRINT_FILES_CAUSE_EXC")

    app.connect("doctree-resolved", callback)
