"""pytest conftest."""
import os
import sys
from io import StringIO
from pathlib import Path
from types import ModuleType
from typing import Dict, Tuple

import coverage
import pytest
from _pytest.config import Config
from _pytest.fixtures import FixtureRequest
from _pytest.monkeypatch import MonkeyPatch
from sphinx.application import Sphinx
from sphinx.testing.path import path
from sphinx.testing.util import SphinxTestApp

pytest_plugins = "sphinx.testing.fixtures"  # pylint: disable=invalid-name


@pytest.fixture(autouse=True)
def fork_exit_save_child_data(monkeypatch: MonkeyPatch):
    """Create a temporary Sphinx extension in memory via a faux Python module with Sphinx hooks.

    Hook functions take care of merging child logs into the parent process to expose them to tests. Functions also take care
    of saving test coverage only covered in child processes.
    """
    status_log_file_name = "_sphinx_child_log_status.log"
    warning_log_file_name = "_sphinx_child_log_warning.log"

    def truncate_logs_after_child_is_born(app: Sphinx):
        app._status.seek(0)  # noqa pylint: disable=protected-access
        app._status.truncate()  # noqa pylint: disable=protected-access
        app._warning.seek(0)  # noqa pylint: disable=protected-access
        app._warning.truncate()  # noqa pylint: disable=protected-access

    def dump_logs_save_cov_before_child_is_killed(app: Sphinx, *_):
        # Save code coverage.
        cov = coverage.Coverage.current()
        if cov:
            cov.stop()
            cov.save()
        # Save Sphinx log statements.
        status: StringIO = app._status  # noqa pylint: disable=protected-access
        warning: StringIO = app._warning  # noqa pylint: disable=protected-access
        status_file = os.path.join(app.outdir, "..", status_log_file_name)
        warning_file = os.path.join(app.outdir, "..", warning_log_file_name)
        with open(status_file, "w", encoding="utf8") as handle:
            handle.write(status.getvalue())
        with open(warning_file, "w", encoding="utf8") as handle:
            handle.write(warning.getvalue())

    def merge_dumped_child_sphinx_logs_into_parent_sphinx_logs(app: Sphinx, *_):
        status: StringIO = app._status  # noqa pylint: disable=protected-access
        warning: StringIO = app._warning  # noqa pylint: disable=protected-access
        status_file = os.path.join(app.outdir, status_log_file_name)
        warning_file = os.path.join(app.outdir, warning_log_file_name)
        with open(status_file, "r", encoding="utf8") as handle:
            status.write(handle.read())
        with open(warning_file, "r", encoding="utf8") as handle:
            warning.write(handle.read())
        os.unlink(status_file)
        os.unlink(warning_file)

    def setup(app: Sphinx):
        app.connect("multi-theme-after-fork-child", truncate_logs_after_child_is_born)
        app.connect("multi-theme-child-before-exit", dump_logs_save_cov_before_child_is_killed)
        app.connect("multi-theme-after-fork-parent-child-exited", merge_dumped_child_sphinx_logs_into_parent_sphinx_logs)

    conftest_fork_exit_save_child_data = ModuleType("conftest_fork_exit_save_child_data")
    conftest_fork_exit_save_child_data.setup = setup
    monkeypatch.setitem(
        sys.modules,
        conftest_fork_exit_save_child_data.__name__,  # pylint: disable=no-member
        conftest_fork_exit_save_child_data,
    )


@pytest.fixture(scope="session")
def rootdir() -> path:
    """Used by sphinx.testing, return the directory containing all test docs."""
    return path(__file__).parent.abspath()


@pytest.fixture(name="sphinx_app")
def _sphinx_app(app: SphinxTestApp) -> SphinxTestApp:
    """Instantiate a new Sphinx app per test function."""
    app.build()
    yield app


@pytest.fixture(name="outdir")
def _outdir(sphinx_app: SphinxTestApp) -> Path:
    """Return the Sphinx output directory with HTML files."""
    return Path(sphinx_app.outdir)


@pytest.fixture()
def skip_if_no_fork() -> bool:
    """Skip a test if the platform is missing os.fork()."""
    if not hasattr(os, "fork"):
        pytest.skip("Unsupported platform: no os.fork()")
    return True


def pytest_configure(config: Config):
    """Register markers."""
    config.addinivalue_line("markers", "keep_srcdir: don't delete session-scoped temporary copy of test source docs")


@pytest.fixture(name="app_params")
def _app_params(request: FixtureRequest, app_params: Tuple[Dict, Dict]) -> Tuple[Dict, Dict]:
    """Delete srcdir after every test."""
    if not request.node.get_closest_marker("keep_srcdir"):
        request.addfinalizer(app_params[1]["srcdir"].rmtree)
    return app_params
