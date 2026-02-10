"""
Intelligent text chunking engine
Handles dynamic chunk sizing, overlap optimization, and token-aware splitting
"""
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import tiktoken

from src.processors.document_processor import ProcessedDocument, DocumentSection


@dataclass
class TextChunk:
    """Represents a chunk of text"""
    content: str
    chunk_id: int
    section_title: Optional[str] = None
    section_level: Optional[int] = None
    start_position: int = 0
    end_position: int = 0
    token_count: int = 0
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ChunkingEngine:
    """Intelligent text chunking with multiple strategies"""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        model_name: str = "gpt-3.5-turbo"
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.encoding_for_model(model_name)
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(text))
    
    def chunk_document(
        self,
        document: ProcessedDocument,
        strategy: str = "smart"
    ) -> List[TextChunk]:
        """
        Chunk a document using the specified strategy
        
        Strategies:
        - smart: Section-aware chunking (default)
        - fixed: Fixed-size chunks
        - sentence: Sentence-based chunks
        - section: One chunk per section
        """
        if strategy == "smart":
            return self._smart_chunk(document)
        elif strategy == "fixed":
            return self._fixed_chunk(document.full_text)
        elif strategy == "sentence":
            return self._sentence_chunk(document.full_text)
        elif strategy == "section":
            return self._section_chunk(document)
        else:
            raise ValueError(f"Unknown chunking strategy: {strategy}")
    
    def _smart_chunk(self, document: ProcessedDocument) -> List[TextChunk]:
        """
        Smart chunking that preserves section boundaries when possible
        Falls back to fixed chunking for long sections
        """
        chunks = []
        chunk_id = 0
        
        for section in document.sections:
            section_tokens = self.count_tokens(section.content)
            
            # If section fits in one chunk, use it as-is
            if section_tokens <= self.chunk_size:
                chunks.append(TextChunk(
                    content=section.content,
                    chunk_id=chunk_id,
                    section_title=section.title,
                    section_level=section.level,
                    token_count=section_tokens,
                    metadata={
                        'strategy': 'section_preserved',
                        'is_complete_section': True
                    }
                ))
                chunk_id += 1
            else:
                # Split long section into multiple chunks
                section_chunks = self._split_long_section(
                    section,
                    start_chunk_id=chunk_id
                )
                chunks.extend(section_chunks)
                chunk_id += len(section_chunks)
        
        return chunks
    
    def _split_long_section(
        self,
        section: DocumentSection,
        start_chunk_id: int
    ) -> List[TextChunk]:
        """Split a long section into multiple chunks while preserving context"""
        chunks = []
        
        # Try to split by paragraphs first
        paragraphs = self._split_into_paragraphs(section.content)
        
        current_chunk = []
        current_tokens = 0
        chunk_id = start_chunk_id
        
        for para in paragraphs:
            para_tokens = self.count_tokens(para)
            
            # If single paragraph is too large, split it
            if para_tokens > self.chunk_size:
                # Save current chunk if any
                if current_chunk:
                    chunks.append(self._create_chunk_from_paragraphs(
                        current_chunk,
                        chunk_id,
                        section.title,
                        section.level
                    ))
                    chunk_id += 1
                    current_chunk = []
                    current_tokens = 0
                
                # Split large paragraph by sentences
                para_chunks = self._split_large_paragraph(para, chunk_id, section)
                chunks.extend(para_chunks)
                chunk_id += len(para_chunks)
            
            # If adding paragraph exceeds chunk size, save current chunk
            elif current_tokens + para_tokens > self.chunk_size:
                if current_chunk:
                    chunks.append(self._create_chunk_from_paragraphs(
                        current_chunk,
                        chunk_id,
                        section.title,
                        section.level
                    ))
                    chunk_id += 1
                
                # Start new chunk with overlap from previous
                if chunks and self.chunk_overlap > 0:
                    overlap_text = self._get_overlap_text(chunks[-1].content)
                    current_chunk = [overlap_text, para]
                    current_tokens = self.count_tokens(overlap_text) + para_tokens
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            
            else:
                current_chunk.append(para)
                current_tokens += para_tokens
        
        # Save last chunk
        if current_chunk:
            chunks.append(self._create_chunk_from_paragraphs(
                current_chunk,
                chunk_id,
                section.title,
                section.level
            ))
        
        return chunks
    
    def _split_large_paragraph(
        self,
        paragraph: str,
        start_chunk_id: int,
        section: DocumentSection
    ) -> List[TextChunk]:
        """Split a very large paragraph by sentences"""
        sentences = self._split_into_sentences(paragraph)
        chunks = []
        
        current_chunk = []
        current_tokens = 0
        chunk_id = start_chunk_id
        
        for sentence in sentences:
            sent_tokens = self.count_tokens(sentence)
            
            if current_tokens + sent_tokens > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = ' '.join(current_chunk)
                chunks.append(TextChunk(
                    content=chunk_text,
                    chunk_id=chunk_id,
                    section_title=section.title,
                    section_level=section.level,
                    token_count=self.count_tokens(chunk_text),
                    metadata={'strategy': 'sentence_split'}
                ))
                chunk_id += 1
                
                # Start new chunk with overlap
                if self.chunk_overlap > 0:
                    overlap_text = self._get_overlap_text(chunk_text)
                    current_chunk = [overlap_text, sentence]
                    current_tokens = self.count_tokens(overlap_text) + sent_tokens
                else:
                    current_chunk = [sentence]
                    current_tokens = sent_tokens
            else:
                current_chunk.append(sentence)
                current_tokens += sent_tokens
        
        # Save last chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append(TextChunk(
                content=chunk_text,
                chunk_id=chunk_id,
                section_title=section.title,
                section_level=section.level,
                token_count=self.count_tokens(chunk_text),
                metadata={'strategy': 'sentence_split'}
            ))
        
        return chunks
    
    def _create_chunk_from_paragraphs(
        self,
        paragraphs: List[str],
        chunk_id: int,
        section_title: str,
        section_level: int
    ) -> TextChunk:
        """Create a chunk from a list of paragraphs"""
        content = '\n\n'.join(paragraphs)
        return TextChunk(
            content=content,
            chunk_id=chunk_id,
            section_title=section_title,
            section_level=section_level,
            token_count=self.count_tokens(content),
            metadata={'strategy': 'paragraph_based'}
        )
    
    def _get_overlap_text(self, text: str) -> str:
        """Get overlap text from the end of previous chunk"""
        tokens = self.encoding.encode(text)
        
        if len(tokens) <= self.chunk_overlap:
            return text
        
        # Get last N tokens for overlap
        overlap_tokens = tokens[-self.chunk_overlap:]
        return self.encoding.decode(overlap_tokens)
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs"""
        # Split by double newlines or more
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitter (can be improved with nltk)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _fixed_chunk(self, text: str) -> List[TextChunk]:
        """Create fixed-size chunks"""
        chunks = []
        tokens = self.encoding.encode(text)
        
        chunk_id = 0
        i = 0
        
        while i < len(tokens):
            # Get chunk tokens
            chunk_tokens = tokens[i:i + self.chunk_size]
            chunk_text = self.encoding.decode(chunk_tokens)
            
            chunks.append(TextChunk(
                content=chunk_text,
                chunk_id=chunk_id,
                token_count=len(chunk_tokens),
                metadata={'strategy': 'fixed'}
            ))
            
            # Move forward with overlap
            i += self.chunk_size - self.chunk_overlap
            chunk_id += 1
        
        return chunks
    
    def _sentence_chunk(self, text: str) -> List[TextChunk]:
        """Create chunks based on sentences"""
        sentences = self._split_into_sentences(text)
        chunks = []
        
        current_chunk = []
        current_tokens = 0
        chunk_id = 0
        
        for sentence in sentences:
            sent_tokens = self.count_tokens(sentence)
            
            if current_tokens + sent_tokens > self.chunk_size and current_chunk:
                chunk_text = ' '.join(current_chunk)
                chunks.append(TextChunk(
                    content=chunk_text,
                    chunk_id=chunk_id,
                    token_count=self.count_tokens(chunk_text),
                    metadata={'strategy': 'sentence'}
                ))
                chunk_id += 1
                current_chunk = [sentence]
                current_tokens = sent_tokens
            else:
                current_chunk.append(sentence)
                current_tokens += sent_tokens
        
        # Save last chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append(TextChunk(
                content=chunk_text,
                chunk_id=chunk_id,
                token_count=self.count_tokens(chunk_text),
                metadata={'strategy': 'sentence'}
            ))
        
        return chunks
    
    def _section_chunk(self, document: ProcessedDocument) -> List[TextChunk]:
        """Create one chunk per section"""
        chunks = []
        
        for chunk_id, section in enumerate(document.sections):
            chunks.append(TextChunk(
                content=section.content,
                chunk_id=chunk_id,
                section_title=section.title,
                section_level=section.level,
                token_count=self.count_tokens(section.content),
                metadata={
                    'strategy': 'section',
                    'is_complete_section': True
                }
            ))
        
        return chunks
    
    def optimize_chunk_size(self, document: ProcessedDocument) -> int:
        """
        Dynamically determine optimal chunk size based on document characteristics
        """
        total_tokens = self.count_tokens(document.full_text)
        num_sections = len(document.sections)
        
        # For short documents, use smaller chunks
        if total_tokens < 5000:
            return 500
        
        # For medium documents with clear sections
        elif total_tokens < 20000 and num_sections > 3:
            return 1000
        
        # For long documents
        elif total_tokens < 50000:
            return 1500
        
        # For very long documents
        else:
            return 2000
