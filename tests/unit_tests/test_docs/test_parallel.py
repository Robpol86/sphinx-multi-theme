"""Tests."""
import sys
from pathlib import Path
from subprocess import check_output, STDOUT
from typing import Dict, Tuple

import pytest


@pytest.mark.usefixtures("skip_if_no_fork")
@pytest.mark.parametrize("parallel", [False, True])
@pytest.mark.sphinx("html", freshenv=True, testroot="parallel")
def test(app_params: Tuple[Dict, Dict], parallel: bool):
    """Test."""
    srcdir = Path(app_params[1]["srcdir"])
    outdir = srcdir / "_build" / "html"

    # Generate documents.
    with (srcdir / "index.rst").open("a", encoding="utf8") as index_rst:
        for idx in range(20):
            doc_rst = srcdir / f"doc{idx:03}.rst"
            doc_rst.write_text(f"""======\nDoc{idx:03}\n======\n\nGenerated page.""", encoding="utf8")
            index_rst.write(f"    doc{idx:03}\n")

    # Build.
    cmd = [sys.executable, "-m", "sphinx", "-T", "-n", "-W", srcdir, outdir]
    if parallel:
        cmd.insert(-2, "-j")
        cmd.insert(-2, "2")
    check_output(cmd, stderr=STDOUT, cwd=srcdir)
