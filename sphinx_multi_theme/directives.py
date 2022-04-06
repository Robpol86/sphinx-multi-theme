"""Sphinx directives."""
from typing import List, Optional, Tuple

from docutils.nodes import bullet_list, Element, list_item, paragraph, reference
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective

from sphinx_multi_theme.theme import MultiTheme, Theme
from sphinx_multi_theme.utils import CONFIG_NAME_INTERNAL_THEMES


class MultiThemeListDirective(SphinxDirective):
    """Sphinx directive that lists and links to the same page in other themes' builds."""

    has_content = False

    def get_multi_theme(self) -> Optional[MultiTheme]:
        """Get the MultiTheme instance."""
        config = self.config
        if CONFIG_NAME_INTERNAL_THEMES in config:
            multi_theme = config[CONFIG_NAME_INTERNAL_THEMES]
            if multi_theme:
                return multi_theme
        log = logging.getLogger(__file__)
        log.warning("Extension not fully initialized: %r not in Sphinx config", CONFIG_NAME_INTERNAL_THEMES)
        return None

    def gen_links(self, themes: List[Theme], active_is_primary: bool) -> List[Tuple[str, str, bool]]:
        """Build a list of theme links.

        If the active theme is also the primary theme then all other themes are in subdirectories relative to the former.
        Otherwise all other themes are up one directory.

        :param themes: List of themes to parse.
        :param active_is_primary: If the current active theme is the primary theme.

        :return: List of: link text, link URI, and if the URI is an internal docname.
        """
        docname = self.env.docname
        entries = []

        for theme in themes:
            if theme.is_active:
                internal = True
                ref = f"{docname}.html"  # TODO was: ref = docname
            else:
                internal = False
                if active_is_primary:
                    ref = f"{theme.subdir}/{docname}.html"
                elif theme.is_primary:
                    ref = f"../{docname}.html"
                else:
                    ref = f"../{theme.subdir}/{docname}.html"
            entries.append((theme.name, ref, internal))

        return entries

    def run(self) -> List[Element]:
        """Main."""
        multi_theme = self.get_multi_theme()
        if not multi_theme:
            return []
        if len(multi_theme.themes) < 2:
            return []

        bullets = bullet_list(bullet="*")
        for text, ref, internal in self.gen_links(multi_theme.themes, multi_theme.active == multi_theme.primary):
            bullet = list_item()
            para = paragraph()
            para += reference(text=text, refuri=ref, internal=internal)
            bullet += para
            bullets.append(bullet)
        return [bullets]
