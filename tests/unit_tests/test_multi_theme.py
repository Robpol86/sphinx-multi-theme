"""Tests."""
import pickle

import pytest
from sphinx.errors import SphinxError

from sphinx_multi_theme.theme import MultiTheme, Theme


def test():
    """Test."""
    with pytest.raises(IndexError):
        MultiTheme([])

    themes = MultiTheme(["a", "b", "c"])
    assert len(themes) == 3

    themes_pickled = pickle.loads(pickle.dumps(themes))
    assert themes_pickled == themes


def test_compare():
    """Test."""
    this = MultiTheme(["a", "b", "c"])
    that = MultiTheme(["a", "b", "c"])
    assert this == that
    assert that == this

    this[0].subdir = "changed"
    assert this != that
    assert that != this
    that[0].subdir = "changed"
    assert this == that
    assert that == this

    assert MultiTheme(["a", "b", "c"]) != MultiTheme(["b", "a", "c"])
    assert MultiTheme(["b", "a", "c"]) != MultiTheme(["a", "b", "c"])

    assert this != "string"
    assert "string" != this


def test_as_list_and_dict():
    """Test."""
    themes = MultiTheme(["a", "b", "c"])

    # Act as a list.
    assert themes[0].name == "a"
    assert themes[1].name == "b"
    assert themes[2].name == "c"
    results = []
    for theme in themes:
        results.append(theme.name)
    assert results == ["a", "b", "c"]

    # Act as a dict.
    assert themes["a"].name == "a"
    assert themes["b"].name == "b"
    assert themes["c"].name == "c"
    results = []
    for key, theme in themes.items():
        results.append((key, theme.name))
    assert results == [("a", "a"), ("b", "b"), ("c", "c")]


def test_active():
    """Test."""
    themes = MultiTheme(["a", "b", "c"])

    assert themes[0].is_active is True
    assert themes[1].is_active is False
    assert themes[2].is_active is False
    assert themes.active.name == "a"

    themes.set_active(0)
    assert themes[0].is_active is True
    assert themes[1].is_active is False
    assert themes[2].is_active is False
    assert themes.active.name == "a"

    themes.set_active(1)
    assert themes[0].is_active is False
    assert themes[1].is_active is True
    assert themes[2].is_active is False
    assert themes.active.name == "b"

    themes.set_active(2)
    assert themes[0].is_active is False
    assert themes[1].is_active is False
    assert themes[2].is_active is True
    assert themes.active.name == "c"

    with pytest.raises(IndexError):
        themes.set_active(3)


def test_primary():
    """Test."""
    themes = MultiTheme(["a", "b", "c"])

    assert themes[0].is_primary is True
    assert themes[1].is_primary is False
    assert themes[2].is_primary is False
    assert themes.primary.name == "a"


def test_subdir_attrs():
    """Test."""
    themes = MultiTheme(["a", "b", "c"])
    assert themes[0].subdir == ""
    assert themes[1].subdir == "theme_b"
    assert themes[2].subdir == "theme_c"

    themes = MultiTheme(["a", "b", "b"])
    assert themes[0].subdir == ""
    assert themes[1].subdir == "theme_b"
    assert themes[2].subdir == "theme_b2"

    themes = MultiTheme(["a", "a", "a", "a"])
    assert themes[0].subdir == ""
    assert themes[1].subdir == "theme_a"
    assert themes[2].subdir == "theme_a2"
    assert themes[3].subdir == "theme_a3"

    themes = MultiTheme(["a"])
    assert themes[0].subdir == ""

    themes = MultiTheme([Theme("a"), Theme("b", subdir="my_subdir")])
    assert themes[0].subdir == ""
    assert themes[1].subdir == "my_subdir"

    themes = MultiTheme(["a", Theme("b", subdir="theme_c"), "c"])
    assert themes[0].subdir == ""
    assert themes[1].subdir == "theme_c"
    assert themes[2].subdir == "theme_c2"

    with pytest.raises(SphinxError) as exc:
        MultiTheme([Theme("a", subdir="my_subdir")])
    assert exc.value.args[0] == "Primary theme cannot have a subdir"

    with pytest.raises(SphinxError) as exc:
        MultiTheme(["a", Theme("b", subdir="my_subdir"), Theme("c", subdir="my_subdir")])
    first = "Theme(name='b', display_name='', subdir='my_subdir', is_active=False)"
    second = "Theme(name='c', display_name='', subdir='my_subdir', is_active=False)"
    assert exc.value.args[0] == f"Subdir collision: {first} and {second}"


def test_truncate():
    """Test."""
    themes = MultiTheme(["a", "b", "c"])

    removed = themes.truncate()
    assert len(themes) == 1
    assert themes[0].name == "a"
    assert len(removed) == 2
    assert removed[0].name == "b"
    assert removed[1].name == "c"

    assert themes.truncate() == []  # pylint: disable=use-implicit-booleaness-not-comparison
    assert len(themes) == 1
    assert themes[0].name == "a"
    assert len(removed) == 2
    assert removed[0].name == "b"
    assert removed[1].name == "c"
