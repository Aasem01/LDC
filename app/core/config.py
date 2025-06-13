from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Settings
    API_HOST: str = os.getenv("API_HOST", "127.0.0.1")
    API_PORT: int = int(os.getenv("API_PORT", "9000"))
    
    # Security Settings
    API_KEY: str = os.getenv("API_KEY", "SElIKLEvUEB9cY6HG8cXQqJYHRqYJHNoIAXGs7FdkwY")
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "http://127.0.0.1:7000/").split(",")
    
    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Hugging Face Settings
    HUGGINGFACE_API_KEY: Optional[str] = os.getenv("HUGGINGFACE_API_KEY")
    # LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "google/flan-t5-base")
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "mistralai/Mistral-7B-Instruct-v0.2")
    USE_HUGGINGFACE: bool = os.getenv("USE_HUGGINGFACE", "True").lower() == "true"
    
    HUGGINGFACE_DEEPSEEK_MODEL_NAME: str = os.getenv("HF_DEEPSEEK_MODEL_NAME", "deepseek-ai/deepseek-llm-7b-chat")

    # Vector Store Settings
    CHROMA_PERSIST_DIRECTORY: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/chroma_db")
    
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY")

    # Document Processing Settings
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "100"))
    
    # Model Settings
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

    class Config:
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings() 

settings = get_settings()