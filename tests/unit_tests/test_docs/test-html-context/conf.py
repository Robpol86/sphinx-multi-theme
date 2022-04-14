"""Sphinx test configuration."""
from sphinx_multi_theme.theme import MultiTheme


exclude_patterns = ["_build"]
extensions = [
    "readthedocs_ext.readthedocs",
    "sphinx_multi_theme.multi_theme",
    "conftest_fork_exit_save_child_data",
]
master_doc = "index"
nitpicky = True
html_theme = MultiTheme(["classic"])
html_context = {"html_theme": html_theme, "other": "for branch coverage"}
