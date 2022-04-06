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
import os
from typing import Dict, List, Tuple, Union

from seedir import seedir
from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.util import logging

from sphinx_multi_theme import __version__
from sphinx_multi_theme.theme import MultiTheme

CONFIG_NAME_INTERNAL_THEMES = "multi_theme__INTERNAL__MultiTheme"
CONFIG_NAME_PRINT_FILES = "multi_theme_print_files"
CONFIG_NAME_PRINT_FILES_STYLE = "multi_theme_print_files_style"
LOGGING_PREFIX = "🍴 "
SPHINX_CONNECT_PRIORITY_FLATTEN_HTML_THEME = 1
SPHINX_CONNECT_PRIORITY_PRINT_FILES = 999


def flatten_html_theme(_: Sphinx, config: Config):
    """Move MultiTheme instance to an internal Sphinx config variable and set html_theme to the active theme's name.

    :param _: Sphinx application.
    :param config: Sphinx configuration.
    """
    multi_theme_instance: Union[str, MultiTheme] = config["html_theme"]

    # Noop if MultiTheme not used.
    try:
        active_theme_name = multi_theme_instance.active.name
    except AttributeError:
        log = logging.getLogger(__name__)
        log.warning("%sSphinx config value for `html_theme` not a %s instance", LOGGING_PREFIX, MultiTheme.__name__)
        return

    # Update config.
    config["html_theme"] = active_theme_name
    config[CONFIG_NAME_INTERNAL_THEMES] = multi_theme_instance

    # Support ReadTheDocs hosted docs.
    html_context_keys: List[Tuple[str, str]] = []
    for top_level_key in ("html_context", "context"):
        if top_level_key in config:
            for key, value in config[top_level_key].items():
                if value == multi_theme_instance:
                    html_context_keys.append((top_level_key, key))
                    config[top_level_key][key] = active_theme_name


def print_files(app: Sphinx, exc: Exception):
    """Print outdir listing.

    :param app: Sphinx application.
    :param exc: Exception raised during Sphinx build process, may be unrelated to this library.
    """
    if exc:
        return  # pragma: no cover
    if not app.config[CONFIG_NAME_PRINT_FILES]:
        return
    log = logging.getLogger(__name__)
    print(flush=True)  # https://github.com/readthedocs/readthedocs-sphinx-ext/blob/2.1.5/readthedocs_ext/readthedocs.py#L270
    output = seedir(
        app.outdir,
        style=app.config[CONFIG_NAME_PRINT_FILES_STYLE],
        printout=False,
        first="folders",
        sort=True,
        slash=os.sep,
    )
    for line in output.splitlines():
        log.info(line)


def setup(app: Sphinx) -> Dict[str, str]:
    """Called by Sphinx during phase 0 (initialization).

    :param app: Sphinx application.

    :returns: Extension version.
    """
    app.add_config_value(CONFIG_NAME_INTERNAL_THEMES, None, "html")
    app.add_config_value(CONFIG_NAME_PRINT_FILES, False, "")
    app.add_config_value(CONFIG_NAME_PRINT_FILES_STYLE, "emoji" if os.sep == "/" else "dash", "")
    app.connect("build-finished", print_files, priority=SPHINX_CONNECT_PRIORITY_PRINT_FILES)
    app.connect("config-inited", flatten_html_theme, priority=SPHINX_CONNECT_PRIORITY_FLATTEN_HTML_THEME)
    return dict(version=__version__)
