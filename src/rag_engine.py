import chromadb
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import FakeEmbeddings # Using Fake functionality for POC to avoid API keys complexity or heavy local models
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import Document
import os

class RAGEngine:
    def __init__(self, collection_name="sar_guidelines"):
        # Connect to Dockerized ChromaDB
        self.client = chromadb.HttpClient(host='localhost', port=8000)
        self.collection_name = collection_name
        # For a real app, use OpenAIEmbeddings or HuggingFaceEmbeddings
        self.embeddings = FakeEmbeddings(size=4096) 
        self.vector_store = Chroma(
            client=self.client,
            collection_name=collection_name,
            embedding_function=self.embeddings
        )

    def ingest_guidelines(self, file_path: str):
        """Loads regulatory guidelines into the vector store."""
        with open(file_path, 'r') as f:
            text = f.read()
        
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_text(text)
        
        documents = [Document(page_content=chunk, metadata={"source": file_path}) for chunk in chunks]
        
        self.vector_store.add_documents(documents)
        print(f"Ingested {len(documents)} chunks from {file_path}")

    def retrieve_context(self, query: str, k: int = 3) -> list:
        """Retrieves relevant guidelines for a given query."""
        docs = self.vector_store.similarity_search(query, k=k)
        return docs

if __name__ == "__main__":
    # Test RAG
    rag = RAGEngine()
    rag.ingest_guidelines("data/regulations/sample_guidelines.txt")
    results = rag.retrieve_context("structuring and wire transfers")
    for doc in results:
        print(f"Content: {doc.page_content[:100]}...")
