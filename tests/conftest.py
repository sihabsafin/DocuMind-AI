"""
Pytest configuration and fixtures
"""
import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_text():
    """Sample text for testing"""
    return """
# Introduction

This is a sample document for testing purposes.

## Background

The background section provides context for the research.

## Methodology

We used various methods to conduct this study.

# Results

The results show significant findings.

## Discussion

The discussion analyzes the results in detail.

# Conclusion

The conclusion summarizes the key findings.
"""


@pytest.fixture
def sample_sections():
    """Sample document sections for testing"""
    from src.processors.document_processor import DocumentSection
    
    return [
        DocumentSection("Introduction", "Introduction content", 1),
        DocumentSection("Methodology", "Methodology content", 2),
        DocumentSection("Results", "Results content", 1),
        DocumentSection("Conclusion", "Conclusion content", 1)
    ]


@pytest.fixture
def mock_groq_api_key(monkeypatch):
    """Mock Groq API key for testing"""
    monkeypatch.setenv("GROQ_API_KEY", "test_key_12345")


@pytest.fixture
def temp_upload_dir(tmp_path):
    """Create temporary upload directory"""
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    return upload_dir
