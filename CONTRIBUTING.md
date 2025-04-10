# Contributing to SAGE

Thank you for considering contributing to SAGE! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project.

## How to Contribute

1. **Fork the repository** and create your branch from `main`.
2. **Clone the repository** to your local machine.
3. **Install development dependencies**: `pip install -e .[dev]`
4. **Make your changes** and add tests if applicable.
5. **Run tests** to ensure they pass: `pytest`
6. **Commit your changes** with clear commit messages.
7. **Push to your fork** and submit a pull request.

## Development Environment

- Use Python 3.8+ for development
- Install development dependencies: `pip install -e .[dev]`
- Format code with `black`: `black src/ tests/`
- Sort imports with `isort`: `isort src/ tests/`
- Run tests with `pytest`: `pytest`

## Pull Request Process

1. Update the README.md or documentation with details of changes if needed.
2. Update the tests if necessary.
3. The PR should work for Python 3.8, 3.9, 3.10, and 3.11.
4. PR needs to be approved by at least one maintainer before merging.

## Coding Standards

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use docstrings for functions and classes following Google style
- Write unit tests for new features
- Keep functions small and focused

## Creating a Release

1. Update version in `src/sage/version.py`
2. Update CHANGELOG.md
3. Create a GitHub release
4. GitHub Actions will publish to PyPI

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.
