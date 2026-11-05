"""Tests for JSON payloads that carry multi-line error messages.

Photoshop error messages often span several lines, for example
``General Photoshop error ...\\n- The command "Play" is not currently available.``
If such a message reaches a JSON payload with a raw line break, ``json.loads``
rejects the payload, ``_script_error_message`` cannot see ``success: false``
and the failure is reported to the caller as a successful script run.
"""

import json
import shutil
import subprocess

import pytest

from photoshop_mcp_server.ps_adapter.application import PhotoshopApp
from photoshop_mcp_server.tools import script_tools

MULTILINE_ERROR = 'General Photoshop error.\n- The command "Play" is not\tavailable.\r'


class _RaisingComApp:
    """COM stand-in whose ``doJavaScript`` always fails with a multi-line error."""

    def __init__(self, message):
        self._message = message

    def doJavaScript(self, script, arguments, execution_mode):
        raise RuntimeError(self._message)


class _RecordingComApp:
    """COM stand-in that records the script it receives."""

    def __init__(self):
        self.scripts = []

    def doJavaScript(self, script, arguments, execution_mode):
        self.scripts.append(script)
        return None


def _adapter(com_app):
    app = PhotoshopApp.__new__(PhotoshopApp)
    app.app = com_app
    return app


class TestAdapterErrorPayload:
    """Failure payloads built in Python are valid JSON for any message."""

    def test_multiline_com_error_is_valid_json(self):
        """A COM error with line breaks, tabs and quotes round-trips through JSON."""
        raw = _adapter(_RaisingComApp(MULTILINE_ERROR)).execute_javascript("x();")

        payload = json.loads(raw)
        assert payload == {"error": MULTILINE_ERROR, "success": False}

    def test_multiline_com_error_is_reported_as_failure(self):
        """``_script_error_message`` recognises the payload as a failure."""
        raw = _adapter(_RaisingComApp(MULTILINE_ERROR)).execute_javascript("x();")

        assert script_tools._script_error_message(raw) == MULTILINE_ERROR


@pytest.mark.skipif(
    shutil.which("node") is None, reason="needs node to run the polyfill"
)
class TestJsonPolyfill:
    """The injected ``JSON.stringify`` polyfill escapes control characters."""

    def _polyfill(self):
        com_app = _RecordingComApp()
        _adapter(com_app).execute_javascript("1;")
        return com_app.scripts[0].split("\n", 1)[0]

    def test_polyfill_output_parses_as_json(self):
        """Strings with line breaks, tabs and quotes stay valid JSON."""
        program = (
            "(function(){var JSON;"
            + self._polyfill()
            + "\nprocess.stdout.write(JSON.stringify({error: "
            + json.dumps(MULTILINE_ERROR)
            + ", success: false}));})();"
        )
        completed = subprocess.run(
            ["node", "-e", program],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            check=True,
        )

        assert json.loads(completed.stdout) == {
            "error": MULTILINE_ERROR,
            "success": False,
        }
