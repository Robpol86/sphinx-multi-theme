"""Tests."""
import os
from io import StringIO

import pytest
from _pytest.monkeypatch import MonkeyPatch
from sphinx.errors import SphinxError
from sphinx.testing.util import SphinxTestApp

ROOTS = ("print-files/off", "print-files/on")


@pytest.mark.parametrize("testroot", [pytest.param(r, marks=pytest.mark.sphinx("html", testroot=r)) for r in ROOTS])
def test(sphinx_app: SphinxTestApp, status: StringIO, testroot: str):
    """Verify single-theme is the same as not using this feature."""
    assert sphinx_app
    logs = status.getvalue().strip()
    lines = logs.splitlines()

    if testroot.endswith("off"):
        assert lines.count(f"|-_static{os.sep}") == 0
        assert lines.count("|-index.html") == 0
    else:
        assert lines.count(f"|-_static{os.sep}") == 1
        assert lines.count("|-index.html") == 1


@pytest.mark.parametrize("fail", [False, True])
@pytest.mark.sphinx("html", testroot="print-files/fail")
def test_disable_on_exception(monkeypatch: MonkeyPatch, app: SphinxTestApp, status: StringIO, fail: bool):
    """Test."""
    if fail:
        monkeypatch.setenv("TEST_PRINT_FILES_CAUSE_EXC", "TRUE")
        with pytest.raises(SphinxError):
            app.build()
    else:
        app.build()
    assert os.path.isfile(os.path.join(app.outdir, "index.html"))

    logs = status.getvalue().strip()
    lines = logs.splitlines()

    if fail:
        assert lines.count(f"html{os.sep}") == 0
    else:
        assert lines.count(f"html{os.sep}") == 1
