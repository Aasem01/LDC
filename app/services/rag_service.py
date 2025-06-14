from typing import Dict, List
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from app.core.interfaces import IRAGService, IConfiguration, IVectorStore, ILLM
from app.core.base_service import BaseService
from app.utils.logger import api_logger

class RAGService(BaseService, IRAGService):
    """Service for handling RAG operations"""
    _instance = None
    
    def __new__(cls, config: IConfiguration, vector_store: IVectorStore, llm: ILLM):
        if cls._instance is None:
            cls._instance = super(RAGService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, config: IConfiguration, vector_store: IVectorStore, llm: ILLM):
        if not hasattr(self, 'initialized'):
            super().__init__(config, "rag_service")
            self._vector_store = vector_store
            self._llm = llm
            self._qa_chain = None
    
    def _initialize(self) -> None:
        """Initialize the RAG service"""
        try:
            self.logger.info("Initializing QA chain")
            self._setup_qa_chain()
            self.logger.info("Successfully initialized QA chain")
        except Exception as e:
            self.logger.error(f"Error initializing RAG service: {str(e)}")
            raise
    
    def _setup_qa_chain(self) -> None:
        """Set up the QA chain"""
        prompt_template = PromptTemplate(
            template="""You are a helpful AI assistant. Use the following pieces of context to answer the question at the end.
            If you don't know the answer, just say that you don't know, don't try to make up an answer.
            
            Context: {context}
            
            Question: {question}
            
            Answer:""",
            input_variables=["context", "question"]
        )

        self._qa_chain = RetrievalQA.from_chain_type(
            llm=self._llm.model,
            chain_type="stuff",
            retriever=self._vector_store.as_retriever(),
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt_template}
        )
    
    def _shutdown(self) -> None:
        """Clean up resources"""
        self._qa_chain = None
    
    async def get_answer(self, question: str) -> Dict:
        """Get answer for a question using the RAG pipeline"""
        if not self.is_initialized:
            raise RuntimeError("RAGService not initialized")
        
        self.logger.info(f"Processing question: {question}")
        
        try:
            if not question or not question.strip():
                raise ValueError("Question cannot be empty")
                
            # Use ainvoke for async operation
            result = await self._qa_chain.ainvoke({"query": question})
            
            if not result or "result" not in result:
                raise ValueError("Invalid response format from QA chain")
                
            self.logger.info("Successfully generated answer")
            self.logger.info(f"Answer: {result['result']}")
            self.logger.info(f"Found {len(result['source_documents'])} relevant documents")
            
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
            self.logger.error(f"Validation error: {str(ve)}")
            raise
        except Exception as e:
            self.logger.error(f"Error generating answer: {str(e)}")
            raise
    
    def add_document(self, document: Document) -> None:
        """Add a document to the RAG system"""
        if not self.is_initialized:
            raise RuntimeError("RAGService not initialized")
        self._vector_store.add_documents([document])
