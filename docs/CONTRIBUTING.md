# Contributing to the Project

We welcome contributions to this project! Please follow these guidelines to ensure a smooth process.

## Getting Started

*   Ensure you have set up your development environment as described in the main `README.md`.
*   Familiarize yourself with the project structure and existing code.

## Pull Request Process

1.  **Fork the repository** and create your branch from `develop`.
2.  **Make your changes**, adhering to the coding standards and conventions used in the project.
3.  **Ensure all pre-commit hooks pass** before committing your changes. You can run them manually with `poetry run pre-commit run --config tools/.pre-commit-config.yaml --all-files`.
4.  **Write clear, concise commit messages** using conventional commit formatting (e.g., `feat: add new endpoint for user profiles`).
5.  **Add or update tests** for your changes. Ensure all tests pass by running `poetry run pytest`.
6.  **Update documentation** if your changes affect user-facing features, API contracts, or deployment processes.
7.  **Push your branch** to your fork and submit a pull request to the `develop` branch of the main repository.
8.  **Ensure your pull request passes all automated checks** (see below).
9.  **Engage in the code review process** and address any feedback.

## Code Quality and CI Checks

All pull requests must pass the automated checks configured in our CI pipeline before they can be merged. These checks ensure code quality, consistency, and security. The key checks include:

*   **Linting**: Code is checked for style and potential errors using Ruff (`Lint, Format, Type Check` job).
*   **Code Formatting**: Code formatting is verified by Ruff (`Lint, Format, Type Check` job).
*   **Type Checking**: Static type analysis is performed using MyPy (`Lint, Format, Type Check` job).
*   **Automated Tests**: The full suite of unit, integration, and end-to-end tests must pass (`Test Suite` job using pytest).
*   **Dependency Review**: Dependencies are checked for known vulnerabilities or licensing issues (`Dependency Review` job).
*   **Security Scans**:
    *   Static application security testing (SAST) is performed by CodeQL (`CodeQL Analysis` job).
    *   Dependency vulnerability scanning is performed by Snyk (`Snyk Vulnerability Scan` job).

Please ensure these checks are passing on your pull request. You can see the status of these checks directly on the pull request page in GitHub.

## Code Style

This project uses `black` for code formatting and `isort` for import sorting, enforced by pre-commit hooks. Please ensure your contributions adhere to these standards.

## Reporting Bugs

If you find a bug, please open an issue in the GitHub repository. Provide as much detail as possible, including:
*   Steps to reproduce the bug.
*   Expected behavior.
*   Actual behavior.
*   Your environment (Python version, OS, etc.).

Thank you for contributing!
