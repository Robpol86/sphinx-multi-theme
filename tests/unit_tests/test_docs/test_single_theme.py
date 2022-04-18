"""Tests."""
import re
from filecmp import clear_cache, DEFAULT_IGNORES, dircmp
from io import StringIO
from pathlib import Path
from typing import Optional

import pytest
from _pytest.monkeypatch import MonkeyPatch
from sphinx.testing.util import SphinxTestApp

from sphinx_multi_theme.theme import MultiTheme
from sphinx_multi_theme.utils import CONFIG_NAME_INTERNAL_THEMES

EXPECTED_NUM_FILES = 23
IGNORE = DEFAULT_IGNORES + [".buildinfo"]
ROOTS = ("single-theme/off", "single-theme/on", "single-theme/incomplete", "single-theme/no-fork")


@pytest.fixture(autouse=True)
def mock_os_without_fork(monkeypatch: MonkeyPatch, tmp_path: Path):
    """Mock os without fork() attribute."""
    mock_os_file = tmp_path / "mock_os" / "mock_os.py"
    mock_os_file.parent.mkdir()
    mock_os_file.write_text("from os import *\ntry:\n  del fork\nexcept NameError:\n  pass")
    monkeypatch.syspath_prepend(mock_os_file.parent)
    monkeypatch.setattr("sphinx_multi_theme.multi_theme.os", __import__("mock_os"))


def directory_compare(left: Optional[Path] = None, right: Optional[Path] = None, compare: Optional[dircmp] = None) -> int:
    """Recursively compare two directories and their file contents.

    :return: Number of common files found recursively.
    """
    clear_cache()
    if not compare:
        compare = dircmp(left, right, ignore=IGNORE)

    # Verify no errors found by dircmp.
    assert not compare.funny_files
    assert not compare.common_funny

    # Verify all non-recursive files/directories in both directories are the same.
    assert not compare.left_only
    assert not compare.right_only
    assert not compare.diff_files

    # Verify file contents.
    file_count = 0
    for name in compare.same_files:
        left_file = Path(compare.left) / name
        right_file = Path(compare.right) / name
        assert left_file.read_bytes() == right_file.read_bytes()
        file_count += 1

    # Recurse.
    for common_sub_dir in compare.subdirs.values():
        file_count += directory_compare(compare=common_sub_dir)

    return file_count


@pytest.mark.keep_srcdir
@pytest.mark.parametrize(
    "testroot", [pytest.param(r, marks=pytest.mark.sphinx("html", freshenv=True, testroot=r)) for r in ROOTS]
)
def test(sphinx_app: SphinxTestApp, outdir: Path, warning: StringIO, testroot: str):
    """Verify single-theme is the same as not using this feature."""
    assert (outdir / "index.html").is_file()

    # Diff all files.
    parts = outdir.parts
    if testroot.endswith("on"):
        idx = parts.index("on")
    elif testroot.endswith("incomplete"):
        idx = parts.index("incomplete")
    elif testroot.endswith("no-fork"):
        idx = parts.index("no-fork")
    else:
        idx = None
    if idx is not None:
        outdir_off = Path(*(parts[:idx] + ("off",) + parts[idx + 1 :]))  # noqa
        assert directory_compare(outdir, outdir_off) == EXPECTED_NUM_FILES

    # Check warnings.
    warnings = warning.getvalue().strip()
    warnings_sans_colors = re.sub(r"\x1b\[[0-9;]+m", "", warnings)
    if testroot.endswith("incomplete"):
        assert warnings_sans_colors == "WARNING: 🍴 Sphinx config value for `html_theme` not a MultiTheme instance"
    elif testroot.endswith("no-fork"):
        assert warnings_sans_colors == "WARNING: 🍴 Platform does not support forking, removing themes: ['fake1', 'fake2']"
    else:
        assert not warnings

    # Check config.
    config = sphinx_app.config
    assert config.html_theme == "classic"
    if testroot.endswith("off"):
        assert CONFIG_NAME_INTERNAL_THEMES not in config
    else:
        config_multi_theme = config[CONFIG_NAME_INTERNAL_THEMES]
        if testroot.endswith("on") or testroot.endswith("no-fork"):
            assert isinstance(config_multi_theme, MultiTheme)
            assert config_multi_theme.active.name == "classic"
        else:
            assert config_multi_theme is None


def test_directory_compare(tmp_path: Path):
    """Sanity checks to verify function works as expected."""
    left = tmp_path / "left"
    right = tmp_path / "right"

    def run():
        return directory_compare(left, right)

    # Setup both directories identically.
    for path in (left, right):
        path.mkdir()
        path.joinpath("one.txt").write_text("One", encoding="utf8")
        path.joinpath("two.txt").write_text("Two", encoding="utf8")
        path.joinpath("three.txt").write_text("Three", encoding="utf8")
        sub_path = path / "sub"
        sub_path.mkdir()
        sub_path.joinpath("four.txt").write_text("Four", encoding="utf8")
    assert run() == 4

    # Extra file.
    for path in (left, right):
        path.joinpath("shoe.txt").write_text("Shoe", encoding="utf8")
        with pytest.raises(AssertionError):
            run()
        path.joinpath("shoe.txt").unlink()
        run()

    # Extra file in subdir.
    for path in (left, right):
        sub_path = path / "new"
        sub_path.mkdir()
        sub_path.joinpath("buckle.txt").write_text("Buckle", encoding="utf8")
        with pytest.raises(AssertionError):
            run()
        sub_path.joinpath("buckle.txt").unlink()
        with pytest.raises(AssertionError):
            run()  # Empty left over directory.
        sub_path.rmdir()
        run()

    # Different size file.
    for path in (left, right):
        file_ = path.joinpath("one.txt")
        file_.write_text("Cowabunga", encoding="utf8")
        with pytest.raises(AssertionError):
            run()
        file_.write_text("One", encoding="utf8")
        run()

    # Same size different contents in a file.
    for path in (left, right):
        file_ = path.joinpath("one.txt")
        old_size = file_.stat().st_size
        file_.write_text("ONE", encoding="utf8")
        assert file_.stat().st_size == old_size
        with pytest.raises(AssertionError):
            run()
        file_.write_text("One", encoding="utf8")
        run()
