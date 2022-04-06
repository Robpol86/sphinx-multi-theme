"""Helpers."""
import os

from sphinx.application import Sphinx
from sphinx.errors import SphinxError
from sphinx.util import ensuredir, logging

LOGGING_PREFIX = "🍴 "


def fork_and_wait() -> bool:
    """Fork the Python process and wait for the child process to finish.

    :return: True if this is the child process, False if this is still the original/parent process.
    """
    pid = os.fork()  # noqa  # pylint: disable=no-member
    if pid < 0:
        raise SphinxError(f"Fork failed ({pid})")
    if pid == 0:  # This is the child process.
        return True

    # This is the parent (original) process. Wait (block) for child to finish.
    exit_status = os.waitpid(pid, 0)[1] // 256  # https://code-maven.com/python-fork-and-wait
    if exit_status != 0:
        raise SphinxError(f"Child process {pid} failed with status {exit_status}")

    return False


def modify_forked_sphinx_app(app: Sphinx, subdir: str):
    """Make changes to the new Sphinx app after forking.

    :param app: Sphinx app instance to modify.
    :param subdir: Build docs into this subdirectory.
    """
    log = logging.getLogger(__file__)
    old_outdir = app.outdir
    old_doctreedir = app.doctreedir

    # Set the output directory.
    new_outdir = os.path.join(old_outdir, subdir)
    ensuredir(new_outdir)
    common_prefix = os.path.dirname(os.path.dirname(os.path.commonprefix([old_outdir, new_outdir])))
    rel_old = os.path.relpath(old_outdir, common_prefix)
    rel_new = os.path.relpath(new_outdir, common_prefix)
    log.info("%sChanging outdir from %r to %r", LOGGING_PREFIX, rel_old, rel_new)
    app.outdir = new_outdir

    # Set the doctree directory.
    new_doctreedir = old_doctreedir.replace(old_outdir, new_outdir)
    if new_doctreedir == old_doctreedir:
        new_doctreedir = os.path.join(old_doctreedir, subdir)
    common_prefix = os.path.dirname(os.path.dirname(os.path.commonprefix([old_doctreedir, new_doctreedir])))
    rel_old = os.path.relpath(old_doctreedir, common_prefix)
    rel_new = os.path.relpath(new_doctreedir, common_prefix)
    log.info("%sChanging doctreedir from %r to %r", LOGGING_PREFIX, rel_old, rel_new)
    app.doctreedir = new_doctreedir

    # Exit after Sphinx finishes building before it sends Python up the call stack (e.g. during sphinx.testing).
    os_exit = os._exit  # noqa pylint: disable=protected-access
    app.connect("build-finished", lambda *_: os_exit(0), priority=999)
