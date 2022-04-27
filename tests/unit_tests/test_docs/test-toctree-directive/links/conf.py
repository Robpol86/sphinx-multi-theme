"""Sphinx test configuration."""
import os

from sphinx_multi_theme.theme import MultiTheme, Theme

exclude_patterns = ["_build"]
extensions = ["sphinx_multi_theme.multi_theme"]
if os.environ.get("TEST_IN_SUBPROCESS") != "TRUE":
    extensions.append("conftest_fork_exit_save_child_data")
master_doc = "index"
nitpicky = True
html_theme = MultiTheme(
    [
        Theme("sphinx_rtd_theme", "Primary"),
        Theme("sphinx_rtd_theme", "Secondary", subdir="theme_secondary"),
    ]
)
