"""
Configuration management for DocuMind AI
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    groq_api_key: str = Field(default="", env="GROQ_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    serpapi_api_key: Optional[str] = Field(default=None, env="SERPAPI_API_KEY")
    
    # Model Configuration
    default_model: str = Field(default="gemma2-9b-it", env="DEFAULT_MODEL")
    premium_model: str = Field(default="llama-3.1-70b-versatile", env="PREMIUM_MODEL")
    fast_model: str = Field(default="llama-3.1-8b-instant", env="FAST_MODEL")
    
    # Ollama Configuration
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="mixtral:8x7b", env="OLLAMA_MODEL")
    
    # Document Processing
    max_file_size_mb: int = Field(default=50, env="MAX_FILE_SIZE_MB")
    max_pages: int = Field(default=1000, env="MAX_PAGES")
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    
    # Summarization Settings
    default_strategy: str = Field(default="auto", env="DEFAULT_STRATEGY")
    enable_section_detection: bool = Field(default=True, env="ENABLE_SECTION_DETECTION")
    enable_table_extraction: bool = Field(default=True, env="ENABLE_TABLE_EXTRACTION")
    
    # Storage
    storage_type: str = Field(default="local", env="STORAGE_TYPE")
    s3_bucket_name: Optional[str] = Field(default=None, env="S3_BUCKET_NAME")
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    
    # Database
    database_url: str = Field(default="sqlite:///./documind.db", env="DATABASE_URL")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    enable_cache: bool = Field(default=True, env="ENABLE_CACHE")
    cache_ttl_hours: int = Field(default=24, env="CACHE_TTL_HOURS")
    
    # Rate Limiting
    daily_document_limit: int = Field(default=50, env="DAILY_DOCUMENT_LIMIT")
    daily_summary_limit: int = Field(default=200, env="DAILY_SUMMARY_LIMIT")
    max_concurrent_jobs: int = Field(default=5, env="MAX_CONCURRENT_JOBS")
    
    # Feature Flags
    enable_multi_document: bool = Field(default=True, env="ENABLE_MULTI_DOCUMENT")
    enable_search_agent: bool = Field(default=True, env="ENABLE_SEARCH_AGENT")
    enable_version_comparison: bool = Field(default=True, env="ENABLE_VERSION_COMPARISON")
    enable_export: bool = Field(default=True, env="ENABLE_EXPORT")
    
    # Monitoring
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    enable_analytics: bool = Field(default=False, env="ENABLE_ANALYTICS")
    
    # UI Configuration
    app_title: str = Field(default="DocuMind AI", env="APP_TITLE")
    app_subtitle: str = Field(default="Enterprise-grade AI Summarization Platform", env="APP_SUBTITLE")
    theme: str = Field(default="dark", env="THEME")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Project paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
PROCESSED_DIR = DATA_DIR / "processed"
SUMMARY_DIR = DATA_DIR / "summaries"

# Create directories if they don't exist
for directory in [DATA_DIR, UPLOAD_DIR, PROCESSED_DIR, SUMMARY_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Global settings instance
settings = Settings()


# Model configurations
MODEL_CONFIGS = {
    "gemma2-9b-it": {
        "provider": "groq",
        "context_window": 8192,
        "speed": "fast",
        "quality": "good",
        "cost": "free"
    },
    "llama-3.1-70b-versatile": {
        "provider": "groq",
        "context_window": 8192,
        "speed": "medium",
        "quality": "excellent",
        "cost": "free"
    },
    "llama-3.1-8b-instant": {
        "provider": "groq",
        "context_window": 8192,
        "speed": "very_fast",
        "quality": "good",
        "cost": "free"
    },
    "mixtral:8x7b": {
        "provider": "ollama",
        "context_window": 32768,
        "speed": "slow",
        "quality": "excellent",
        "cost": "free_local"
    }
}


# Strategy selection thresholds
STRATEGY_THRESHOLDS = {
    "stuff": {
        "max_tokens": 4000,
        "description": "Single pass - for short documents"
    },
    "map_reduce": {
        "min_tokens": 4000,
        "max_tokens": 100000,
        "description": "Parallel processing - default for long documents"
    },
    "refine": {
        "min_tokens": 4000,
        "description": "Iterative refinement - premium quality"
    }
}


# Summary level configurations
SUMMARY_LEVELS = {
    "tldr": {
        "max_length": 150,
        "style": "concise",
        "description": "1-2 sentence overview"
    },
    "bullet": {
        "max_bullets": 7,
        "style": "structured",
        "description": "Key points in bullet format"
    },
    "executive": {
        "max_length": 500,
        "style": "professional",
        "description": "Executive overview with context"
    },
    "detailed": {
        "max_length": 2000,
        "style": "comprehensive",
        "description": "Detailed analysis with structure"
    }
}


# Summary styles
SUMMARY_STYLES = {
    "technical": "Technical and precise language, assumes expert knowledge",
    "simple": "Clear and simple language, suitable for general audience",
    "executive": "Professional business language, focus on key insights",
    "academic": "Scholarly tone, formal language with proper citations",
    "legal": "Formal legal language, precise terminology"
}
