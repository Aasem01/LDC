from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_community.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from typing import List, Dict
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline, AutoModelForCausalLM
import torch
from app.core.config import settings
from app.services.embedding_service import embedding_service
from app.services.db_service import db_service
from app.utils.logger import rag_logger
from langchain_community.llms import HuggingFaceEndpoint




class RAGService:
    _instance = None
    _llm = None
    _qa_chain = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RAGService, cls).__new__(cls)
            rag_logger.info("Creating new RAGService instance")
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            rag_logger.info("Initializing RAGService")
            self._initialize_llm()
            self.initialized = True

    def _initialize_llm(self):
        """Initialize the language model"""
        rag_logger.info(f"Using {settings.USE_HUGGINGFACE} model")
        if settings.USE_HUGGINGFACE:
            rag_logger.info("Using Hugging Face model")
            self._setup_huggingface_llm()
        else:
            rag_logger.info("Using OpenAI model")
            self._setup_openai_llm()

    def _setup_huggingface_llm(self):
        """
        Set up the Hugging Face model using pipeline.
        """
        rag_logger.info(f"Setting up Hugging Face model: {settings.HUGGINGFACE_DEEPSEEK_MODEL_NAME}")
        
        try:
            # Initialize tokenizer and model with authentication
            tokenizer = AutoTokenizer.from_pretrained(
                settings.HUGGINGFACE_DEEPSEEK_MODEL_NAME,
                token=settings.HUGGINGFACE_API_KEY,
            )
            
            model = AutoModelForCausalLM.from_pretrained(
                settings.HUGGINGFACE_DEEPSEEK_MODEL_NAME,
                token=settings.HUGGINGFACE_API_KEY,
                torch_dtype=torch.bfloat16,
                device_map="auto"
            )

            # Create pipeline
            pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_length=512,
                temperature=0.7,
                top_p=0.95,
                repetition_penalty=1.15,
                do_sample=True,
            )
            
            # Create LangChain wrapper
            self._llm = HuggingFacePipeline(pipeline=pipe)
            rag_logger.info("Successfully initialized Hugging Face pipeline")
            
            # Test the endpoint with a simple prompt
            test_response = self._llm.invoke("Hello")
            if not test_response:
                raise ValueError("Empty response from Hugging Face endpoint")
            rag_logger.info("Successfully initialized Hugging Face Endpoint")
        except Exception as e:
            rag_logger.error(f"Error setting up Hugging Face endpoint: {str(e)}")
            raise

    def _setup_openai_llm(self):
        """Set up the OpenAI model"""
        try:
            self._llm = ChatOpenAI(
                model="deepseek-chat",
                openai_api_key=settings.DEEPSEEK_API_KEY,
                base_url="https://api.deepseek.com",
                temperature=0.1,
                streaming=False,
            )
            rag_logger.info("Successfully initialized OpenAI model")
        except Exception as e:
            rag_logger.error(f"Error setting up OpenAI model: {str(e)}")
            raise

    def _initialize_qa_chain(self):
        """Initialize the QA chain"""
        if self._qa_chain is None:
            rag_logger.info("Initializing QA chain")
            try:
                vector_store = db_service.get_vector_store()
                
                prompt_template = PromptTemplate(
                    template="""You are a helpful AI assistant. Use the following pieces of context to answer the question at the end.
                    If you don't know the answer, just say that you don't know, don't try to make up an answer.
                    
                    Context: {context}
                    
                    Question: {question}
                    
                    Answer:""",
                    input_variables=["context", "question"]
                )

                self._qa_chain = RetrievalQA.from_chain_type(
                    llm=self._llm,
                    chain_type="stuff",
                    retriever=vector_store.as_retriever(),
                    return_source_documents=True,
                    chain_type_kwargs={"prompt": prompt_template}
                )
                rag_logger.info("Successfully initialized QA chain")
            except Exception as e:
                rag_logger.error(f"Error initializing QA chain: {str(e)}")
                raise

    async def get_answer(self, question: str) -> Dict:
        """
        Get answer for a question using the RAG pipeline.
        
        Args:
            question (str): Question to answer
            
        Returns:
            Dict: Answer and source documents
        """
        rag_logger.info(f"Processing question: {question}")
        
        if not self._qa_chain:
            self._initialize_qa_chain()
            
        try:
            if not question or not question.strip():
                raise ValueError("Question cannot be empty")
                
            # Use ainvoke for async operation
            result = await self._qa_chain.ainvoke({"query": question})
            
            if not result or "result" not in result:
                raise ValueError("Invalid response format from QA chain")
                
            rag_logger.info("Successfully generated answer")
            rag_logger.info(f"Answer: {result['result']}")
            rag_logger.info(f"Found {len(result['source_documents'])} relevant documents")
            
            # Format source documents according to schema
            source_docs = [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in result["source_documents"]
            ]
            
            return {
                "answer": result["result"],
                "source_documents": source_docs
            }
        except ValueError as ve:
            rag_logger.error(f"Validation error: {str(ve)}")
            raise
        except Exception as e:
            rag_logger.error(f"Error generating answer: {str(e)}")
            raise

# Initialize services once
rag_service = RAGService()
