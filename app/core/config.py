from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache
from pydantic import Field
from app.utils.logger import api_logger
import os
from pathlib import Path

class AppSettings(BaseSettings):
    """Application settings"""
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Security Settings
    ALLOWED_ORIGINS: List[str] = ["http://127.0.0.1:7000", "http://localhost:7000", "testclient"]
    
    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL_NAME: str = "deepseek-chat"
    OPENAI_API_BASE: str = "https://api.deepseek.com"

    # Hugging Face Settings
    HUGGINGFACE_API_KEY: Optional[str] = None
    HUGGINGFACE_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    USE_HUGGINGFACE: bool = True
    
    # DeepSeek Settings
    DEEPSEEK_API_KEY: Optional[str] = None
    HF_DEEPSEEK_MODEL_NAME: str = "deepseek-ai/deepseek-coder-6.7b-base"
    
    # Model Settings
    LLM_MODEL_NAME: str = "mistralai/Mistral-7B-Instruct-v0.2"
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    
    # Vector Store Settings
    CHROMA_PERSIST_DIRECTORY: str = "data/chroma"
    
    # Document Processing Settings
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100
    RAW_DOCUMENTS_DIR: str = "data/raw"
    
    # API Keys
    API_KEY: str = Field(default="", description="API key for OpenAI")

    # Database URL (for SQLAlchemy)
    DATABASE_URL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True
    
    def __init__(self, **kwargs):
        # Get the project root directory
        project_root = Path(__file__).parent.parent.parent
        env_path = project_root / ".env"
        
        # Log the .env file path
        api_logger.info(f"Looking for .env file at: {env_path}")
        
        if not env_path.exists():
            api_logger.warning(f".env file not found at {env_path}")
        
        super().__init__(_env_file=str(env_path), **kwargs)
        api_logger.info("Loading settings from environment variables...")
        api_logger.info(f"API_KEY: {'*' * 8}{self.API_KEY[-4:] if self.API_KEY else 'Not set'}")
        api_logger.info(f"DEEPSEEK_API_KEY: {'*' * 8}{self.DEEPSEEK_API_KEY[-4:] if self.DEEPSEEK_API_KEY else 'Not set'}")
        api_logger.info(f"USE_HUGGINGFACE: {self.USE_HUGGINGFACE}")
        api_logger.info(f"OPENAI_MODEL_NAME: {self.OPENAI_MODEL_NAME}")
        api_logger.info(f"HF_DEEPSEEK_MODEL_NAME: {self.HF_DEEPSEEK_MODEL_NAME}")
        api_logger.info(f"OPENAI_API_BASE: {self.OPENAI_API_BASE}")
        api_logger.info(f"ALLOWED_ORIGINS: {self.ALLOWED_ORIGINS}")
        self.validate_api_keys()
    
    def validate_api_keys(self):
        """Validate that required API keys are present"""
        if self.USE_HUGGINGFACE and not self.DEEPSEEK_API_KEY:
            raise ValueError("DEEPSEEK_API_KEY is required when using HuggingFace models")
        if not self.USE_HUGGINGFACE and not self.API_KEY:
            raise ValueError("API_KEY is required when using OpenAI models")

    def validate(self) -> None:
        """Validate required settings"""
        if not self.API_KEY:
            raise ValueError("API_KEY is required")
        
        if self.USE_HUGGINGFACE and not self.HUGGINGFACE_API_KEY:
            raise ValueError("HUGGINGFACE_API_KEY is required when using Hugging Face models")
        
        if not self.USE_HUGGINGFACE and not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required when not using Hugging Face models")

class Configuration:
    """Configuration manager implementing singleton pattern"""
    _instance = None
    _settings = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Configuration, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._settings is None:
            api_logger.info("Initializing Configuration singleton...")
            self._settings = AppSettings()
            api_logger.info("Configuration initialized successfully")
            self._settings.validate()  # Validate settings on initialization

    @property
    def settings(self) -> AppSettings:
        """Get the settings instance"""
        return self._settings

    @classmethod
    def get_instance(cls) -> 'Configuration':
        """Get the singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

# Create singleton instance
configuration = Configuration.get_instance()

# For backward compatibility and convenience
settings = configuration.settings