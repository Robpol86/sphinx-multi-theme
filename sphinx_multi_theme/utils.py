"""Avoid circular imports and other misc code."""
import os
import sys
import traceback
from os import _exit as os_exit  # noqa
from os import waitpid
from pathlib import Path
from typing import Optional, Tuple

from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.errors import SphinxError
from sphinx.util import ensuredir, logging

CONFIG_NAME_INTERNAL_IS_CHILD = "multi_theme__INTERNAL__is_child"
CONFIG_NAME_INTERNAL_THEMES = "multi_theme__INTERNAL__MultiTheme"
CONFIG_NAME_PRINT_FILES = "multi_theme_print_files"
CONFIG_NAME_PRINT_FILES_STYLE = "multi_theme_print_files_style"
LOGGING_PREFIX = "🍴 "
SPHINX_CONNECT_PRIORITY_FLATTEN_HTML_THEME = 1
SPHINX_CONNECT_PRIORITY_FORK_SPHINX = SPHINX_CONNECT_PRIORITY_FLATTEN_HTML_THEME - 1
SPHINX_CONNECT_PRIORITY_PRINT_FILES = 999
SPHINX_CONNECT_PRIORITY_TERMINATE_FORKED_BUILD = SPHINX_CONNECT_PRIORITY_PRINT_FILES + 1
SPHINX_CONNECT_PRIORITY_UNSUPPORTED_BUILDER_NOOP = 1
SUPPORTED_BUILDERS = ["html", "linkcheck"]


def fork_and_wait(app: Sphinx) -> bool:
    """Fork the Python process and wait for the child process to finish.

    :param app: Sphinx app instance for emitting events.

    :return: True if this is the child process, False if this is still the original/parent process.
    """
    app.emit("multi-theme-before-fork")
    pid = os.fork()  # pylint: disable=no-member
    if pid < 0:
        raise SphinxError(f"Fork failed ({pid})")
    if pid == 0:  # This is the child process.
        app.emit("multi-theme-after-fork-child")
        return True

    # This is the parent (original) process. Wait (block) for child to finish.
    app.emit("multi-theme-after-fork-parent-child-running", pid)
    exit_status = waitpid(pid, 0)[1] // 256  # https://code-maven.com/python-fork-and-wait
    app.emit("multi-theme-after-fork-parent-child-exited", pid, exit_status)
    if exit_status != 0:
        raise SphinxError(f"Child process {pid} failed with status {exit_status}")

    return False


def terminate_forked_build(app: Sphinx, exc: Optional[Exception]):
    """Terminate forked process immediately after the Sphinx build.

    :param app: Sphinx app instance
    :param exc: Exception during build if it failed.
    """
    if exc:
        print(traceback.format_exc())

    log = logging.getLogger(__name__)
    log.info("%sChild process %s", LOGGING_PREFIX, "failed" if exc else "completed")
    sys.stdout.flush()
    sys.stderr.flush()

    exit_status = 1 if exc else 0
    app.emit("multi-theme-child-before-exit", exit_status, exc)
    os_exit(exit_status)


def determine_new_doctreedir(old_doctreedir: Path, old_outdir: Path, new_outdir: Path) -> Tuple[Path, bool]:
    """Return the new doctreedir and if it's external to the outdir.

    :param old_doctreedir: The original doctreedir path.
    :param old_outdir: The original outdir path.
    :param new_outdir: The new outdir path.
    """
    if old_doctreedir.parent.absolute() == old_outdir.absolute():
        # Handle default doctree dir location (e.g. _build/html/.doctrees).
        return new_outdir / old_doctreedir.name, False
    try:
        # Handle doctree being deeper inside outdir.
        return new_outdir / old_doctreedir.absolute().relative_to(old_outdir.absolute()), False
    except ValueError:
        # Doctree dir is external to outdir.
        return old_doctreedir / new_outdir.name, True


def log_dir_change(label: str, old_dir: Path, new_dir: Path, depth: int):
    """Log the directory change with relative paths.

    :param label: Directory label (e.g. "outdir").
    :param old_dir: Old directory.
    :param new_dir: New directory.
    :param depth: Include these many common parent directories.
    """
    log = logging.getLogger(__name__)

    common_prefix = Path(*os.path.commonprefix([old_dir.parts, new_dir.parts]))
    for _ in range(depth):
        common_prefix = common_prefix.parent
    rel_old = old_dir.relative_to(common_prefix)
    rel_new = new_dir.relative_to(common_prefix)

    log.info("%sChanging %s from '%s' to '%s'", LOGGING_PREFIX, label, rel_old, rel_new)


def modify_forked_sphinx_app(app: Sphinx, config: Config, subdir: str):
    """Make changes to the new Sphinx app after forking.

    :param app: Sphinx app instance to modify.
    :param config: Sphinx configuration.
    :param subdir: Build docs into this subdirectory.
    """
    old_outdir = app.outdir
    old_doctreedir = app.doctreedir

    # Set the output directory.
    new_outdir = os.path.join(old_outdir, subdir)
    ensuredir(new_outdir)
    log_dir_change("outdir", Path(old_outdir), Path(new_outdir), 2)
    app.outdir = new_outdir

    # Set the doctree directory.
    new_doctreedir, is_external = determine_new_doctreedir(Path(old_doctreedir), Path(old_outdir), Path(new_outdir))
    log_dir_change("doctreedir", Path(old_doctreedir), new_doctreedir, 3 if is_external else 2)
    app.doctreedir = str(new_doctreedir)

    # Set flag.
    config[CONFIG_NAME_INTERNAL_IS_CHILD] = True

    # Exit after Sphinx finishes building before it sends Python up the call stack (e.g. during sphinx.testing).
    app.connect("build-finished", terminate_forked_build, priority=SPHINX_CONNECT_PRIORITY_TERMINATE_FORKED_BUILD)
