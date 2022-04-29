# sphinx-multi-theme

[![Github-CI][github-ci]][github-link]
[![Coverage Status][codecov-badge]][codecov-link]
[![Documentation Status][rtd-badge]][rtd-link]
[![Code style: black][black-badge]][black-link]
[![PyPI][pypi-badge]][pypi-link]

[github-ci]: https://github.com/Robpol86/sphinx-multi-theme/actions/workflows/ci.yml/badge.svg?branch=main
[github-link]: https://github.com/Robpol86/sphinx-multi-theme/actions/workflows/ci.yml
[codecov-badge]: https://codecov.io/gh/Robpol86/sphinx-multi-theme/branch/main/graph/badge.svg
[codecov-link]: https://codecov.io/gh/Robpol86/sphinx-multi-theme
[rtd-badge]: https://readthedocs.org/projects/sphinx-multi-theme/badge/?version=latest
[rtd-link]: https://sphinx-multi-theme.readthedocs.io/en/latest/?badge=latest
[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[black-link]: https://github.com/ambv/black
[pypi-badge]: https://img.shields.io/pypi/v/sphinx-multi-theme.svg
[pypi-link]: https://pypi.org/project/sphinx-multi-theme

A Sphinx extension that builds copies of your docs using multiple themes into separate subdirectories.

📖 See the documentation at https://sphinx-multi-theme.readthedocs.io

## Install

Requires Python 3.6 or greater and Sphinx 4.0 or greater. Not supported on Windows.

```shell
pip install sphinx-multi-theme
```

## Example

```python
# conf.py
from sphinx_multi_theme.theme import MultiTheme, Theme

extensions = [
    "sphinx_multi_theme.multi_theme",
]

html_theme = MultiTheme(
    [
        Theme("sphinx_rtd_theme", "Read the Docs"),
        Theme("alabaster", "Alabaster"),
        Theme("classic", "Classic"),
    ]
)
```

```rst
===============
An RST Document
===============

.. multi-theme-toctree::
    :caption: Example Themes

```
