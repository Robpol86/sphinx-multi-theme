"""Tests."""
import pytest

from sphinx_multi_theme.multi_theme import Theme


def test():
    """Test."""
    theme = Theme("name")
    assert theme.name == "name"
    assert theme.subdir == ""
    assert theme.is_active is False
    assert theme.is_primary is True

    theme.is_active = True
    assert theme.is_active is True

    theme = Theme("name", "subdir")
    assert theme.name == "name"
    assert theme.subdir == "subdir"
    assert theme.is_active is False
    assert theme.is_primary is False

    with pytest.raises(AttributeError):
        theme.is_primary = True  # noqa

    assert repr(theme) == "Theme(name='name', subdir='subdir', is_active=False)"
