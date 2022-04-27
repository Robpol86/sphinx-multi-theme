"""Tests."""
import os
import re
import sys
from subprocess import CalledProcessError, check_output, STDOUT
from typing import Callable, Dict, Tuple

import pytest
from _pytest.monkeypatch import MonkeyPatch
from sphinx.errors import SphinxError
from sphinx.testing.path import path


@pytest.mark.usefixtures("skip_if_no_fork")
@pytest.mark.sphinx("html", freshenv=True, testroot="fork-failed")
def test_os_fork_negative(monkeypatch: MonkeyPatch, app_params: Tuple[Dict, Dict], make_app: Callable):
    """Test."""
    monkeypatch.setattr("sphinx_multi_theme.utils.os.fork", lambda: -1)

    args, kwargs = app_params
    with pytest.raises(SphinxError) as exc:
        make_app(*args, **kwargs)
    assert exc.value.args[0] == "Fork failed (-1)"


@pytest.mark.parametrize("fail", [False, True])
@pytest.mark.usefixtures("skip_if_no_fork")
@pytest.mark.sphinx("html", freshenv=True, testroot="fork-failed")
def test_exit_code(app_params: Tuple[Dict, Dict], fail: bool):
    """Test."""
    srcdir: path = app_params[1]["srcdir"]
    outdir: path = srcdir / "_build" / str(fail) / "html"
    outdir.makedirs()
    cmd = [sys.executable, "-m", "sphinx", "-T", "-n", "-W", srcdir, outdir]

    # Run.
    if fail:
        env = dict(os.environ, TEST_EXIT_STATUS_CAUSE_EXC="TRUE")
        with pytest.raises(CalledProcessError) as exc:
            check_output(cmd, env=env, stderr=STDOUT)
        output = exc.value.output
    else:
        output = check_output(cmd, stderr=STDOUT)

    # Check.
    logs = output.decode("utf8").strip()
    lines = logs.splitlines()
    if fail:
        assert lines.count("Sphinx error:") == 2  # One in child logs another in the parent logs.
        assert lines.count("TEST_EXIT_STATUS_CAUSE_EXC") == 1  # Only in the child.
        assert len(re.findall(r"SphinxError: Child process \d+ failed with status 2$", logs, re.MULTILINE)) == 1  # Parent.
        assert not os.path.isfile(os.path.join(outdir, "index.html"))
    else:
        assert lines.count("Sphinx error:") == 0
        assert lines.count("TEST_EXIT_STATUS_CAUSE_EXC") == 0
        assert len(re.findall(r"SphinxError: Child process \d+ failed with status 2$", logs, re.MULTILINE)) == 0
        assert os.path.isfile(os.path.join(outdir, "index.html"))


@pytest.mark.usefixtures("skip_if_no_fork")
@pytest.mark.sphinx("html", freshenv=True, testroot="fork-failed")
def test_child_logs(app_params: Tuple[Dict, Dict]):
    """Test."""
    srcdir: path = app_params[1]["srcdir"]
    outdir: path = srcdir / "_build" / "html"
    cmd = [sys.executable, "-m", "sphinx", "-T", "-n", "-W", srcdir, outdir]

    # Run.
    env = dict(os.environ, TEST_ENV_UPDATED_CAUSE_EXC="TRUE")
    with pytest.raises(CalledProcessError) as exc:
        check_output(cmd, env=env, stderr=STDOUT)
    output = exc.value.output

    # Check.
    logs = output.decode("utf8").strip()
    assert "SphinxError: TEST_ENV_UPDATED_CAUSE_EXC" in logs
