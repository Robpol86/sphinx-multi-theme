"""Tests."""
import os
import re
import shutil
import sys
from io import StringIO
from pathlib import Path
from subprocess import check_output, STDOUT
from typing import Dict, List, Optional, Tuple

import pytest
from bs4 import BeautifulSoup


@pytest.mark.usefixtures("skip_if_no_fork")
@pytest.mark.sphinx("html", freshenv=True, testroot="poly-theme")
def test(outdir: Path):
    """Test."""
    # Primary theme.
    for file_ in ("index.html", "other.html"):
        html = BeautifulSoup((outdir / file_).read_text(encoding="utf8"), "html.parser")
        stylesheets = [link["href"] for link in html.find_all("link", rel="stylesheet")]
        assert "_static/classic.css" in stylesheets

    # Secondary themes.
    for file_ in ("index.html", "other.html"):
        for theme in ("traditional", "alabaster"):
            html = BeautifulSoup((outdir / f"theme_{theme}" / file_).read_text(encoding="utf8"), "html.parser")
            stylesheets = [link["href"] for link in html.find_all("link", rel="stylesheet")]
            assert f"_static/{theme}.css" in stylesheets


@pytest.mark.usefixtures("skip_if_no_fork", "sphinx_app")
@pytest.mark.sphinx("html", freshenv=True, testroot="poly-theme")
def test_logs(status: StringIO):
    """Verify child logs are present."""
    logs = status.getvalue().strip()
    assert logs.count("Entering multi-theme build mode") == 1
    assert logs.count("Changing outdir from") == 2  # child
    assert logs.count("Child process completed") == 2  # child
    assert logs.count("Done with theme") == 2
    assert logs.count("Exiting multi-theme build mode") == 1

    # Test is_child flag.
    matches = re.findall(r"(\w+ multi-theme|^callback.+$)", logs, re.MULTILINE)
    expected = [
        "Entering multi-theme",
        "callback(): html_theme='traditional', is_child=True",
        "callback(): html_theme='alabaster', is_child=True",
        "Exiting multi-theme",
        "callback(): html_theme='classic', is_child=False",
    ]
    assert matches == expected


@pytest.mark.keep_srcdir
@pytest.mark.usefixtures("skip_if_no_fork")
@pytest.mark.parametrize("second_run", [False, True])
@pytest.mark.sphinx("epub", testroot="poly-theme")
def test_unsupported(outdir: Path, status: StringIO, second_run: bool):
    """Test."""
    # Primary theme.
    for file_ in ("index.xhtml", "other.xhtml"):
        path = outdir / file_
        assert path.exists()

    # Secondary themes.
    for theme in ("traditional", "alabaster"):
        path = outdir / f"theme_{theme}"
        leftover_file = path / "leftover_file.txt"
        if not second_run:
            assert not path.exists()
            path.mkdir()
            leftover_file.touch()
        else:
            assert leftover_file.exists()
            assert [f.name for f in path.iterdir()] == [leftover_file.name]

    logs = status.getvalue().strip()
    assert logs.count("Unsupported builder 'epub', terminating child process") == 2  # child
    assert logs.count("Unsupported builder 'epub', removing themes: ['traditional', 'alabaster']") == 1


@pytest.mark.usefixtures("skip_if_no_fork")
@pytest.mark.parametrize("relative_src", [False, True])
@pytest.mark.parametrize("relative_out", [False, True])
@pytest.mark.sphinx("html", freshenv=True, testroot="poly-theme")
def test_dir_change(tmp_path: Path, app_params: Tuple[Dict, Dict], relative_src: bool, relative_out: bool):
    """Test."""
    srcdir = Path(app_params[1]["srcdir"])
    outdir = srcdir / "_build" / "html"

    def run(doctreedir: Optional[Path] = None) -> List[str]:
        if outdir.exists():
            shutil.rmtree(outdir)
        if doctreedir and doctreedir.exists():
            shutil.rmtree(doctreedir)
        cmd = [sys.executable, "-m", "sphinx", "-T", "-n", "-W"]
        if doctreedir:
            cmd += ["-d", doctreedir]
        env = dict(os.environ, TEST_IN_SUBPROCESS="TRUE")
        cmd += ["." if relative_src else srcdir, outdir.relative_to(srcdir) if relative_out else outdir]
        output = check_output(cmd, env=env, stderr=STDOUT, cwd=srcdir)
        logs = output.decode("utf8").strip()
        return logs.splitlines()

    # Immediate parent (no -d).
    lines = run()
    assert "🍴 Changing outdir from '_build/html' to '_build/html/theme_alabaster'" in lines
    assert "🍴 Changing doctreedir from '_build/html/.doctrees' to '_build/html/theme_alabaster/.doctrees'" in lines

    # Deep parent (-d outdir/a/b/doctrees).
    lines = run(outdir / "a" / "b" / "doctrees")
    assert "🍴 Changing outdir from '_build/html' to '_build/html/theme_alabaster'" in lines
    assert "🍴 Changing doctreedir from '_build/html/a/b/doctrees' to '_build/html/theme_alabaster/a/b/doctrees'" in lines

    # External (-d tmp_path/x/y/doctrees).
    lines = run(tmp_path / "x" / "y" / "doctrees")
    assert "🍴 Changing outdir from '_build/html' to '_build/html/theme_alabaster'" in lines
    assert "🍴 Changing doctreedir from 'x/y/doctrees' to 'x/y/doctrees/theme_alabaster'" in lines
