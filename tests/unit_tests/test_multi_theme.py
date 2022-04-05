"""Tests."""
import pytest
from sphinx.errors import SphinxError

from sphinx_multi_theme.multi_theme import MultiTheme, Theme


def test():
    """Test."""
    with pytest.raises(IndexError):
        MultiTheme([])

    themes = MultiTheme(["a", "b", "c"])
    assert len(themes) == 3


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

    themes = MultiTheme([Theme("a"), Theme("b", "my_subdir")])
    assert themes[0].subdir == ""
    assert themes[1].subdir == "my_subdir"

    themes = MultiTheme(["a", Theme("b", "theme_c"), "c"])
    assert themes[0].subdir == ""
    assert themes[1].subdir == "theme_c"
    assert themes[2].subdir == "theme_c2"

    with pytest.raises(SphinxError) as exc:
        MultiTheme([Theme("a", "my_subdir")])
    assert exc.value.args[0] == "Primary theme cannot have a subdir"

    with pytest.raises(SphinxError) as exc:
        MultiTheme(["a", Theme("b", "my_subdir"), Theme("c", "my_subdir")])
    first = "Theme(name='b', subdir='my_subdir', is_active=False)"
    second = "Theme(name='c', subdir='my_subdir', is_active=False)"
    assert exc.value.args[0] == f"Subdir collision: {first} and {second}"
