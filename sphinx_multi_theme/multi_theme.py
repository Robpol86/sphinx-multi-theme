"""A Sphinx extension that builds copies of your docs using multiple themes into separate subdirectories.

https://sphinx-multi-theme.readthedocs.io
https://github.com/Robpol86/sphinx-multi-theme
https://pypi.org/project/sphinx-multi-theme

Example output file structure:
    docs/_build/html/index.html
    docs/_build/html/_static/jquery.js
    docs/_build/html/theme_alabaster/_static/jquery.js
    docs/_build/html/theme_alabaster/index.html
    docs/_build/html/theme_classic/_static/jquery.js
    docs/_build/html/theme_classic/index.html
"""
from dataclasses import dataclass, field


@dataclass
class Theme:
    """A 'struct' representing one theme."""

    name: str  # e.g. "sphinx_rtd_theme"
    subdir: str = ""  # Subdirectory basename including prefix, e.g. "theme_rtd"
    is_active: bool = field(default=False, init=False)  # If this is the current theme Sphinx is building in this process.

    @property
    def is_primary(self) -> bool:
        """Theme is considered the primary theme if it has no subdir specified."""
        return not self.subdir
