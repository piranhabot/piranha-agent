# Release Process

This document describes how to prepare and publish a new release of Piranha Agent.

## Checklist

1.  **Version Update**:
    - Update `version` in `pyproject.toml`.
    - Update `version` in `rust_core/Cargo.toml`.
    - Update `piranha/version.py`.
2.  **Changelog**:
    - Update `CHANGELOG.md` with the new version and its changes.
3.  **Testing**:
    - Run all tests: `make test`.
    - Ensure CI passes.
4.  **Tagging**:
    - Create a new git tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`.
    - Push the tag: `git push origin vX.Y.Z`.
5.  **GitHub Release**:
    - Create a new release on GitHub from the tag.
    - Attach build artifacts if necessary.
6.  **PyPI**:
    - GitHub Actions will automatically build and publish to PyPI on tag creation.

## Manual Publishing (Optional)

To publish manually:

```bash
maturin publish
```
