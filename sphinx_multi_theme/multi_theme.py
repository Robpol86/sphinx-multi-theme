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
from typing import Dict, List, Tuple, Union

from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.util import logging

from sphinx_multi_theme import __version__
from sphinx_multi_theme.theme import MultiTheme
from sphinx_multi_theme.utils import fork, LOGGING_PREFIX, modify_forked_sphinx_app

CONFIG_NAME_INTERNAL_THEMES = "multi_theme__INTERNAL__MultiTheme"


def fork_and_flatten_html_theme(app: Sphinx, config: Config):
    """Fork the Python process and set html_theme to the theme name.

    :param app: Sphinx application.
    :param config: Sphinx configuration.
    """
    log = logging.getLogger(__name__)
    multi_theme_instance: Union[str, MultiTheme] = config["html_theme"]

    # Noop if MultiTheme not used.
    try:
        primary_theme_name = multi_theme_instance.primary.name
    except AttributeError:
        log.warning("%sSphinx config value for `html_theme` not a %s instance", LOGGING_PREFIX, MultiTheme.__name__)
        return

    # Update config.
    config["html_theme"] = primary_theme_name
    config[CONFIG_NAME_INTERNAL_THEMES] = multi_theme_instance

    # Support ReadTheDocs hosted docs.
    html_context_keys: List[Tuple[str, str]] = []
    for top_level_key in ("html_context", "context"):
        if top_level_key in config:
            for key, value in config[top_level_key].items():
                if value == multi_theme_instance:
                    html_context_keys.append((top_level_key, key))
                    config[top_level_key][key] = primary_theme_name

    # Skip fork if only one theme used.
    if len(multi_theme_instance) < 2:
        return

    # Fork for each secondary theme serially.
    log.info("%sEntering multi-theme build mode", LOGGING_PREFIX)
    for idx, theme in enumerate(multi_theme_instance):
        if not theme.is_primary:
            log.info("%sBuilding docs with theme %s into %s", LOGGING_PREFIX, theme.name, theme.subdir)
            if fork():
                # This is the child process.
                multi_theme_instance.set_active(idx)
                modify_forked_sphinx_app(app, theme.subdir)
                config["html_theme"] = theme.name
                for key in html_context_keys:
                    config["html_context"][key] = theme.name
                return
            log.info("%sDone with theme %s", LOGGING_PREFIX, theme.name)
    log.info("%sExiting multi-theme build mode", LOGGING_PREFIX)


def setup(app: Sphinx) -> Dict[str, str]:
    """Called by Sphinx during phase 0 (initialization).

    :param app: Sphinx application.

    :returns: Extension version.
    """
    app.add_config_value(CONFIG_NAME_INTERNAL_THEMES, None, "html")
    app.connect("config-inited", fork_and_flatten_html_theme)
    return dict(version=__version__)
