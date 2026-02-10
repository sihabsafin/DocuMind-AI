"""
Summarization Strategies
Implements Stuff, Map-Reduce, and Refine chains for different document types
"""
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass

from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document as LangChainDocument

from src.core.chunking_engine import TextChunk
from src.models.llm_manager import llm_manager
from config.settings import SUMMARY_LEVELS, SUMMARY_STYLES


@dataclass
class SummaryResult:
    """Result of a summarization operation"""
    content: str
    summary_type: str  # tldr, bullet, executive, detailed
    strategy_used: str  # stuff, map_reduce, refine
    model_used: str
    total_chunks: int
    metadata: Dict


class BaseSummarizationStrategy(ABC):
    """Base class for summarization strategies"""
    
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name
        self.llm = llm_manager.get_model(model_name)
    
    @abstractmethod
    def summarize(
        self,
        chunks: List[TextChunk],
        summary_type: str = "executive",
        style: str = "professional"
    ) -> SummaryResult:
        """Summarize chunks of text"""
        pass
    
    def _chunks_to_langchain_docs(self, chunks: List[TextChunk]) -> List[LangChainDocument]:
        """Convert TextChunks to LangChain Documents"""
        docs = []
        for chunk in chunks:
            metadata = {
                'chunk_id': chunk.chunk_id,
                'section_title': chunk.section_title,
                'section_level': chunk.section_level,
                'token_count': chunk.token_count
            }
            docs.append(LangChainDocument(
                page_content=chunk.content,
                metadata=metadata
            ))
        return docs
    
    def _get_prompt_template(self, summary_type: str, style: str) -> str:
        """Get prompt template based on summary type and style"""
        summary_config = SUMMARY_LEVELS.get(summary_type, SUMMARY_LEVELS['executive'])
        style_instruction = SUMMARY_STYLES.get(style, SUMMARY_STYLES['executive'])
        
        if summary_type == "tldr":
            return f"""Write a concise TL;DR (1-2 sentences) of the following text.
            
Style: {style_instruction}

Text:
{{text}}

TL;DR:"""
        
        elif summary_type == "bullet":
            return f"""Summarize the following text as 5-7 clear bullet points.

Style: {style_instruction}

Text:
{{text}}

BULLET SUMMARY:"""
        
        elif summary_type == "executive":
            return f"""Write an executive summary of the following text.
Include:
- Main purpose/objective
- Key findings or points
- Conclusions or recommendations

Maximum length: {summary_config['max_length']} words
Style: {style_instruction}

Text:
{{text}}

EXECUTIVE SUMMARY:"""
        
        elif summary_type == "detailed":
            return f"""Write a comprehensive, detailed summary of the following text.
Include:
- Full context and background
- All major points and supporting details
- Methodology (if applicable)
- Key findings and evidence
- Conclusions and implications

Preserve the logical flow and structure.
Maximum length: {summary_config['max_length']} words
Style: {style_instruction}

Text:
{{text}}

DETAILED SUMMARY:"""
        
        else:
            return f"""Summarize the following text clearly and comprehensively.

Style: {style_instruction}

Text:
{{text}}

SUMMARY:"""


class StuffStrategy(BaseSummarizationStrategy):
    """
    Stuff strategy - puts all text into a single prompt
    Best for: Short documents (<4000 tokens)
    """
    
    def summarize(
        self,
        chunks: List[TextChunk],
        summary_type: str = "executive",
        style: str = "professional"
    ) -> SummaryResult:
        """Summarize using stuff strategy"""
        
        # Combine all chunks into one text
        combined_text = "\n\n".join([chunk.content for chunk in chunks])
        
        # Get prompt
        prompt_template = self._get_prompt_template(summary_type, style)
        prompt = PromptTemplate(template=prompt_template, input_variables=["text"])
        
        # Create chain
        docs = [LangChainDocument(page_content=combined_text)]
        chain = load_summarize_chain(
            llm=self.llm,
            chain_type="stuff",
            prompt=prompt
        )
        
        # Run summarization
        result = chain.run(docs)
        
        return SummaryResult(
            content=result.strip(),
            summary_type=summary_type,
            strategy_used="stuff",
            model_used=self.model_name or "default",
            total_chunks=len(chunks),
            metadata={
                'style': style,
                'combined_length': len(combined_text)
            }
        )


class MapReduceStrategy(BaseSummarizationStrategy):
    """
    Map-Reduce strategy - summarizes each chunk independently, then combines
    Best for: Long documents (4000-100000 tokens)
    """
    
    def summarize(
        self,
        chunks: List[TextChunk],
        summary_type: str = "executive",
        style: str = "professional"
    ) -> SummaryResult:
        """Summarize using map-reduce strategy"""
        
        # Convert chunks to LangChain documents
        docs = self._chunks_to_langchain_docs(chunks)
        
        # Map prompt - summarize individual chunks
        map_template = f"""Write a concise summary of the following section:

{{text}}

SECTION SUMMARY:"""
        
        map_prompt = PromptTemplate(template=map_template, input_variables=["text"])
        
        # Reduce prompt - combine summaries
        reduce_template = self._get_prompt_template(summary_type, style)
        reduce_prompt = PromptTemplate(template=reduce_template, input_variables=["text"])
        
        # Create chain
        chain = load_summarize_chain(
            llm=self.llm,
            chain_type="map_reduce",
            map_prompt=map_prompt,
            combine_prompt=reduce_prompt,
            return_intermediate_steps=False
        )
        
        # Run summarization
        result = chain.run(docs)
        
        return SummaryResult(
            content=result.strip(),
            summary_type=summary_type,
            strategy_used="map_reduce",
            model_used=self.model_name or "default",
            total_chunks=len(chunks),
            metadata={
                'style': style,
                'num_sections': len(docs)
            }
        )


class RefineStrategy(BaseSummarizationStrategy):
    """
    Refine strategy - builds summary iteratively, refining with each chunk
    Best for: Premium quality summaries where quality > speed
    """
    
    def summarize(
        self,
        chunks: List[TextChunk],
        summary_type: str = "executive",
        style: str = "professional"
    ) -> SummaryResult:
        """Summarize using refine strategy"""
        
        # Convert chunks to LangChain documents
        docs = self._chunks_to_langchain_docs(chunks)
        
        # Initial prompt - for first chunk
        initial_template = self._get_prompt_template(summary_type, style)
        initial_prompt = PromptTemplate(template=initial_template, input_variables=["text"])
        
        # Refine prompt - for subsequent chunks
        refine_template = f"""You are working on producing a {summary_type} summary.
We have an existing summary up to this point:

{{existing_answer}}

Now you have the opportunity to refine this summary with additional context:

{{text}}

Given this new context, refine and improve the existing summary.
If the new context is not relevant, return the existing summary unchanged.

Style: {SUMMARY_STYLES.get(style, SUMMARY_STYLES['executive'])}

REFINED SUMMARY:"""
        
        refine_prompt = PromptTemplate(
            template=refine_template,
            input_variables=["existing_answer", "text"]
        )
        
        # Create chain
        chain = load_summarize_chain(
            llm=self.llm,
            chain_type="refine",
            question_prompt=initial_prompt,
            refine_prompt=refine_prompt,
            return_intermediate_steps=False
        )
        
        # Run summarization
        result = chain.run(docs)
        
        return SummaryResult(
            content=result.strip(),
            summary_type=summary_type,
            strategy_used="refine",
            model_used=self.model_name or "default",
            total_chunks=len(chunks),
            metadata={
                'style': style,
                'num_refinements': len(docs) - 1
            }
        )


class StrategySelectorr:
    """Automatically selects the best summarization strategy"""
    
    @staticmethod
    def select_strategy(
        chunks: List[TextChunk],
        total_tokens: int,
        quality_preference: str = "balanced"
    ) -> str:
        """
        Select appropriate strategy based on document characteristics
        
        Args:
            chunks: List of text chunks
            total_tokens: Total token count
            quality_preference: "fast", "balanced", or "premium"
        
        Returns:
            Strategy name: "stuff", "map_reduce", or "refine"
        """
        
        # For very short documents, use stuff
        if total_tokens < 4000:
            return "stuff"
        
        # For premium quality preference, use refine
        if quality_preference == "premium" and total_tokens < 50000:
            return "refine"
        
        # For very long documents, map-reduce is more efficient
        if total_tokens > 50000:
            return "map_reduce"
        
        # Default to map-reduce for balanced approach
        if quality_preference == "balanced":
            return "map_reduce"
        
        # For fast preference, use map-reduce (parallelizable)
        if quality_preference == "fast":
            return "map_reduce"
        
        # Default
        return "map_reduce"
    
    @staticmethod
    def get_strategy_instance(
        strategy_name: str,
        model_name: Optional[str] = None
    ) -> BaseSummarizationStrategy:
        """Get an instance of the specified strategy"""
        
        strategies = {
            "stuff": StuffStrategy,
            "map_reduce": MapReduceStrategy,
            "refine": RefineStrategy
        }
        
        strategy_class = strategies.get(strategy_name)
        if not strategy_class:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        
        return strategy_class(model_name=model_name)


class MultiLevelSummarizer:
    """
    Generates multiple summary levels for a document
    Produces: TL;DR, Bullet Summary, Executive Summary, Detailed Summary
    """
    
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name
        self.selector = StrategySelectorr()
    
    def generate_all_summaries(
        self,
        chunks: List[TextChunk],
        total_tokens: int,
        style: str = "professional"
    ) -> Dict[str, SummaryResult]:
        """Generate all summary levels"""
        
        # Select base strategy
        strategy_name = self.selector.select_strategy(chunks, total_tokens, "balanced")
        
        summaries = {}
        
        # Get model names from settings
        from config.settings import settings
        
        # TL;DR - use fast model
        fast_strategy = self.selector.get_strategy_instance("stuff", settings.fast_model)
        summaries['tldr'] = fast_strategy.summarize(chunks, "tldr", style)
        
        # Bullet Summary - use default model
        strategy = self.selector.get_strategy_instance(strategy_name, self.model_name)
        summaries['bullet'] = strategy.summarize(chunks, "bullet", style)
        
        # Executive Summary - use default model
        summaries['executive'] = strategy.summarize(chunks, "executive", style)
        
        # Detailed Summary - use premium model for best quality
        premium_strategy = self.selector.get_strategy_instance(
            strategy_name,
            settings.premium_model
        )
        summaries['detailed'] = premium_strategy.summarize(chunks, "detailed", style)
        
        return summaries
