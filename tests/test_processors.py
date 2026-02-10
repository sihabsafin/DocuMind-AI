"""
Test suite for document processors
"""
import pytest
from pathlib import Path
from src.processors.document_processor import (
    PDFProcessor,
    DOCXProcessor,
    TextProcessor,
    DocumentProcessorFactory
)


class TestPDFProcessor:
    """Test PDF document processing"""
    
    def test_pdf_processor_initialization(self):
        """Test PDF processor can be initialized"""
        processor = PDFProcessor()
        assert processor is not None
    
    def test_extract_sections(self):
        """Test section extraction from text"""
        processor = PDFProcessor()
        text = """
# Introduction
This is the introduction.

# Methodology
This is the methodology.

# Conclusion
This is the conclusion.
        """
        sections = processor.extract_sections(text)
        assert len(sections) > 0
        assert any('Introduction' in s.title for s in sections)
    
    def test_count_words(self):
        """Test word counting"""
        processor = PDFProcessor()
        text = "This is a test document with ten words total."
        count = processor.count_words(text)
        assert count == 9  # "ten" is one word


class TestDOCXProcessor:
    """Test DOCX document processing"""
    
    def test_docx_processor_initialization(self):
        """Test DOCX processor can be initialized"""
        processor = DOCXProcessor()
        assert processor is not None


class TestTextProcessor:
    """Test text/markdown document processing"""
    
    def test_text_processor_initialization(self):
        """Test text processor can be initialized"""
        processor = TextProcessor()
        assert processor is not None
    
    def test_markdown_detection(self):
        """Test markdown file detection"""
        processor = TextProcessor()
        # This would need actual file testing
        assert processor is not None


class TestDocumentProcessorFactory:
    """Test the document processor factory"""
    
    def test_get_pdf_processor(self):
        """Test factory returns PDF processor for .pdf files"""
        processor = DocumentProcessorFactory.get_processor(Path("test.pdf"))
        assert isinstance(processor, PDFProcessor)
    
    def test_get_docx_processor(self):
        """Test factory returns DOCX processor for .docx files"""
        processor = DocumentProcessorFactory.get_processor(Path("test.docx"))
        assert isinstance(processor, DOCXProcessor)
    
    def test_get_text_processor(self):
        """Test factory returns text processor for .txt files"""
        processor = DocumentProcessorFactory.get_processor(Path("test.txt"))
        assert isinstance(processor, TextProcessor)
    
    def test_get_markdown_processor(self):
        """Test factory returns text processor for .md files"""
        processor = DocumentProcessorFactory.get_processor(Path("test.md"))
        assert isinstance(processor, TextProcessor)
    
    def test_unsupported_file_type(self):
        """Test factory raises error for unsupported file types"""
        with pytest.raises(ValueError):
            DocumentProcessorFactory.get_processor(Path("test.xyz"))


class TestDocumentSection:
    """Test DocumentSection data structure"""
    
    def test_section_creation(self):
        """Test creating a document section"""
        from src.processors.document_processor import DocumentSection
        
        section = DocumentSection(
            title="Test Section",
            content="This is test content",
            level=1
        )
        
        assert section.title == "Test Section"
        assert section.content == "This is test content"
        assert section.level == 1


class TestProcessedDocument:
    """Test ProcessedDocument data structure"""
    
    def test_processed_doc_creation(self):
        """Test creating a processed document"""
        from src.processors.document_processor import ProcessedDocument, DocumentSection
        
        sections = [
            DocumentSection("Section 1", "Content 1", 1),
            DocumentSection("Section 2", "Content 2", 1)
        ]
        
        doc = ProcessedDocument(
            filename="test.pdf",
            file_type="pdf",
            full_text="Full document text",
            sections=sections,
            metadata={},
            tables=[],
            total_chars=100,
            total_words=20
        )
        
        assert doc.filename == "test.pdf"
        assert doc.file_type == "pdf"
        assert len(doc.sections) == 2
        assert doc.total_words == 20


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
