"""Tests."""
from pathlib import Path

import pytest
from bs4 import BeautifulSoup


@pytest.mark.usefixtures("skip_if_no_fork")
@pytest.mark.sphinx("html", freshenv=True, testroot="duplicated-theme")
def test(outdir: Path):
    """Test."""
    # Primary theme.
    for file_ in ("index.html", "other.html"):
        html = BeautifulSoup((outdir / file_).read_text(encoding="utf8"), "html.parser")
        stylesheets = [link["href"] for link in html.find_all("link", rel="stylesheet")]
        assert "_static/classic.css" in stylesheets

    # Secondary themes.
    for file_ in ("index.html", "other.html"):
        for suffix in ("", "2", "3"):
            html = BeautifulSoup((outdir / f"theme_classic{suffix}" / file_).read_text(encoding="utf8"), "html.parser")
            stylesheets = [link["href"] for link in html.find_all("link", rel="stylesheet")]
            assert "_static/classic.css" in stylesheets
