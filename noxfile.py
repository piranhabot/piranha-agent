import nox

@nox.session(python=["3.10", "3.11", "3.12"])
def tests(session):
    session.install("-e", ".[dev]")
    session.run("maturin", "develop")
    session.run("pytest", "tests/")

@nox.session
def lint(session):
    session.install("ruff", "mypy")
    session.run("ruff", "check", ".")
    session.run("mypy", "piranha_agent/")
