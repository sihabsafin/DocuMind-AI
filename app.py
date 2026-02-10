"""
DocuMind AI - Main Streamlit Application
Enterprise-grade AI Summarization Platform
"""
import streamlit as st
from pathlib import Path
import sys
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings
from src.processors.document_processor import DocumentProcessorFactory
from src.core.chunking_engine import ChunkingEngine
from src.strategies.summarization_strategies import MultiLevelSummarizer, StrategySelectorr
from src.models.llm_manager import llm_manager

# Page configuration
st.set_page_config(
    page_title=settings.app_title,
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enterprise look
st.markdown("""
<style>
    /* Main theme */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Headers */
    h1 {
        color: #FFFFFF;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    h2, h3 {
        color: #E0E0E0;
        font-weight: 600;
    }
    
    /* Cards and containers */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1E1E1E;
        border-radius: 4px;
        padding: 8px 16px;
        color: #A0A0A0;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #2E7D32;
        color: #FFFFFF;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #2E7D32;
        color: white;
        border-radius: 4px;
        padding: 0.5rem 2rem;
        font-weight: 500;
        border: none;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #388E3C;
        box-shadow: 0 4px 12px rgba(46, 125, 50, 0.3);
    }
    
    /* File uploader */
    .uploadedFile {
        background-color: #1E1E1E;
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #2E7D32;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background-color: #2E7D32;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #1A1A1A;
    }
    
    /* Success/Info boxes */
    .stSuccess {
        background-color: #1B5E20;
        border-left: 4px solid #2E7D32;
    }
    
    .stInfo {
        background-color: #0D47A1;
        border-left: 4px solid #1976D2;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if 'processed_doc' not in st.session_state:
        st.session_state.processed_doc = None
    if 'chunks' not in st.session_state:
        st.session_state.chunks = None
    if 'summaries' not in st.session_state:
        st.session_state.summaries = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False


def render_header():
    """Render application header"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("📄 " + settings.app_title)
        st.markdown(f"*{settings.app_subtitle}*")
    
    with col2:
        st.markdown("###")
        if st.button("ℹ️ About"):
            st.info("""
            **DocuMind AI** uses state-of-the-art AI models to:
            - Intelligently summarize documents of any length
            - Preserve document structure and context
            - Generate multiple summary levels
            - Adapt to your preferred writing style
            
            Powered by Groq (Gemma-2, LLaMA-3) for fast, accurate results.
            """)


def render_sidebar():
    """Render sidebar with settings and info"""
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Model selection
        st.subheader("Model Configuration")
        available_models = list(llm_manager.list_available_models().keys())
        selected_model = st.selectbox(
            "Select Model",
            available_models,
            index=available_models.index(settings.default_model),
            help="Choose the AI model for summarization"
        )
        
        # Summary style
        st.subheader("Summary Style")
        style = st.selectbox(
            "Writing Style",
            ["executive", "technical", "simple", "academic", "legal"],
            help="Choose the tone and complexity of summaries"
        )
        
        # Quality preference
        st.subheader("Quality Settings")
        quality = st.select_slider(
            "Quality vs Speed",
            options=["fast", "balanced", "premium"],
            value="balanced",
            help="Higher quality takes more time"
        )
        
        # Advanced settings
        with st.expander("Advanced Settings"):
            chunk_size = st.slider(
                "Chunk Size",
                min_value=500,
                max_value=3000,
                value=settings.chunk_size,
                step=100,
                help="Size of text chunks for processing"
            )
            
            chunk_overlap = st.slider(
                "Chunk Overlap",
                min_value=0,
                max_value=500,
                value=settings.chunk_overlap,
                step=50,
                help="Overlap between chunks for context"
            )
        
        st.divider()
        
        # System info
        st.subheader("📊 System Info")
        model_info = llm_manager.get_model_info(selected_model)
        st.metric("Provider", model_info['provider'].upper())
        st.metric("Speed", model_info['speed'].replace('_', ' ').title())
        st.metric("Quality", model_info['quality'].title())
        st.metric("Cost", "Free" if model_info['cost'] == 'free' else model_info['cost'])
        
        return {
            'model': selected_model,
            'style': style,
            'quality': quality,
            'chunk_size': chunk_size,
            'chunk_overlap': chunk_overlap
        }


def process_document(uploaded_file, settings_dict):
    """Process uploaded document"""
    
    # Save uploaded file temporarily
    temp_path = Path("data/uploads") / uploaded_file.name
    temp_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Process document
    with st.spinner("📖 Processing document..."):
        processed_doc = DocumentProcessorFactory.process_document(temp_path)
        st.session_state.processed_doc = processed_doc
    
    # Chunk document
    with st.spinner("✂️ Chunking document..."):
        chunker = ChunkingEngine(
            chunk_size=settings_dict['chunk_size'],
            chunk_overlap=settings_dict['chunk_overlap']
        )
        chunks = chunker.chunk_document(processed_doc, strategy="smart")
        st.session_state.chunks = chunks
    
    return processed_doc, chunks


def generate_summaries(chunks, total_tokens, settings_dict):
    """Generate all summary levels"""
    
    summarizer = MultiLevelSummarizer(model_name=settings_dict['model'])
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Generate summaries with progress updates
    status_text.text("🤖 Generating TL;DR...")
    progress_bar.progress(25)
    
    summaries = summarizer.generate_all_summaries(
        chunks,
        total_tokens,
        style=settings_dict['style']
    )
    
    progress_bar.progress(100)
    status_text.text("✅ All summaries generated!")
    time.sleep(0.5)
    progress_bar.empty()
    status_text.empty()
    
    return summaries


def render_document_upload():
    """Render document upload section"""
    st.header("📤 Upload Document")
    
    uploaded_file = st.file_uploader(
        "Choose a document",
        type=['pdf', 'docx', 'txt', 'md'],
        help="Supported formats: PDF, DOCX, TXT, Markdown"
    )
    
    if uploaded_file:
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.info(f"📄 **{uploaded_file.name}**")
        
        with col2:
            file_size = len(uploaded_file.getvalue()) / (1024 * 1024)
            st.metric("Size", f"{file_size:.2f} MB")
        
        with col3:
            st.metric("Type", uploaded_file.type.split('/')[-1].upper())
    
    return uploaded_file


def render_document_info(processed_doc, chunks):
    """Render document information"""
    st.header("📊 Document Analysis")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Words", f"{processed_doc.total_words:,}")
    
    with col2:
        st.metric("Characters", f"{processed_doc.total_chars:,}")
    
    with col3:
        st.metric("Sections", len(processed_doc.sections))
    
    with col4:
        st.metric("Chunks", len(chunks))
    
    # Section preview
    with st.expander("📑 Document Structure"):
        for section in processed_doc.sections[:10]:  # Show first 10 sections
            st.markdown(f"**{section.title}** (Level {section.level})")
            st.caption(section.content[:200] + "..." if len(section.content) > 200 else section.content)
            st.divider()


def render_summaries(summaries):
    """Render generated summaries"""
    st.header("📝 Summaries")
    
    # Create tabs for different summary levels
    tabs = st.tabs(["🎯 TL;DR", "📋 Bullet Points", "👔 Executive", "📖 Detailed"])
    
    # TL;DR Tab
    with tabs[0]:
        st.subheader("TL;DR")
        st.info(summaries['tldr'].content)
        
        col1, col2 = st.columns([3, 1])
        with col2:
            st.caption(f"Strategy: {summaries['tldr'].strategy_used}")
            st.caption(f"Model: {summaries['tldr'].model_used}")
    
    # Bullet Points Tab
    with tabs[1]:
        st.subheader("Key Points")
        st.markdown(summaries['bullet'].content)
        
        col1, col2 = st.columns([3, 1])
        with col2:
            st.caption(f"Strategy: {summaries['bullet'].strategy_used}")
            st.caption(f"Model: {summaries['bullet'].model_used}")
    
    # Executive Summary Tab
    with tabs[2]:
        st.subheader("Executive Summary")
        st.markdown(summaries['executive'].content)
        
        col1, col2 = st.columns([3, 1])
        with col2:
            st.caption(f"Strategy: {summaries['executive'].strategy_used}")
            st.caption(f"Model: {summaries['executive'].model_used}")
    
    # Detailed Summary Tab
    with tabs[3]:
        st.subheader("Detailed Analysis")
        st.markdown(summaries['detailed'].content)
        
        col1, col2 = st.columns([3, 1])
        with col2:
            st.caption(f"Strategy: {summaries['detailed'].strategy_used}")
            st.caption(f"Model: {summaries['detailed'].model_used}")


def render_export_options(summaries, filename):
    """Render export options"""
    st.header("💾 Export")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Export all summaries as Markdown
        md_content = f"# Summaries for {filename}\n\n"
        md_content += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        for summary_type, summary in summaries.items():
            md_content += f"## {summary_type.upper()}\n\n"
            md_content += f"{summary.content}\n\n"
            md_content += "---\n\n"
        
        st.download_button(
            "📄 Download Markdown",
            data=md_content,
            file_name=f"{Path(filename).stem}_summaries.md",
            mime="text/markdown"
        )
    
    with col2:
        # Export as plain text
        txt_content = f"SUMMARIES FOR: {filename}\n"
        txt_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        txt_content += "=" * 60 + "\n\n"
        
        for summary_type, summary in summaries.items():
            txt_content += f"{summary_type.upper()}\n"
            txt_content += "-" * 60 + "\n"
            txt_content += f"{summary.content}\n\n"
        
        st.download_button(
            "📝 Download Text",
            data=txt_content,
            file_name=f"{Path(filename).stem}_summaries.txt",
            mime="text/plain"
        )
    
    with col3:
        # Export as JSON
        import json
        json_data = {
            'filename': filename,
            'generated_at': datetime.now().isoformat(),
            'summaries': {
                k: {
                    'content': v.content,
                    'strategy': v.strategy_used,
                    'model': v.model_used
                } for k, v in summaries.items()
            }
        }
        
        st.download_button(
            "🔧 Download JSON",
            data=json.dumps(json_data, indent=2),
            file_name=f"{Path(filename).stem}_summaries.json",
            mime="application/json"
        )


def main():
    """Main application logic"""
    
    # Initialize
    init_session_state()
    
    # Render header
    render_header()
    
    # Render sidebar and get settings
    settings_dict = render_sidebar()
    
    # Main content
    st.divider()
    
    # Document upload
    uploaded_file = render_document_upload()
    
    if uploaded_file:
        # Process button
        if st.button("🚀 Process & Summarize", type="primary", use_container_width=True):
            try:
                # Process document
                processed_doc, chunks = process_document(uploaded_file, settings_dict)
                
                # Calculate total tokens
                chunker = ChunkingEngine()
                total_tokens = sum(chunk.token_count for chunk in chunks)
                
                # Display document info
                st.success("✅ Document processed successfully!")
                render_document_info(processed_doc, chunks)
                
                st.divider()
                
                # Generate summaries
                st.header("🤖 Generating Summaries...")
                summaries = generate_summaries(chunks, total_tokens, settings_dict)
                st.session_state.summaries = summaries
                
            except Exception as e:
                st.error(f"❌ Error processing document: {str(e)}")
                st.exception(e)
    
    # Display summaries if available
    if st.session_state.summaries:
        st.divider()
        render_summaries(st.session_state.summaries)
        
        st.divider()
        render_export_options(st.session_state.summaries, uploaded_file.name)
    
    # Footer
    st.divider()
    st.caption("DocuMind AI | Powered by Groq & LangChain | Built with Streamlit")


if __name__ == "__main__":
    main()
