"""Theme and MultiTheme classes that can be directly used in conf.py."""
from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Tuple, Union

from sphinx.errors import SphinxError


@dataclass
class Theme:
    """A 'struct' representing one theme."""

    name: str  # e.g. "sphinx_rtd_theme"
    display_name: str = ""  # Pretty name shown in the toctree, e.g. "Read the Docs"
    subdir: str = ""  # Subdirectory basename including prefix, e.g. "theme_rtd"
    is_active: bool = field(default=False, init=False)  # If this is the current theme Sphinx is building in this process.

    @property
    def is_primary(self) -> bool:
        """Theme is considered the primary theme if it has no subdir specified."""
        return not self.subdir


class MultiTheme:
    """Builds copies documentation using multiple themes.

    The first theme is considered the primary theme whilst remaining themes are considered secondary and will be built into
    subdirectories.
    """

    DIRECTORY_PREFIX = "theme_"

    def __init__(self, themes: List[Union[str, Theme]]):
        """Constructor.

        :param themes: List of theme names as strings (e.g. ["classic"] or list of Theme instances (e.g. [Theme("classic")]).
        """
        themes_ = []
        for theme in themes:
            themes_.append(theme if hasattr(theme, "subdir") else Theme(theme))
        self.themes = themes_
        self.set_active(0)
        self.set_subdir_attrs()

    def __len__(self) -> int:
        """Return length of self.themes."""
        return len(self.themes)

    def __getitem__(self, item) -> Theme:
        """Allows class to act as a dict or a list."""
        try:
            return self.themes[item]
        except TypeError:
            return {t.name: t for t in self.themes}[item]

    def __iter__(self) -> Iterator[Theme]:
        """Yield themes."""
        yield from self.themes

    def __eq__(self, other):
        """Compare."""
        # https://stackoverflow.com/questions/390250/elegant-ways-to-support-equivalence-equality-in-python-classes
        if type(other) is type(self):
            return other.themes == self.themes
        return NotImplemented

    def items(self) -> Iterator[Tuple[str, Theme]]:
        """Yield name and theme pairs."""
        for theme in self.themes:
            yield theme.name, theme

    def set_active(self, idx: int) -> Theme:
        """Set theme at specific index as active and set all other themes as inactive.

        :return: The active theme.
        """
        active_theme = self.themes[idx]
        active_theme.is_active = True
        for idx2, theme in enumerate(self.themes):
            if idx == idx2:
                continue
            theme.is_active = False
        return active_theme

    @property
    def active(self) -> Theme:
        """Return the active theme."""
        themes = [t for t in self.themes if t.is_active]
        return themes[0]

    @property
    def primary(self) -> Theme:
        """Return the primary theme."""
        themes = [t for t in self.themes if t.is_primary]
        return themes[0]

    def truncate(self) -> List[Theme]:
        """Remove all secondary themes, only keep the primary theme."""
        removed_themes = self.themes[1:]
        self.themes[:] = self.themes[:1]
        return removed_themes

    def set_subdir_attrs(self):
        """Set subdir attribute for every theme except the first one."""
        primary_theme = self.themes[0]
        if primary_theme.subdir:
            raise SphinxError("Primary theme cannot have a subdir")

        secondary_themes = self.themes[1:]
        visited: Dict[str, Theme] = {}
        for theme in secondary_themes:
            if theme.subdir:
                # User specified custom subdir.
                if theme.subdir in visited:
                    raise SphinxError(f"Subdir collision: {visited[theme.subdir]} and {theme}")
            else:
                subdir = f"{self.DIRECTORY_PREFIX}{theme.name}"
                if subdir in visited:
                    i = 2
                    while f"{subdir}{i}" in visited:
                        i += 1
                    subdir = f"{subdir}{i}"
                theme.subdir = subdir
            visited[theme.subdir] = theme
