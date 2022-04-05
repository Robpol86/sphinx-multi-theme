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
from typing import Dict, Union

from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.util import logging

from sphinx_multi_theme import __version__
from sphinx_multi_theme.theme import MultiTheme

CONFIG_NAME_INTERNAL_THEMES = "multi_theme__INTERNAL__MultiTheme"


def flatten_html_theme(_: Sphinx, config: Config):
    """Replace MultiTheme instance with a string (the active theme's name).

    :param _: Sphinx application.
    :param config: Sphinx configuration.
    """
    multi_theme_instance: Union[str, MultiTheme] = config["html_theme"]
    try:
        active_theme_name = multi_theme_instance.active.name
    except AttributeError:
        log = logging.getLogger(__name__)
        log.warning("Sphinx config value for `html_theme` not a %s instance", MultiTheme.__name__)
    else:
        config["html_theme"] = active_theme_name
        config[CONFIG_NAME_INTERNAL_THEMES] = multi_theme_instance


def setup(app: Sphinx) -> Dict[str, str]:
    """Called by Sphinx during phase 0 (initialization).

    :param app: Sphinx application.

    :returns: Extension version.
    """
    app.add_config_value(CONFIG_NAME_INTERNAL_THEMES, None, "html")
    app.connect("config-inited", flatten_html_theme)
    return dict(version=__version__)
