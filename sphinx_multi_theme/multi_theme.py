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
import sys
from os import _exit as os_exit  # noqa
from typing import Dict, List, Tuple, Union

from seedir import seedir
from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.util import logging

from sphinx_multi_theme import __version__, utils
from sphinx_multi_theme.directives import MultiThemeTocTreeDirective
from sphinx_multi_theme.nodes import MultiThemeTocTreeNode
from sphinx_multi_theme.theme import MultiTheme


def fork_sphinx(app: Sphinx, config: Config):
    """Fork the Python Sphinx process serially as many times as there are secondary themes.

    :param app: Sphinx application.
    :param config: Sphinx configuration.
    """
    log = logging.getLogger(__name__)
    multi_theme_instance: Union[str, MultiTheme] = config["html_theme"]

    # Noop if MultiTheme not used or only one theme specified by the user.
    try:
        themes = multi_theme_instance.themes
    except AttributeError:
        log.warning("Sphinx config value for `html_theme` not a %s instance", MultiTheme.__name__)
        return
    if len(themes) < 2:
        return

    # Noop on unsupported platforms.
    if not hasattr(os, "fork"):
        removed = multi_theme_instance.truncate()
        removed_names = [t.name for t in removed]
        log.warning("Platform does not support forking, removing themes: %r", removed_names)
        return

    # Fork and wait.
    log.info("%sEntering multi-theme build mode", utils.LOGGING_PREFIX)
    for idx, theme in enumerate(themes):
        if not theme.is_primary:
            log.info("%sBuilding docs with theme %r into directory %r", utils.LOGGING_PREFIX, theme.name, theme.subdir)
            app.emit("multi-theme-before-fork", config, theme.name, theme.subdir)
            if utils.fork_and_wait(app):
                # This is the child process.
                multi_theme_instance.set_active(idx)
                utils.modify_forked_sphinx_app(app, config, theme.subdir)
                return
            log.info("%sDone with theme %r", utils.LOGGING_PREFIX, theme.name)
    log.info("%sExiting multi-theme build mode", utils.LOGGING_PREFIX)


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
        return

    # Update config.
    config["html_theme"] = active_theme_name
    config[utils.CONFIG_NAME_INTERNAL_THEMES] = multi_theme_instance

    # Support ReadTheDocs hosted docs.
    html_context_keys: List[Tuple[str, str]] = []
    for top_level_key in ("html_context", "context"):
        if top_level_key in config:
            for key, value in config[top_level_key].items():
                if value == multi_theme_instance:
                    html_context_keys.append((top_level_key, key))
                    config[top_level_key][key] = active_theme_name


def unsupported_builder_noop(app: Sphinx):
    """Disable extension on unsupported builders.

    :param app: Sphinx application.
    """
    if app.builder.name in utils.SUPPORTED_BUILDERS:
        return
    log = logging.getLogger(__name__)

    if app.config[utils.CONFIG_NAME_INTERNAL_IS_CHILD]:
        log.info("%sUnsupported builder %r, terminating child process", utils.LOGGING_PREFIX, app.builder.name)
        sys.stdout.flush()
        sys.stderr.flush()
        try:
            os.rmdir(app.outdir)
        except OSError:
            pass
        try:
            os.rmdir(app.doctreedir)
        except OSError:
            pass
        app.emit("multi-theme-unsupported-builder-child-before-exit", app.builder, utils.SUPPORTED_BUILDERS)
        os_exit(0)

    multi_theme_instance = app.config[utils.CONFIG_NAME_INTERNAL_THEMES]
    if multi_theme_instance:
        removed = multi_theme_instance.truncate()
        if removed:
            removed_names = [t.name for t in removed]
            log.info("%sUnsupported builder %r, removing themes: %r", utils.LOGGING_PREFIX, app.builder.name, removed_names)


def print_files(app: Sphinx, exc: Exception):
    """Print outdir listing.

    :param app: Sphinx application.
    :param exc: Exception raised during Sphinx build process, may be unrelated to this library.
    """
    if exc:
        return
    if not app.config[utils.CONFIG_NAME_PRINT_FILES]:
        return
    log = logging.getLogger(__name__)
    print(flush=True)  # https://github.com/readthedocs/readthedocs-sphinx-ext/blob/2.1.5/readthedocs_ext/readthedocs.py#L270
    output = seedir(
        app.outdir,
        style=app.config[utils.CONFIG_NAME_PRINT_FILES_STYLE],
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
    app.add_config_value(utils.CONFIG_NAME_INTERNAL_IS_CHILD, False, "")
    app.add_config_value(utils.CONFIG_NAME_INTERNAL_THEMES, None, "html")
    app.add_config_value(utils.CONFIG_NAME_PRINT_FILES, False, "")
    app.add_config_value(utils.CONFIG_NAME_PRINT_FILES_STYLE, "emoji" if os.sep == "/" else "dash", "")
    app.add_directive("multi-theme-toctree", MultiThemeTocTreeDirective)
    app.add_event("multi-theme-after-fork-child")
    app.add_event("multi-theme-after-fork-parent-child-exited")
    app.add_event("multi-theme-after-fork-parent-child-running")
    app.add_event("multi-theme-before-fork")
    app.add_event("multi-theme-child-before-exit")
    app.add_event("multi-theme-unsupported-builder-child-before-exit")
    app.add_node(MultiThemeTocTreeNode)
    app.connect("build-finished", print_files, priority=utils.SPHINX_CONNECT_PRIORITY_PRINT_FILES)
    app.connect("builder-inited", unsupported_builder_noop, priority=utils.SPHINX_CONNECT_PRIORITY_UNSUPPORTED_BUILDER_NOOP)
    app.connect("config-inited", flatten_html_theme, priority=utils.SPHINX_CONNECT_PRIORITY_FLATTEN_HTML_THEME)
    app.connect("config-inited", fork_sphinx, priority=utils.SPHINX_CONNECT_PRIORITY_FORK_SPHINX)
    return dict(parallel_read_safe=True, parallel_write_safe=True, version=__version__)
