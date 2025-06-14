from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from langchain.schema import Document

class IVectorStore(ABC):
    """Interface for vector store operations"""
    @abstractmethod
    def add_documents(self, documents: List[Document]) -> None:
        pass

    @abstractmethod
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        pass

    @abstractmethod
    def get_all_documents(self) -> List[Dict]:
        pass

    @abstractmethod
    def delete_document(self, document_id: str) -> None:
        pass

    @abstractmethod
    def delete_all(self) -> None:
        pass

class IEmbeddingModel(ABC):
    """Interface for embedding model operations"""
    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        pass

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        pass

class ILLM(ABC):
    """Interface for Language Model operations"""
    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass

    @abstractmethod
    def stream_generate(self, prompt: str):
        pass

class IDocumentProcessor(ABC):
    """Interface for document processing operations"""
    @abstractmethod
    def split_documents(self, documents: List[Document]) -> List[Document]:
        pass

    @abstractmethod
    def process_document(self, document: Document) -> List[Document]:
        pass

class IRAGService(ABC):
    """Interface for RAG operations"""
    @abstractmethod
    async def get_answer(self, question: str) -> Dict:
        pass

    @abstractmethod
    def add_document(self, document: Document) -> None:
        pass

class IConfiguration(ABC):
    """Interface for configuration management"""
    @abstractmethod
    def get_setting(self, key: str) -> any:
        pass

    @abstractmethod
    def validate(self) -> bool:
        pass 