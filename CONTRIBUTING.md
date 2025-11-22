# Contributing to Adaptive Question Generator

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)
- Error messages or screenshots

### Suggesting Features

Open an issue with:
- Clear description of the feature
- Use case / why it's needed
- Example of how it would work

### Contributing Code

1. **Fork the repository**
2. **Create a branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Test thoroughly**
5. **Commit**: `git commit -m "Add: feature description"`
6. **Push**: `git push origin feature/your-feature-name`
7. **Open a Pull Request**

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Agent_Compute.git
cd Agent_Compute

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8

# Run tests
pytest

# Format code
black .

# Check linting
flake8
```

## Code Style

- Follow PEP 8 style guidelines
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and small
- Add comments for complex logic

## Testing

- Add tests for new features
- Ensure existing tests pass
- Test with different file formats
- Test with both Ollama and OpenAI

## Documentation

- Update relevant .md files
- Add docstrings to new functions
- Update USAGE_GUIDE.md if needed
- Add examples for new features

## Commit Messages

Use clear, descriptive commit messages:

- `Add: new feature description`
- `Fix: bug description`
- `Update: what was updated`
- `Refactor: what was refactored`
- `Docs: documentation changes`

## Pull Request Process

1. Update documentation
2. Add tests if applicable
3. Ensure all tests pass
4. Update README if needed
5. Describe your changes clearly
6. Link related issues

## Questions?

Open an issue or discussion if you have questions!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

