"""Sphinx test configuration."""
from sphinx_multi_theme.theme import MultiTheme

exclude_patterns = ["_build"]
extensions = ["sphinx_multi_theme.multi_theme"]
master_doc = "index"
nitpicky = True
html_theme = MultiTheme(["classic", "traditional", "alabaster"])
