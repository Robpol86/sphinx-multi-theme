"""Tests."""
from pathlib import Path

from sphinx_multi_theme.utils import determine_new_doctreedir


def test(tmp_path: Path):
    """Test Sphinx default (doctreedir in $outdir/.doctrees)."""
    old_outdir = tmp_path / "html"
    new_outdir = tmp_path / "html" / "theme_test"
    old_doctreedir = old_outdir / ".doctrees"

    new_doctreedir, is_external = determine_new_doctreedir(old_doctreedir, old_outdir, new_outdir)
    assert new_doctreedir == new_outdir / ".doctrees"
    assert is_external is False


def test_deep(tmp_path: Path):
    """Test doctreedir deeper within the outdir."""
    old_outdir = tmp_path / "html"
    new_outdir = tmp_path / "html" / "theme_test"
    old_doctreedir = old_outdir / "a" / "b" / ".doctrees"

    new_doctreedir, is_external = determine_new_doctreedir(old_doctreedir, old_outdir, new_outdir)
    assert new_doctreedir == new_outdir / "a" / "b" / ".doctrees"
    assert is_external is False


def test_external(tmp_path: Path):
    """Test doctreedir outside the outdir."""
    old_outdir = tmp_path / "a" / "html"
    new_outdir = tmp_path / "a" / "html" / "theme_test"
    old_doctreedir = tmp_path / "b" / "doctrees"

    new_doctreedir, is_external = determine_new_doctreedir(old_doctreedir, old_outdir, new_outdir)
    assert new_doctreedir == tmp_path / "b" / "doctrees" / "theme_test"
    assert is_external is True
