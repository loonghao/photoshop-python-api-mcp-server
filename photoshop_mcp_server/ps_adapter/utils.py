"""Utility functions for Photoshop adapter."""

import time
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar, cast

from loguru import logger
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

# Type variable for generic function
T = TypeVar("T")


def with_retry(
    max_attempts: int = 3, wait_seconds: float = 2.0
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Retry a function if it fails.

    This is particularly useful when Photoshop is starting up and not immediately responsive.

    Args:
        max_attempts: Maximum number of retry attempts.
        wait_seconds: Time to wait between retries in seconds.

    Returns:
        Decorated function with retry logic.

    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            attempts = 0
            last_exception = None

            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    last_exception = e

                    if attempts < max_attempts:
                        logger.warning(
                            f"Error executing {func.__name__}: {e}. "
                            f"Retrying in {wait_seconds} seconds... "
                            f"(Attempt {attempts}/{max_attempts})"
                        )
                        time.sleep(wait_seconds)
                    else:
                        logger.error(
                            f"Failed to execute {func.__name__} after {max_attempts} attempts: {e}"
                        )

            # If we get here, all attempts failed
            if last_exception:
                raise last_exception

            # This should never happen, but to satisfy the type checker
            raise RuntimeError(
                f"Failed to execute {func.__name__} after {max_attempts} attempts"
            )

        return cast(Callable[..., T], wrapper)

    return decorator


def with_tenacity_retry(
    max_attempts: int = 5,
    wait_seconds: float = 2.0,
    exception_types: tuple = (Exception,),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Retry a function using tenacity.

    This provides more advanced retry capabilities for Photoshop operations.

    Args:
        max_attempts: Maximum number of retry attempts.
        wait_seconds: Time to wait between retries in seconds.
        exception_types: Tuple of exception types to retry on.

    Returns:
        Decorated function with retry logic.

    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_fixed(wait_seconds),
            retry=retry_if_exception_type(exception_types),
            before_sleep=lambda retry_state: logger.warning(
                f"Error executing {func.__name__}: {retry_state.outcome.exception()}. "
                f"Retrying in {wait_seconds} seconds... "
                f"(Attempt {retry_state.attempt_number}/{max_attempts})"
            ),
        )
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            return func(*args, **kwargs)

        return cast(Callable[..., T], wrapper)

    return decorator
