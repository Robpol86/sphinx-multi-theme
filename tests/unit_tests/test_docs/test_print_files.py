"""Tests."""
import os
from io import StringIO

import pytest
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
