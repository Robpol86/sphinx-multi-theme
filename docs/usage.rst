.. _usage:

=====
Usage
=====

The way ``sphinx-multi-theme`` works is by specifying all the themes you want to build using the usual
`html_theme <https://www.sphinx-doc.org/en/master/usage/theming.html#using-a-theme>`_ option in your ``conf.py`` file, but
instead of a string you'll use the provided ``MultiTheme`` class. Forking happens on the
`config-inited <https://www.sphinx-doc.org/en/master/extdev/appapi.html#event-config-inited>`_ Sphinx event. Here is an
exmaple:

.. code-block:: python

    from sphinx_multi_theme.theme import MultiTheme, Theme

    extensions = [
        "sphinx_multi_theme.multi_theme",
    ]
    html_theme = MultiTheme(
        [
            Theme("alabaster", "Alabaster"),
            Theme("classic", "Classic"),
        ]
    )
    master_doc = "index"
    version = "1.2.3"

In this example the documentation will be built twice: the main theme will use the
`built-in <https://www.sphinx-doc.org/en/master/usage/theming.html#builtin-themes>`_ Alabaster theme, and the Classic theme
will be built in a subdirectory.

Linking to Themes
=================

You may use the ``multi-theme-toctree`` directive to link all themes with each other. This directive is based on the built-in
`toctree <https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-toctree>`_ directive, with
most of those options still available. This will let your users visit all themes and all themes will show up on the sidebar
(provided that the theme you're using has a sidebar). Here is an example ``index.rst`` or ``index.md``:

.. tabbed:: reStructuredText

    .. code-block:: rst

        ==========
        My Project
        ==========

        Hello World

        .. toctree::
            :caption: Pages

            document1
            document2

        .. multi-theme-toctree::
            :caption: Themes

.. tabbed:: MyST Markdown

    .. code-block:: md

        # My Project

        Hello World

        ```{toctree}
        :caption: Pages

        document1
        document2
        ```

        ```{multi-theme-toctree}
        :caption: Themes
        ```
