from typing import Optional, Generator
from langchain_openai import ChatOpenAI
from langchain_community.llms import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
from app.core.interfaces import ILLM, IConfiguration
from app.core.base_service import BaseService
from app.utils.logger import api_logger

class LLMService(BaseService, ILLM):
    """Service for handling language model operations"""
    _instance = None
    
    def __new__(cls, config: IConfiguration):
        if cls._instance is None:
            cls._instance = super(LLMService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, config: IConfiguration):
        if not hasattr(self, 'initialized'):
            super().__init__(config, "llm_service")
            self._model = None
    
    def _initialize(self) -> None:
        """Initialize the language model"""
        try:
            self.logger.info("Initializing language model")
            if self.config.settings.USE_HUGGINGFACE:
                self._setup_huggingface_llm()
            else:
                self._setup_openai_llm()
            self.logger.info("Successfully initialized language model")
        except Exception as e:
            self.logger.error(f"Error initializing language model: {str(e)}")
            raise
    
    def _setup_huggingface_llm(self) -> None:
        """Set up Hugging Face model"""
        try:
            self.logger.info("Setting up Hugging Face model")
            model_name = self.config.settings.HF_DEEPSEEK_MODEL_NAME
            api_key = self.config.settings.DEEPSEEK_API_KEY
            
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            
            pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=512,
                temperature=0.7,
                top_p=0.95,
                repetition_penalty=1.15
            )
            
            self._model = HuggingFacePipeline(pipeline=pipe)
            self.logger.info("Successfully initialized Hugging Face model")
        except Exception as e:
            self.logger.error(f"Error setting up Hugging Face model: {str(e)}")
            raise
    
    def _setup_openai_llm(self) -> None:
        """Set up OpenAI model"""
        try:
            self.logger.info("Setting up OpenAI model")
            self._model = ChatOpenAI(
                model_name=self.config.settings.OPENAI_MODEL_NAME,
                openai_api_key=self.config.settings.DEEPSEEK_API_KEY,
                openai_api_base=self.config.settings.OPENAI_API_BASE,
                temperature=0.7,
                streaming=True
            )
            self.logger.info("Successfully initialized OpenAI model")
        except Exception as e:
            self.logger.error(f"Error setting up OpenAI model: {str(e)}")
            raise
    
    def _shutdown(self) -> None:
        """Clean up resources"""
        self._model = None
    
    def generate(self, prompt: str) -> str:
        """Generate text from a prompt"""
        if not self.is_initialized:
            raise RuntimeError("LLMService not initialized")
        return self._model.invoke(prompt)
    
    def stream_generate(self, prompt: str) -> Generator[str, None, None]:
        """Stream generate text from a prompt"""
        if not self.is_initialized:
            raise RuntimeError("LLMService not initialized")
        for chunk in self._model.stream(prompt):
            yield chunk
    
    @property
    def model(self) -> ChatOpenAI | HuggingFacePipeline:
        """Get the language model"""
        if not self.is_initialized:
            raise RuntimeError("LLMService not initialized")
        return self._model 