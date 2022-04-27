"""Tests."""
from io import StringIO
from pathlib import Path
from typing import List, Tuple

import pytest
from bs4 import BeautifulSoup, Tag


class HTML:
    """Parse all HTML files."""

    def __init__(self, outdir: Path):
        """Constructor."""
        self.outdir = outdir
        self.primary_index = self.parse("index.html")
        self.primary_other = self.parse("other.html")
        self.primary_sub = self.parse("sub", "page.html")
        self.secondary_index = self.parse("theme_secondary", "index.html")
        self.secondary_other = self.parse("theme_secondary", "other.html")
        self.secondary_sub = self.parse("theme_secondary", "sub", "page.html")

    def parse(self, *path: str) -> BeautifulSoup:
        """Parse HTML for a file."""
        file_ = self.outdir / Path(*path)
        text = file_.read_text(encoding="utf8")
        return BeautifulSoup(text, "html.parser")

    @property
    def wrapper_p(self) -> Tag:
        """Return toctree-wrapper (not in the sidebar) for the primary theme."""
        wrapper = self.primary_index.find_all("div", ["toctree-wrapper"])[1]
        assert wrapper.find_next("span").text == "MultiTheme"
        return wrapper

    @property
    def wrapper_s(self) -> Tag:
        """Return toctree-wrapper (not in the sidebar) for the secondary theme."""
        wrapper = self.secondary_index.find_all("div", ["toctree-wrapper"])[1]
        assert wrapper.find_next("span").text == "MultiTheme"
        return wrapper

    def directive_links(self) -> Tuple[List[BeautifulSoup], ...]:
        """Return a_hrefs from the directive output (not the sidebar) of both index.html files."""
        a_hrefs_p, a_hrefs_s = self.wrapper_p.find_all("a"), self.wrapper_s.find_all("a")
        assert len(a_hrefs_p) == 2
        assert len(a_hrefs_s) == 2
        assert a_hrefs_p[0].text == "Primary"
        assert a_hrefs_p[1].text == "Secondary"
        assert a_hrefs_s[0].text == "Primary"
        assert a_hrefs_s[1].text == "Secondary"
        return a_hrefs_p, a_hrefs_s

    def node_links(self, primary: bool) -> Tuple[List[BeautifulSoup], ...]:
        """Return a_hrefs from node outputs of all three HTML files in one theme."""
        page_index = self.primary_index.select("nav ul")[1] if primary else self.secondary_index.select("nav ul")[1]
        page_other = self.primary_other.select("nav ul")[1] if primary else self.secondary_other.select("nav ul")[1]
        page_sub = self.primary_sub.select("nav ul")[1] if primary else self.secondary_sub.select("nav ul")[1]
        a_hrefs_all = tuple(p.find_all("a") for p in (page_index, page_other, page_sub))
        for a_hrefs in a_hrefs_all:
            assert len(a_hrefs) == 2
            assert a_hrefs[0].text == "Primary"
            assert a_hrefs[1].text == "Secondary"
        return a_hrefs_all


@pytest.fixture(name="html")
def _html(outdir: Path) -> HTML:
    """Parse all HTML files."""
    return HTML(outdir)


@pytest.mark.usefixtures("skip_if_no_fork")
@pytest.mark.sphinx("html", freshenv=True, testroot="toctree-directive/links")
def test_links(html: HTML):
    """Test."""
    # Directive outputs.
    links_primary, links_secondary = html.directive_links()
    assert links_primary[0]["href"] == "#"  # Self
    assert links_primary[1]["href"] == "theme_secondary/index.html"
    assert links_secondary[0]["href"] == "../index.html"
    assert links_secondary[1]["href"] == "#"  # Self

    # Node outputs in primary theme.
    links_index, links_other, links_sub = html.node_links(primary=True)

    assert links_index[0]["href"] == "#"
    assert "current" in links_index[0]["class"]
    assert links_index[1]["href"] == "theme_secondary/index.html"
    assert "current" not in links_index[1]["class"]

    assert links_other[0]["href"] == "#"
    assert "current" in links_other[0]["class"]
    assert links_other[1]["href"] == "theme_secondary/other.html"
    assert "current" not in links_other[1]["class"]

    assert links_sub[0]["href"] == "#"
    assert "current" in links_sub[0]["class"]
    assert links_sub[1]["href"] == "../theme_secondary/sub/page.html"
    assert "current" not in links_sub[1]["class"]

    # Node outputs in secondary theme.
    links_index, links_other, links_sub = html.node_links(primary=False)

    assert links_index[0]["href"] == "../index.html"
    assert "current" not in links_index[0]["class"]
    assert links_index[1]["href"] == "#"
    assert "current" in links_index[1]["class"]

    assert links_other[0]["href"] == "../other.html"
    assert "current" not in links_other[0]["class"]
    assert links_other[1]["href"] == "#"
    assert "current" in links_other[1]["class"]

    assert links_sub[0]["href"] == "../../sub/page.html"
    assert "current" not in links_sub[0]["class"]
    assert links_sub[1]["href"] == "#"
    assert "current" in links_sub[1]["class"]


@pytest.mark.usefixtures("skip_if_no_fork")
@pytest.mark.sphinx("html", freshenv=True, testroot="toctree-directive/reversed")
def test_reversed(html: HTML):
    """Test."""
    a_hrefs_p = html.wrapper_p.find_all("a")
    a_hrefs_s = html.wrapper_s.find_all("a")

    assert a_hrefs_p[0].text == "Secondary"
    assert a_hrefs_p[1].text == "Primary"
    assert a_hrefs_s[0].text == "Secondary"
    assert a_hrefs_s[1].text == "Primary"

    assert a_hrefs_p[0]["href"] == "theme_secondary/index.html"
    assert a_hrefs_p[1]["href"] == "#"
    assert a_hrefs_s[0]["href"] == "#"
    assert a_hrefs_s[1]["href"] == "../index.html"


@pytest.mark.usefixtures("sphinx_app")
@pytest.mark.sphinx("html", freshenv=True, testroot="toctree-directive/incomplete")
def test_incomplete(warning: StringIO):
    """Test."""
    warnings = warning.getvalue().strip()
    assert "Sphinx config value for `html_theme` not a MultiTheme instance" in warnings
    assert "Extension not fully initialized: no multi-themes specified" in warnings
