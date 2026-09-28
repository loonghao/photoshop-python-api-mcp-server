# Import built-in modules
import platform

# Import third-party modules
import nox

# Define package name
PACKAGE_NAME = "photoshop_mcp_server"

# Pinned lint tool versions.
#
# These are pinned on purpose: an unpinned `black` picks up style changes from a
# new upstream release and silently fails `nox -s lint` on untouched code. Local
# runs and CI must use the same versions, so bump these in one place only.
ISORT_VERSION = "9.0.1"
RUFF_VERSION = "0.16.9"
BLACK_VERSION = "26.5.1"

LINT_DEPS = (
    f"isort=={ISORT_VERSION}",
    f"ruff=={RUFF_VERSION}",
    f"black=={BLACK_VERSION}",
)


@nox.session
def lint(session):
    """Run linting checks."""
    session.install(*LINT_DEPS)
    session.run("isort", "--check-only", PACKAGE_NAME)
    session.run("black", "--check", PACKAGE_NAME)
    session.run("ruff", "check", PACKAGE_NAME)


@nox.session(name="lint-fix")
def lint_fix(session):
    """Fix linting issues."""
    session.install(*LINT_DEPS, "pre-commit")
    session.run("ruff", "check", "--fix", PACKAGE_NAME)
    session.run("isort", PACKAGE_NAME)
    session.run("black", PACKAGE_NAME)
    session.run("pre-commit", "run", "--all-files")


@nox.session
def pytest(session):
    """Run the test suite."""
    session.install("-e", ".")
    session.install("pytest", "pytest-cov", "pytest-mock")
    session.run(
        "pytest",
        f"--cov={PACKAGE_NAME}",
        "--cov-report=xml:coverage.xml",
        "--cov-report=term",
        *session.posargs,
    )


@nox.session
def test_photoshop(session):
    """Run tests that require Photoshop (Windows only)."""
    if platform.system() != "Windows":
        session.skip("Photoshop tests only run on Windows")

    session.install("-e", ".")
    session.install("pytest", "pytest-cov")
    session.run(
        "pytest",
        "tests/integration",
        f"--cov={PACKAGE_NAME}",
        "--cov-report=term",
        *session.posargs,
    )


@nox.session
def build(session):
    """Build the package."""
    session.install("poetry")
    session.run("poetry", "build")
