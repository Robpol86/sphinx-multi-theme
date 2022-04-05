"""Tests."""
from pathlib import Path

import pytest
from bs4 import BeautifulSoup


@pytest.mark.sphinx("html", testroot="poly-theme")
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
