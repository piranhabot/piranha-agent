# PyPI Publishing Instructions

## Prerequisites

1. **Create PyPI Account**: https://pypi.org/account/register/
2. **Create TestPyPI Account** (for testing): https://test.pypi.org/account/register/

## Generate API Token

### For PyPI:
1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Token name: `github-actions-piranha`
4. Scope: All projects
5. Copy the token (starts with `pypi-`)

### For TestPyPI:
1. Go to https://test.pypi.org/manage/account/token/
2. Click "Add API token"
3. Token name: `github-actions-piranha-test`
4. Copy the token

## Add Secrets to GitHub

1. Go to your repo: `https://github.com/YOUR_USERNAME/piranha-agent`
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add these secrets:

| Name | Value |
|------|-------|
| `PYPI_API_TOKEN` | `pypi-AgEIcHlwaS5vcmc...` (your PyPI token) |
| `TESTPYPI_API_TOKEN` | `pypi-AgEIcHlwaS5vcmc...` (your TestPyPI token) |
| `CODECOV_TOKEN` | (get from https://codecov.io/ after enabling repo) |

## Test Publishing (Optional)

Before publishing to real PyPI, test with TestPyPI:

```bash
# Build wheel
pip install maturin
maturin build --release

# Upload to TestPyPI
pip install twine
twine upload --repository testpypi target/wheels/*.whl

# Test installation
pip install --index-url https://test.pypi.org/simple/ piranha-agent
```

## Manual Publishing

If you want to publish manually instead of using GitHub Actions:

```bash
# Build
maturin build --release

# Upload to PyPI
twine upload target/wheels/*.whl
```

## Automatic Publishing

The GitHub Actions workflow will automatically publish to PyPI when you:
1. Create a new release on GitHub
2. Tag it with a version (e.g., `v0.3.0`)
3. The workflow will build and publish automatically

## Verify Publication

After publishing, verify on:
- PyPI: https://pypi.org/project/piranha-agent/
- TestPyPI: https://test.pypi.org/project/piranha-agent/

## Installation After Publishing

Users can install with:
```bash
pip install piranha-agent
```
