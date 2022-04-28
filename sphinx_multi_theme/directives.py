"""Sphinx directives."""
from typing import List, Optional, Tuple

import funcy
from docutils.nodes import Node
from sphinx import addnodes
from sphinx.directives import other
from sphinx.util import logging

from sphinx_multi_theme import utils
from sphinx_multi_theme.nodes import MultiThemeTocTreeNode
from sphinx_multi_theme.theme import MultiTheme


class MultiThemeTocTreeDirective(other.TocTree):
    """Sphinx toctree directive that lists all themes linking to the same document."""

    has_content = False
    option_spec = funcy.omit(other.TocTree.option_spec, ["glob", "maxdepth", "titlesonly"])
    NODE = MultiThemeTocTreeNode

    def run(self) -> List[Node]:
        """Directive entrypoint.

        Usually only called from index.rst and no other documents despite the sidebar being rendered in all documents on some
        Sphinx themes.
        """
        self.options["maxdepth"] = 1
        self.options["titlesonly"] = True
        return super().run()

    def parse_content(self, toctree: addnodes.toctree) -> List[Node]:
        """Called by super().run()."""
        log = logging.getLogger(__name__)

        # Get MultiTheme instance.
        multi_theme: Optional[MultiTheme] = self.config[utils.CONFIG_NAME_INTERNAL_THEMES]
        if not multi_theme:
            log.warning("Extension not fully initialized: no multi-themes specified")
            self.options["hidden"] = True
            return []
        if len(multi_theme.themes) < 2:
            self.options["hidden"] = True
            return []

        # Populate entries.
        entries: List[Tuple[str, str]] = toctree.setdefault("entries", [])
        ref_prefixes: List[str] = toctree.setdefault("ref_prefixes", [])
        active_is_primary = multi_theme.active == multi_theme.primary
        for theme in multi_theme.themes:
            if theme.is_active:
                ref_prefix = ""
            elif active_is_primary:
                ref_prefix = theme.subdir
            elif theme.is_primary:
                ref_prefix = ".."
            else:
                ref_prefix = f"../{theme.subdir}"
            text = theme.display_name or theme.name
            ref = "self"
            entries.append((text, ref))
            ref_prefixes.append(ref_prefix)

        # Implement reversed option.
        if "reversed" in self.options:
            for key in ("entries", "ref_prefixes"):
                toctree[key] = list(reversed(toctree[key]))

        # Replace the original toctree node with a custom one.
        new_toctree = self.NODE()
        new_toctree.update_all_atts(toctree, and_source=True)
        toctree.replace_self(new_toctree)

        return []
