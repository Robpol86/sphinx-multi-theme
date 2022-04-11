"""Tests."""
import os
import sys
from io import StringIO
from subprocess import CalledProcessError, check_output, STDOUT
from typing import Dict, Tuple

import pytest
from sphinx.testing import path
from sphinx.testing.util import SphinxTestApp

ROOTS = ("print-files/off", "print-files/on")


@pytest.mark.parametrize(
    "testroot", [pytest.param(r, marks=pytest.mark.sphinx("html", freshenv=True, testroot=r)) for r in ROOTS]
)
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
@pytest.mark.sphinx("html", freshenv=True, testroot="print-files/fail")
def test_disable_on_exception(app_params: Tuple[Dict, Dict], fail: bool):
    """Test."""
    srcdir: path = app_params[1]["srcdir"]
    outdir: path = srcdir / "_build" / str(fail) / "html"
    outdir.makedirs()
    cmd = [sys.executable, "-m", "sphinx", "-T", "-n", "-W", srcdir, outdir]

    # Run.
    if fail:
        env = dict(os.environ, TEST_PRINT_FILES_CAUSE_EXC="TRUE")
        with pytest.raises(CalledProcessError) as exc:
            check_output(cmd, env=env, stderr=STDOUT)
        output = exc.value.output
    else:
        output = check_output(cmd, stderr=STDOUT)

    # Check.
    logs = output.decode("utf8").strip()
    lines = logs.splitlines()
    if fail:
        assert lines.count("Sphinx error:") == 1
        assert lines.count("TEST_PRINT_FILES_CAUSE_EXC") == 1
        assert lines.count(f"html{os.sep}") == 0
        assert not os.path.isfile(os.path.join(outdir, "index.html"))
    else:
        assert lines.count("Sphinx error:") == 0
        assert lines.count("TEST_PRINT_FILES_CAUSE_EXC") == 0
        assert lines.count(f"html{os.sep}") == 1
        assert os.path.isfile(os.path.join(outdir, "index.html"))
