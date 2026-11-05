"""Tests for ``PhotoshopApp.open_document``.

``photoshop.Session(action="open")`` only runs its action when the session is
entered with ``with``. Constructing it directly opened nothing, so the adapter
closed the current document and returned whatever was active instead of the
requested file.
"""

from photoshop_mcp_server.ps_adapter import application
from photoshop_mcp_server.ps_adapter.application import PhotoshopApp


class _FakeComApp:
    """COM stand-in that records ``open`` calls."""

    def __init__(self):
        self.opened = []

    def open(self, file_path):
        self.opened.append(file_path)
        return f"document:{file_path}"


def _adapter(com_app, session=None):
    app = PhotoshopApp.__new__(PhotoshopApp)
    app.app = com_app
    if session is not None:
        app.session = session
    return app


class _FakeSession:
    def __init__(self):
        self.active_document = _FakeDocument()


class _FakeDocument:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


def test_open_document_opens_the_requested_file():
    """The requested path is passed to ``Application.open`` and returned."""
    com_app = _FakeComApp()

    result = _adapter(com_app).open_document("C:/images/photo.psd")

    assert com_app.opened == ["C:/images/photo.psd"]
    assert result == "document:C:/images/photo.psd"


def test_open_document_with_session_does_not_close_the_active_document(monkeypatch):
    """An existing session is left alone and no new Session is constructed."""

    def _no_session(*args, **kwargs):
        raise AssertionError("Session must not be constructed by open_document")

    monkeypatch.setattr(application, "Session", _no_session)
    com_app = _FakeComApp()
    session = _FakeSession()

    result = _adapter(com_app, session=session).open_document("C:/images/photo.psd")

    assert com_app.opened == ["C:/images/photo.psd"]
    assert result == "document:C:/images/photo.psd"
    assert session.active_document.closed is False
