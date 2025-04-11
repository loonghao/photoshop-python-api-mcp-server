# Import built-in modules
import platform

# Import third-party modules
import nox

# Define package name
PACKAGE_NAME = "photoshop_mcp_server"


@nox.session
def lint(session):
    """Run linting checks."""
    session.install("isort", "ruff", "black")
    session.run("isort", "--check-only", PACKAGE_NAME)
    session.run("black", "--check", PACKAGE_NAME)
    session.run("ruff", "check", PACKAGE_NAME)


@nox.session(name="lint-fix")
def lint_fix(session):
    """Fix linting issues."""
    session.install("isort", "ruff", "black", "pre-commit")
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
