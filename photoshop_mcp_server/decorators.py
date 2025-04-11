"""Decorators for MCP tools."""

import functools
import inspect
import sys
import traceback
from collections.abc import Callable
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def debug_tool(func: F) -> F:
    """Add detailed error information to MCP tool functions.

    This decorator wraps MCP tool functions to catch exceptions and provide
    detailed error information in the response, including:
    - Exception type
    - Exception message
    - Stack trace
    - Function arguments

    Args:
        func: The MCP tool function to decorate

    Returns:
        The decorated function

    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> dict[str, Any]:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Get the exception info
            exc_type, exc_value, exc_traceback = sys.exc_info()

            # Format the traceback
            tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            tb_text = "".join(tb_lines)

            # Print to console for server-side debugging
            print(f"ERROR in {func.__name__}:\n{tb_text}")

            # Get the function arguments
            arg_spec = inspect.getfullargspec(func)
            arg_names = arg_spec.args

            # Create a dictionary of argument names and values
            # Skip 'self' if it's a method
            start_idx = 1 if arg_names and arg_names[0] == "self" else 0
            arg_dict = {}
            for i, arg_name in enumerate(arg_names[start_idx:], start_idx):
                if i < len(args):
                    arg_dict[arg_name] = repr(args[i])

            # Add keyword arguments
            for key, value in kwargs.items():
                arg_dict[key] = repr(value)

            # Format arguments for display
            args_str = ", ".join(f"{k}={v}" for k, v in arg_dict.items())

            # Create a user-friendly error message
            user_error = f"Error in {func.__name__}: {e!s}\nArguments: {args_str}\n\nTraceback:\n{tb_text}"

            # Create detailed error response
            error_response = {
                "success": False,
                "error": str(e),  # Original short error
                "detailed_error": user_error,  # Detailed error for display
                "error_type": exc_type.__name__,
                "traceback": tb_text,
                "function": func.__name__,
                "arguments": arg_dict,
                "module": func.__module__,
            }

            return error_response

    return wrapper  # type: ignore


def log_tool_call(func: F) -> F:
    """Log MCP tool function calls.

    This decorator logs the function name and arguments when called,
    and the result when the function returns.

    Args:
        func: The MCP tool function to decorate

    Returns:
        The decorated function

    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Get the function arguments
        arg_spec = inspect.getfullargspec(func)
        arg_names = arg_spec.args

        # Create a dictionary of argument names and values
        # Skip 'self' if it's a method
        start_idx = 1 if arg_names and arg_names[0] == "self" else 0
        arg_dict = {}
        for i, arg_name in enumerate(arg_names[start_idx:], start_idx):
            if i < len(args):
                arg_dict[arg_name] = repr(args[i])

        # Add keyword arguments
        for key, value in kwargs.items():
            arg_dict[key] = repr(value)

        # Log the function call
        print(
            f"TOOL CALL: {func.__name__}({', '.join(f'{k}={v}' for k, v in arg_dict.items())})"
        )

        # Call the function
        result = func(*args, **kwargs)

        # Log the result
        print(f"TOOL RESULT: {func.__name__} -> {result}")

        return result

    return wrapper  # type: ignore
