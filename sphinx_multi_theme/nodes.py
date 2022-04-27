"""Docutils nodes."""
from typing import Optional

from sphinx import addnodes


class MultiThemeTocTreeNode(addnodes.toctree):
    """TocTree node for MultiThemeTocTreeDirective."""

    def __init__(self, *args, **kwargs):
        """Initialize position counter."""
        super().__init__(*args, **kwargs)
        self.ref_prefixes_pos = 0

    @property
    def docname(self) -> str:
        """Get the current Sphinx document name (e.g. "index")."""
        env = self.document.settings.env  # noqa
        return getattr(env.app.builder, "current_docname", None) or self.attributes["parent"]

    def get_ref(self, key) -> Optional[str]:
        """Return the relative link to a theme or an empty string if key out of scope."""
        if "ref_prefixes" not in self.attributes:
            return None
        if key != "parent":
            if key == "entries":
                # Reset position.
                self.ref_prefixes_pos = 0
            return None

        ref_prefixes = self.attributes["ref_prefixes"]
        ref_prefix: str = ref_prefixes[self.ref_prefixes_pos]
        self.ref_prefixes_pos += 1

        return self.docname if not ref_prefix else f"{ref_prefix}/{self.docname}"

    def __getitem__(self, key):
        """Intercept call from TocTree adapter and return relative link to theme."""
        ref = self.get_ref(key)
        return super().__getitem__(key) if ref is None else ref

    def get(self, key, failobj=None):
        """Same as __getitem__()."""
        ref = self.get_ref(key)
        return super().get(key, failobj=failobj) if ref is None else ref
