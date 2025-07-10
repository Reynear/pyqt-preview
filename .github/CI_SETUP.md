# CI/CD Setup Guide

This guide will help you set up the GitHub Actions CI/CD pipeline for PyQt Preview.

## Quick Start

1. **Push the workflow files** to your repository:
   ```bash
   git add .github/
   git commit -m "Add CI/CD pipeline with comprehensive testing"
   git push
   ```

2. **The pipeline will automatically run** on:
   - Push to `main` or `develop` branches
   - Pull requests to `main` or `develop` branches

## What the CI Pipeline Does

### 🧪 **Test Job** (Matrix Strategy)
- **Platforms**: Ubuntu, Windows, macOS
- **Python Versions**: 3.9, 3.10, 3.11, 3.12, 3.13
- **Total Combinations**: 15 test environments
- **Tests**: All 172 unit and integration tests
- **Coverage**: Code coverage reporting with Codecov

### 🔒 **Security Job**
- **Bandit**: Security vulnerability scanning
- **Safety**: Dependency vulnerability checking
- **Python Version**: 3.11 on Ubuntu

### 📚 **Documentation Job**
- **Markdown Linting**: Ensures documentation quality
- **Link Checking**: Validates documentation links
- **Python Version**: 3.11 on Ubuntu

### 🚀 **Integration Job**
- **CLI Installation**: Tests package installation
- **Example Validation**: Syntax checks for example files
- **Real-world Testing**: End-to-end functionality
- **Dependencies**: Runs after main tests pass

## Setting Up External Services

### Codecov (Coverage Reporting)
1. Go to [codecov.io](https://codecov.io)
2. Sign in with your GitHub account
3. Add your repository
4. Coverage reports will be uploaded automatically

### Dependabot (Dependency Updates)
- Already configured in `.github/dependabot.yml`
- Will create weekly PRs for dependency updates
- Groups related dependencies together
- **Action Required**: Replace `your-username` with your GitHub username

## Configuration Files

### Required Files ✅
- `.github/workflows/test.yml` - Main CI workflow
- `.github/dependabot.yml` - Dependency updates
- `pyproject.toml` - Updated with CI dependencies

### Optional Files 📋
- `.github/README_BADGES.md` - Badge templates for README
- `.github/CI_SETUP.md` - This setup guide

## Local Development Commands

Test the same commands that CI runs:

```bash
# Install dependencies
pip install uv
uv sync --dev

# Linting and formatting
uv run ruff check src tests
uv run ruff format src tests

# Type checking
uv run mypy src/pyqt_preview --ignore-missing-imports

# Run tests with coverage
uv run pytest tests/ -v --cov=pyqt_preview --cov-report=term-missing

# Security checks
uv run bandit -r src/

# Test CLI installation
uv run pip install -e .
uv run pyqt-preview --version
```

## Customization

### Modify Test Matrix
Edit `.github/workflows/test.yml`:
```yaml
matrix:
  os: [ubuntu-latest, windows-latest, macos-latest]
  python-version: ["3.9", "3.10", "3.11", "3.12", "3.13"]
```

### Add More Checks
Add additional jobs to the workflow:
- Performance testing
- Documentation building
- Release automation
- Docker image building

### Branch Protection Rules
Consider setting up branch protection rules:
1. Go to Settings → Branches
2. Add rule for `main` branch
3. Require status checks to pass
4. Require pull request reviews

## Troubleshooting

### Common Issues

**Qt/GUI Tests Failing on Linux**
- Uses `xvfb-run` for headless testing
- System dependencies automatically installed

**Import Errors**
- Check `pyproject.toml` dependencies
- Ensure all test dependencies are listed

**Permission Errors**
- Check file permissions in repository
- Ensure workflow files are executable

**Matrix Job Failures**
- Some combinations may fail due to compatibility
- Consider excluding specific combinations if needed

## Monitoring

### GitHub Actions Tab
- View all workflow runs
- Check logs for failed jobs
- Monitor resource usage

### Status Badges
- Add badges to README.md (see `.github/README_BADGES.md`)
- Shows real-time CI status
- Links to detailed reports

## Next Steps

1. **Commit and push** the workflow files
2. **Watch the first run** in GitHub Actions tab
3. **Set up Codecov** for coverage reporting
4. **Add status badges** to your README
5. **Configure branch protection** rules
6. **Customize** the pipeline for your needs

Your PyQt Preview project now has enterprise-grade CI/CD! 🚀 