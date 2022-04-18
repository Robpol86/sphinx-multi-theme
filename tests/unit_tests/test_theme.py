"""Tests."""
import pickle

import pytest

from sphinx_multi_theme.theme import Theme


def test():
    """Test."""
    theme = Theme("name")
    assert theme.name == "name"
    assert theme.display_name == ""
    assert theme.subdir == ""
    assert theme.is_active is False
    assert theme.is_primary is True

    theme.is_active = True
    assert theme.is_active is True

    theme = Theme("name", "Name", "subdir")
    assert theme.name == "name"
    assert theme.display_name == "Name"
    assert theme.subdir == "subdir"
    assert theme.is_active is False
    assert theme.is_primary is False

    with pytest.raises(AttributeError):
        theme.is_primary = True  # noqa

    assert repr(theme) == "Theme(name='name', display_name='Name', subdir='subdir', is_active=False)"

    theme_pickled = pickle.loads(pickle.dumps(theme))
    assert repr(theme_pickled) == repr(theme)
    assert theme_pickled == theme
