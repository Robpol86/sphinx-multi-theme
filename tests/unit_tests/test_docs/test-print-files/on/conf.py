"""Sphinx test configuration."""
from sphinx_multi_theme.theme import MultiTheme


exclude_patterns = ["_build"]
extensions = ["sphinx_multi_theme.multi_theme", "conftest_fork_exit_save_child_data"]
master_doc = "index"
nitpicky = True
html_theme = MultiTheme(["classic"])
multi_theme_print_files = True
multi_theme_print_files_style = "dash"
