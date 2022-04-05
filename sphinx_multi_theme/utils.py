"""Helpers."""
import os

from sphinx.application import Sphinx
from sphinx.errors import SphinxError
from sphinx.util import ensuredir, logging


def fork() -> bool:
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
    log.info(">>> Changing outdir from %s to %s", old_outdir, new_outdir)
    app.outdir = new_outdir

    # Set the doctree directory.
    new_doctreedir = old_doctreedir.replace(old_outdir, new_outdir)
    if new_doctreedir == old_doctreedir:
        new_doctreedir = os.path.join(old_doctreedir, subdir)
    log.info(">>> Changing doctreedir from %s to %s", old_doctreedir, new_doctreedir)
    app.doctreedir = new_doctreedir

    # Exit after Sphinx finishes building before it sends Python up the call stack (e.g. during sphinx.testing).
    os_exit = os._exit  # noqa pylint: disable=protected-access
    app.connect("build-finished", lambda *_: os_exit(0), priority=999)
