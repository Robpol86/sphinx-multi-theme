"""Tests."""
from _pytest.monkeypatch import MonkeyPatch

from sphinx_multi_theme.utils import terminate_forked_build


def test(monkeypatch: MonkeyPatch):
    """Test."""
    exit_status = []
    monkeypatch.setattr("sphinx_multi_theme.utils.os_exit", exit_status.append)
    mock_app = type("", (), {"emit": lambda *_: None})()

    terminate_forked_build(mock_app, None)
    assert exit_status == [0]

    exit_status.clear()
    terminate_forked_build(mock_app, RuntimeError())
    assert exit_status == [1]
