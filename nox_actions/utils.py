# Import built-in modules
from pathlib import Path


PACKAGE_NAME = ""
THIS_ROOT = Path(__file__).parent.parent
PROJECT_ROOT = THIS_ROOT.parent


def _assemble_env_paths(*paths):
    """Assemble environment paths separated by a semicolon.

    Args:
        *paths: Paths to be assembled.

    Returns:
        str: Assembled paths separated by a semicolon.

    """
    return ";".join(paths)
