"""Sphinx configuration file."""
# pylint: disable=invalid-name
import time

from sphinx_multi_theme import __version__ as version  # noqa
from sphinx_multi_theme.theme import MultiTheme, Theme


# General configuration.
author = "Robpol86"
copyright = f'{time.strftime("%Y")}, {author}'  # pylint: disable=redefined-builtin  # noqa
html_last_updated_fmt = f"%c {time.tzname[time.localtime().tm_isdst]}"
exclude_patterns = []
extensions = [
    "notfound.extension",  # https://sphinx-notfound-page.readthedocs.io
    "sphinx_copybutton",  # https://sphinx-copybutton.readthedocs.io
    "sphinx_multi_theme.multi_theme",
    "sphinx_panels",  # https://sphinx-panels.readthedocs.io
    "sphinxext.opengraph",  # https://sphinxext-opengraph.readthedocs.io
]
language = "en"
project = "sphinx-multi-theme"
pygments_style = "vs"


# Options for HTML output.
html_copy_source = False
html_theme = MultiTheme(
    [
        Theme("sphinx_rtd_theme", "Read the Docs"),
        Theme("alabaster", "Alabaster"),
        Theme("classic", "Classic"),
        Theme("traditional", "Traditional"),
    ]
)


# Options for sphinx-multi-theme.
multi_theme_print_files = True


# https://sphinxext-opengraph.readthedocs.io/en/latest/#options
ogp_site_name = project
ogp_type = "website"
ogp_use_first_image = True
