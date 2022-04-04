"""Sphinx configuration file."""
# pylint: disable=invalid-name
import time


# General configuration.
author = "Robpol86"
copyright = f'{time.strftime("%Y")}, {author}'  # pylint: disable=redefined-builtin  # noqa
html_last_updated_fmt = f"%c {time.tzname[time.localtime().tm_isdst]}"
exclude_patterns = []
extensions = [
    "notfound.extension",  # https://sphinx-notfound-page.readthedocs.io
    "sphinx_copybutton",  # https://sphinx-copybutton.readthedocs.io
    "sphinx_panels",  # https://sphinx-panels.readthedocs.io
    "sphinxext.opengraph",  # https://sphinxext-opengraph.readthedocs.io
]
language = "en"
project = "sphinx-multi-theme"
pygments_style = "vs"


# Options for HTML output.
html_copy_source = False
html_theme = "sphinx_rtd_theme"


# https://sphinxext-opengraph.readthedocs.io/en/latest/#options
ogp_site_name = project
ogp_type = "website"
ogp_use_first_image = True
