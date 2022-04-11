"""Tests."""
from pathlib import Path

import pytest


@pytest.mark.sphinx("html", freshenv=True, testroot="html-context")
def test(outdir: Path):
    """Test."""
    assert (outdir / "index.html").is_file()
