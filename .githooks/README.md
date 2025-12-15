# Git Hooks

This directory contains Git hooks that help enforce code quality and standards for this project.

## Setup

The hooks should be automatically set up when you clone the repository by running:

```bash
git config core.hooksPath .githooks
chmod +x .githooks/*
```

## Available Hooks

### 1. pre-commit

This hook runs before each commit and performs the following checks:

- **Secret Detection**: Uses [gitleaks](https://github.com/gitleaks/gitleaks) to scan for credentials and secrets
- **Terraform Validation**:
  - Uses `terraform fmt` to check formatting
  - Uses `terraform validate` to verify configuration
  - Uses [tflint](https://github.com/terraform-linters/tflint) for additional linting
- **Python Linting** (using tools defined in pyproject.toml):
  - Uses [ruff](https://github.com/astral-sh/ruff) for code formatting, linting, and import sorting
  - Uses [mypy](https://mypy.readthedocs.io/) for static type checking

### 2. commit-msg

This hook validates commit messages against the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
type(scope): description
```

Examples:

- `feat(api): add new endpoint for user registration`
- `fix(auth): resolve login issue with expired tokens`
- `docs: update README with setup instructions`

### 3. pre-push

This hook runs comprehensive checks before pushing to remote repositories:

- **Runs pre-commit checks on all files** (not just staged files):
  - Secret detection with gitleaks
  - Terraform validation and linting
  - Python code formatting and linting
- **Runs all tests** regardless of branch:
  - Executes the full test suite using pytest
  - Provides clear feedback on test results
- **Protected branch checks** (main, master, develop, release, production):
  - Additional validation checks for protected branches

## Required Tools

For the best experience, install these tools:

- **gitleaks**: `brew install gitleaks` (macOS) or follow [installation guide](https://github.com/gitleaks/gitleaks#installing)
- **tflint**: `brew install tflint` (macOS) or follow [installation guide](https://github.com/terraform-linters/tflint#installation)
- **terraform**: [Installation guide](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)
- **uv**: [Installation guide](https://github.com/astral-sh/uv#installation) (required for Python dependency management)

## Python Development Tools

The Python tools are managed through uv and specified in pyproject.toml:

```bash
# Install all development dependencies
uv pip install -e ".[dev]"

# Or install individual tools
uv pip install ruff mypy pytest
```

## Bypassing Hooks

If needed, you can bypass hooks using the `--no-verify` flag:

```bash
git commit --no-verify
git push --no-verify
```

However, this should be done only in exceptional cases. 