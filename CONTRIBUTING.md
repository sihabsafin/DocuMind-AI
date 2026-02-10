# Contributing to DocuMind AI

Thank you for your interest in contributing to DocuMind AI! 🎉

We welcome contributions from the community to help make this project better.

---

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version)
- Screenshots if applicable

### Suggesting Features

We love new ideas! For feature requests:
- Check existing issues first
- Explain the use case
- Describe the expected behavior
- Consider implementation approach

### Code Contributions

1. **Fork the repository**

2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make your changes**
   - Follow the code style (see below)
   - Add tests if applicable
   - Update documentation

4. **Test your changes**
   ```bash
   pytest tests/
   ```

5. **Commit with clear messages**
   ```bash
   git commit -m "Add amazing feature"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

7. **Open a Pull Request**
   - Describe your changes
   - Reference related issues
   - Wait for review

---

## 📋 Code Style

### Python
- Follow PEP 8
- Use Black for formatting: `black src/`
- Use type hints where possible
- Write docstrings for functions

### Docstrings Format
```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of function
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When something goes wrong
    """
    pass
```

### Imports
```python
# Standard library
import os
from pathlib import Path

# Third party
import streamlit as st
from langchain import ...

# Local
from src.core import ...
```

---

## 🧪 Testing

### Running Tests
```bash
# All tests
pytest

# With coverage
pytest --cov=src

# Specific test file
pytest tests/test_processors.py

# Verbose mode
pytest -v
```

### Writing Tests
- Place tests in `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use fixtures from `conftest.py`

Example:
```python
def test_feature():
    """Test that feature works correctly"""
    result = my_function(input_data)
    assert result == expected_output
```

---

## 📁 Project Structure

```
documind-ai/
├── src/
│   ├── core/           # Core functionality
│   ├── strategies/     # Summarization strategies
│   ├── processors/     # Document processors
│   ├── models/         # LLM management
│   ├── agents/         # Future: Research agents
│   └── utils/          # Utility functions
├── config/             # Configuration
├── tests/              # Test suite
├── data/               # Data directories
├── ui/                 # UI components (future)
├── docs/               # Additional documentation
├── app.py              # Main application
└── requirements.txt    # Dependencies
```

---

## 🎯 Priority Areas

We're particularly interested in contributions for:

1. **Document Processors**
   - Support for more file types
   - Better table extraction
   - Image OCR support

2. **Summarization Quality**
   - Better prompt engineering
   - Quality metrics
   - Fact-checking

3. **UI/UX Improvements**
   - Better visualizations
   - Responsive design
   - Accessibility

4. **Performance**
   - Caching improvements
   - Parallel processing
   - Memory optimization

5. **Testing**
   - More test coverage
   - Integration tests
   - Performance benchmarks

---

## 📝 Documentation

When adding features:
- Update README.md if needed
- Add docstrings to new functions
- Update configuration examples
- Add usage examples

---

## 🔍 Code Review Process

1. **Automated Checks**
   - Tests must pass
   - Code style must comply
   - No breaking changes

2. **Manual Review**
   - Code quality
   - Documentation
   - Test coverage
   - Performance impact

3. **Approval**
   - At least one maintainer approval
   - All discussions resolved
   - Ready to merge!

---

## 🐛 Found a Security Issue?

Please **do not** open a public issue. Instead:
- Email: security@documind.ai
- Describe the vulnerability
- Include steps to reproduce
- We'll respond within 48 hours

---

## 💬 Communication

- **GitHub Issues**: Bug reports, features
- **Discussions**: Questions, ideas
- **Discord**: Real-time chat
- **Email**: General inquiries

---

## ⚖️ License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## 🙏 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

---

## 📚 Resources

- [Python Style Guide](https://pep8.org/)
- [Git Best Practices](https://www.git-scm.com/book/en/v2)
- [Pytest Documentation](https://docs.pytest.org/)
- [Streamlit Docs](https://docs.streamlit.io/)

---

Thank you for contributing to DocuMind AI! 🚀
