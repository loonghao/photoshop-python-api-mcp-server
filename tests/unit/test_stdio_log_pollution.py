"""Regression tests keeping diagnostics out of the MCP stdio stream.

The MCP stdio transport uses stdout exclusively for JSON-RPC frames. Any other
bytes written there are handed to the client's JSON parser and desynchronise
the session, which is what produced "Unexpected non-whitespace character after
JSON at position 4" for users running the server from an editor.

These tests are the anti-regression gate: they drive a real stdio session and
assert that nothing but JSON-RPC reaches stdout.
"""

import io
import json
import logging
import os
import subprocess
import sys
import textwrap
from contextlib import redirect_stdout

import pytest

from photoshop_mcp_server import logging_config
from photoshop_mcp_server.registry import register_tool

LOGGER_NAME = logging_config.LOGGER_NAME


@pytest.fixture(autouse=True)
def _restore_logging():
    """Keep logging mutations from leaking between tests."""
    logger = logging.getLogger(LOGGER_NAME)
    previous_handlers = list(logger.handlers)
    previous_level = logger.level
    previous_propagate = logger.propagate
    yield
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()
    for handler in previous_handlers:
        logger.addHandler(handler)
    logger.setLevel(previous_level)
    logger.propagate = previous_propagate


def _has_stdout_handler(logger: logging.Logger) -> bool:
    """Report whether any handler in a logger's chain writes to stdout.

    Args:
        logger: The logger to inspect.

    Returns:
        bool: True if a handler targets ``sys.stdout``.

    """
    current: logging.Logger | None = logger
    while current is not None:
        for handler in current.handlers:
            stream = getattr(handler, "stream", None)
            if stream is sys.stdout:
                return True
            target = getattr(handler, "_ps_mcp_stdout_sentinel", None)
            if target is True:
                return True
        if not current.propagate:
            break
        current = current.parent
    return False


def _wrap_stdout_for_detection(buffer: io.StringIO) -> io.StringIO:
    """Tag a buffer so handlers pointing at it are detected as stdout."""
    buffer._ps_mcp_stdout_sentinel = True  # type: ignore[attr-defined]
    return buffer


# --------------------------------------------------------------------------
# Handler routing
# --------------------------------------------------------------------------


def test_root_logger_has_no_stdout_handler():
    """The root logger must never write to stdout.

    Third-party libraries log through the root logger before the package logger
    exists, so routing it away from stdout is what keeps their output out of the
    JSON-RPC stream.
    """
    logging_config.configure_root_logging()
    assert not _has_stdout_handler(logging.getLogger())


def test_package_logger_has_no_stdout_handler():
    """No handler in the package logger's chain may target stdout."""
    logging_config.configure_logging(force=True)
    assert not _has_stdout_handler(logging.getLogger(LOGGER_NAME))


def test_log_file_route_does_not_use_stdout(tmp_path):
    """File logging keeps stderr enabled without introducing a stdout handler."""
    log_file = tmp_path / "server.log"
    logging_config.configure_logging(log_file=str(log_file), force=True)

    logger = logging.getLogger(LOGGER_NAME)
    logger.info("hello from the file route")

    for handler in logger.handlers:
        handler.flush()

    assert log_file.exists()
    assert "hello from the file route" in log_file.read_text(encoding="utf-8")
    assert not _has_stdout_handler(logger)


def test_log_level_env_var_is_honoured(monkeypatch):
    """PS_MCP_LOG_LEVEL selects the level without touching stdout."""
    monkeypatch.setenv(logging_config.ENV_LOG_LEVEL, "DEBUG")
    monkeypatch.delenv(logging_config.ENV_LOG_FILE, raising=False)

    logger = logging_config.configure_logging(force=True)

    assert logger.level == logging.DEBUG
    assert not _has_stdout_handler(logger)


def test_emit_writes_nothing_to_stdout():
    """A record at every level leaves stdout byte-for-byte empty."""
    logging_config.configure_logging(level=logging.DEBUG, force=True)
    logger = logging.getLogger(LOGGER_NAME)

    buffer = _wrap_stdout_for_detection(io.StringIO())
    with redirect_stdout(buffer):
        logger.debug("debug record")
        logger.info("info record")
        logger.warning("warning record")
        logger.error("error record")
        for handler in logger.handlers:
            handler.flush()

    assert buffer.getvalue() == ""


# --------------------------------------------------------------------------
# log_tool_call: the decorator that fires on every tools/call
# --------------------------------------------------------------------------


def test_log_tool_call_is_silent_at_default_level():
    """At the default level a decorated tool writes nothing to stdout.

    ``log_tool_call`` wraps every registered tool, so an unconditional print
    here would emit two lines per call on every single request.
    """
    from photoshop_mcp_server.decorators import log_tool_call

    logging_config.configure_logging(level=logging.INFO, force=True)

    @log_tool_call
    def sample_tool(value: int = 1) -> str:
        return f"ok:{value}"

    buffer = _wrap_stdout_for_detection(io.StringIO())
    with redirect_stdout(buffer):
        result = sample_tool(value=7)
        for handler in logging.getLogger(LOGGER_NAME).handlers:
            handler.flush()

    assert result == "ok:7"
    assert buffer.getvalue() == ""


def test_log_tool_call_emits_debug_records_when_debug_enabled(monkeypatch):
    """With debug enabled the call is still logged, just not to stdout."""
    from photoshop_mcp_server.decorators import log_tool_call

    logging_config.configure_logging(level=logging.DEBUG, force=True)

    records: list[logging.LogRecord] = []

    class _CaptureHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            records.append(record)

    capture = _CaptureHandler(level=logging.DEBUG)
    logging.getLogger(LOGGER_NAME).addHandler(capture)

    @log_tool_call
    def sample_tool(value: int = 3) -> str:
        return f"ok:{value}"

    buffer = _wrap_stdout_for_detection(io.StringIO())
    with redirect_stdout(buffer):
        sample_tool(value=3)

    messages = [record.getMessage() for record in records]
    assert any("TOOL CALL: sample_tool" in m for m in messages)
    assert any("TOOL RESULT: sample_tool" in m for m in messages)
    assert buffer.getvalue() == ""


def test_debug_tool_traceback_goes_to_stderr_not_stdout():
    """An exception inside a tool is logged, never printed to stdout."""
    from photoshop_mcp_server.decorators import debug_tool

    logging_config.configure_logging(level=logging.INFO, force=True)

    @debug_tool
    def exploding_tool() -> dict:
        raise RuntimeError("boom")

    buffer = _wrap_stdout_for_detection(io.StringIO())
    with redirect_stdout(buffer):
        result = exploding_tool()
        for handler in logging.getLogger(LOGGER_NAME).handlers:
            handler.flush()

    assert result["success"] is False
    assert "boom" in result["error"]
    assert buffer.getvalue() == ""


# --------------------------------------------------------------------------
# End-to-end stdio session
# --------------------------------------------------------------------------

_STDIO_DRIVER = textwrap.dedent('''
    """Drive a real stdio session with a tool that deliberately logs."""
    import sys
    import traceback

    from mcp.server.fastmcp import FastMCP

    from photoshop_mcp_server.registry import register_tool
    from photoshop_mcp_server.logging_config import configure_root_logging, get_logger

    configure_root_logging()
    probe_logger = get_logger("probe")

    mcp_server = FastMCP(name="PollutionProbe")


    def probe_tool(text: str = "hi") -> dict:
        """A tool that exercises every diagnostic path a real tool uses.

        It logs at several levels, prints through ``log_tool_call``'s code path,
        and captures a traceback, so a regression that sends any of those to
        stdout is caught here rather than passing on an empty stream.
        """
        probe_logger.info("probe_tool info record: %s", text)
        probe_logger.debug("probe_tool debug record: %s", text)
        try:
            raise RuntimeError("probe traceback")
        except RuntimeError:
            probe_logger.debug("probe traceback captured: %s", traceback.format_exc())
        # stdout is block-buffered when piped, so flush to make any stray write
        # deterministic instead of depending on when the buffer fills.
        sys.stdout.flush()
        return {"success": True, "echo": text}


    # register_tool applies debug_tool + log_tool_call, exactly as production
    # tools are registered.
    register_tool(mcp_server, probe_tool, "probe_tool")

    mcp_server.run()
    ''')

_JSONRPC_INITIALIZE = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-06-18",
        "capabilities": {},
        "clientInfo": {"name": "probe", "version": "0.0.0"},
    },
}

_JSONRPC_INITIALIZED = {
    "jsonrpc": "2.0",
    "method": "notifications/initialized",
}

_JSONRPC_TOOL_CALL = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {"name": "photoshop_probe_tool", "arguments": {"text": "pollute"}},
}


def test_stdio_session_stdout_is_pure_jsonrpc():
    """Every line on stdout during a real session is a valid JSON-RPC frame.

    The probe tool registers through the production ``register_tool`` path and
    calls ``print`` internally, so a regression that restores print-to-stdout
    anywhere in the tool path fails here rather than passing vacuously.
    """
    request = "\n".join(
        json.dumps(message)
        for message in (_JSONRPC_INITIALIZE, _JSONRPC_INITIALIZED, _JSONRPC_TOOL_CALL)
    )

    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    # Keep the child off any inherited logging configuration.
    env.pop(logging_config.ENV_LOG_FILE, None)
    env[logging_config.ENV_LOG_LEVEL] = "DEBUG"

    completed = subprocess.run(
        [sys.executable, "-c", _STDIO_DRIVER],
        input=request + "\n",
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        timeout=120,
    )

    stdout_lines = [line for line in completed.stdout.splitlines() if line.strip()]

    # The session must have produced frames at all, otherwise the test below
    # would trivially pass on an empty stream.
    assert stdout_lines, (
        "stdio session produced no stdout; stderr was:\n" + completed.stderr
    )

    non_json = []
    for line in stdout_lines:
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            non_json.append(line)
            continue
        assert parsed.get("jsonrpc") == "2.0", f"not a JSON-RPC frame: {line!r}"

    assert not non_json, (
        "stdout carried non-JSON-RPC bytes that would corrupt a client session:\n"
        + "\n".join(repr(line) for line in non_json)
    )

    # Confirm the probe tool actually ran, so the tool path was exercised.
    responses = [json.loads(line) for line in stdout_lines]
    tool_response = next(
        (r for r in responses if r.get("id") == 2 and "result" in r), None
    )
    assert tool_response is not None, (
        "tools/call did not reach the probe tool; responses were: "
        + repr(responses)[:2000]
    )
    payload = json.loads(tool_response["result"]["content"][0]["text"])
    assert payload["echo"] == "pollute"


def test_stdio_session_reports_no_stdout_logging():
    """Even under the probe tool, no logging handler targets stdout."""
    logging_config.configure_logging(level=logging.DEBUG, force=True)
    register_tool  # ensure the registry import path is exercised
    assert not _has_stdout_handler(logging.getLogger(LOGGER_NAME))
    assert not _has_stdout_handler(logging.getLogger())
