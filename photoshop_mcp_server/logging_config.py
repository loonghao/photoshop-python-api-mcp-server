"""Logging configuration for the Photoshop MCP server.

MCP transports over stdio use ``stdout`` exclusively for JSON-RPC frames. Any
diagnostic output written there is parsed by the client as a protocol message
and breaks the session, so all logging must go to stderr or to a file.

This module is the single place that decides where log records go, and it is
imported by every module that logs so the configuration can never drift back
to ``stdout``.
"""

import logging
import os
import sys
from typing import Any

DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

#: Name of the package-level logger. Modules should obtain their logger with
#: ``logging.getLogger(__name__)`` so that they nest under this one.
LOGGER_NAME = "photoshop-mcp-server"

ENV_LOG_LEVEL = "PS_MCP_LOG_LEVEL"
ENV_LOG_FILE = "PS_MCP_LOG_FILE"

_VALID_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


def _resolve_level(raw: str | None, default: int = logging.INFO) -> int:
    """Translate an environment override into a logging level.

    Args:
        raw: Value of the level environment variable.
        default: Level used when the variable is unset or unrecognised.

    Returns:
        int: A logging level constant.

    """
    if not raw:
        return default
    candidate = raw.strip().upper()
    if candidate in _VALID_LEVELS:
        return getattr(logging, candidate)
    return default


def _build_handlers(log_file: str | None) -> list[logging.Handler]:
    """Create the handlers that log records are routed to.

    Args:
        log_file: Optional path for file logging.

    Returns:
        list: Configured logging handlers. Never targets ``stdout``.

    """
    formatter = logging.Formatter(DEFAULT_LOG_FORMAT)

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(formatter)

    handlers: list[logging.Handler] = [stderr_handler]

    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(formatter)
            handlers.append(file_handler)
        except OSError as exc:  # pragma: no cover - depends on filesystem
            # Never let a bad log path take the server down; stderr still works.
            logging.getLogger(LOGGER_NAME).warning(
                "Could not open log file %s: %s", log_file, exc
            )

    return handlers


def configure_logging(
    level: int | None = None,
    log_file: str | None = None,
    force: bool = True,
) -> logging.Logger:
    """Configure the package logger to write only to stderr or a file.

    Environment variables take effect when the matching argument is omitted:

    - ``PS_MCP_LOG_LEVEL``: one of DEBUG, INFO, WARNING, ERROR, CRITICAL.
    - ``PS_MCP_LOG_FILE``: path to a log file; stderr stays enabled alongside.

    Args:
        level: Explicit logging level. Falls back to the environment variable,
            then to INFO.
        log_file: Explicit log file path. Falls back to the environment
            variable, then to stderr-only.
        force: Replace existing handlers instead of appending to them.

    Returns:
        logging.Logger: The configured package logger.

    """
    logger = logging.getLogger(LOGGER_NAME)

    resolved_level = (
        level if level is not None else _resolve_level(os.environ.get(ENV_LOG_LEVEL))
    )
    resolved_file = log_file if log_file is not None else os.environ.get(ENV_LOG_FILE)

    if force:
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            handler.close()

    if not logger.handlers:
        for handler in _build_handlers(resolved_file):
            logger.addHandler(handler)

    logger.setLevel(resolved_level)
    # Let records flow to the handlers we installed rather than being filtered
    # by an ancestor's level or swallowed by a lastResort handler on stderr.
    logger.propagate = False

    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a logger nested under the package logger.

    Args:
        name: Logger name, normally ``__name__``.

    Returns:
        logging.Logger: A child of the package logger.

    """
    if not name or name == LOGGER_NAME:
        return logging.getLogger(LOGGER_NAME)
    return logging.getLogger(LOGGER_NAME).getChild(name)


def configure_root_logging(**kwargs: Any) -> None:
    """Point the root logger at stderr so third-party warnings stay off stdout.

    Some third-party libraries emit warnings through the root logger before the
    package logger exists. Routing the root logger away from ``stdout`` keeps
    those records from corrupting the JSON-RPC stream.

    Args:
        **kwargs: Forwarded to :func:`configure_logging`.

    """
    configure_logging(**kwargs)
    root = logging.getLogger()
    if not root.handlers:
        root.addHandler(logging.StreamHandler(sys.stderr))
