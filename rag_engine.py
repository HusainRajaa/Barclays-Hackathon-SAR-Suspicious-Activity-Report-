import os
import sys

try:
    from langchain_community.vectorstores import FAISS
    from langchain_huggingface import HuggingFaceEmbeddings
    # Modern imports for LangChain 0.2+
    from langchain_text_splitters import CharacterTextSplitter
    from langchain_core.documents import Document
except ImportError as e:
    # Fallback/Debug
    print(f"Import Error: {e}")
    print("Trying legacy imports...")
    try:
        from langchain.vectorstores import FAISS
        from langchain.embeddings import HuggingFaceEmbeddings
        from langchain.text_splitter import CharacterTextSplitter
        from langchain.docstore.document import Document
    except ImportError as e2:
        print(f"Legacy Import Error: {e2}")
        print("Please ensure requirements are installed: pip install langchain langchain-community langchain-huggingface faiss-cpu sentence-transformers")
        sys.exit(1)

import pandas as pd

# Global variables for the engine
VECTOR_DB_PATH = "./faiss_index"

class RAGEngine:
    def __init__(self):
        print("Initializing RAG Engine (FAISS)...")
        # Use a lightweight local embedding model (runs on CPU/Mac M1)
        # Using HuggingFaceEmbeddings from langchain_huggingface (or community)
        try:
             self.embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        except Exception:
             from langchain_community.embeddings import HuggingFaceEmbeddings
             self.embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
             
        self.vector_db = None
        print("RAG Engine Initialized.")

    def ingest_data(self, documents: list[str]):
        """
        Ingests a list of text strings (regulatory rules) into the Vector DB.
        """
        print(f"Ingesting {len(documents)} documents...")
        
        # Convert strings to LangChain Documents
        docs = [Document(page_content=d, metadata={"source": "FCA Manual"}) for d in documents]
        
        # Split text
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=0)
        split_docs = text_splitter.split_documents(docs)
        
        # Create FAISS index
        self.vector_db = FAISS.from_documents(split_docs, self.embedding_function)
        
        # Save locally
        self.vector_db.save_local(VECTOR_DB_PATH)
        print("Ingestion Complete. Index saved.")

    def load_index(self):
        """Loads the FAISS index from disk."""
        if os.path.exists(VECTOR_DB_PATH):
             self.vector_db = FAISS.load_local(
                 VECTOR_DB_PATH, 
                 self.embedding_function, 
                 allow_dangerous_deserialization=True
             )
             print("Loaded existing FAISS index.")
        else:
            print("No existing index found. Please ingest data first.")
        return self.vector_db

    def retrieve_context(self, query: str, k: int = 2):
        """
        Retrieves top-k relevant rules.
        """
        if not self.vector_db:
            self.load_index()
            
        print(f"Retrieving context for: '{query}'")
        if self.vector_db:
            results = self.vector_db.similarity_search(query, k=k)
            return results
        return []

    def generate_sar_narrative(self, alert_data: dict, context_docs: list):
        """
        Generates the SAR narrative template.
        """
        context_text = "\n".join([f"- {d.page_content}" for d in context_docs])
        
        sar_draft = f"""
*** GENERATED SAR NARRATIVE ***

[INTRODUCTION]
Based on the review of account activity for customer {alert_data.get('Customer Name')}, a series of transactions executed on {alert_data.get('Date')} were flagged as potential suspicious activity.

[TRANSACTION DETAILS]
The customer initiated a {alert_data.get('Transaction Type')} of ${alert_data.get('Amount')}. 
Specific details: {alert_data.get('Description')}

[REGULATORY CONTEXT & REASONING]
This activity has been flagged in accordance with the following regulatory indicators:
{context_text}

[CONCLUSION]
Due to the alignment with the above indicators, this activity is deemed suspicious and is being reported for further investigation.
"""
        return sar_draft

if __name__ == "__main__":
    # Test Run
    try:
        from mock_data_loader import generate_regulatory_docs, generate_mock_alerts
    except ImportError:
        def generate_regulatory_docs(): return ["Rule A: Test Rule"]
        def generate_mock_alerts(): return pd.DataFrame([{"Description": "Test Alert", "Customer Name": "Test User", "Date": "2023-01-01", "Amount": 100, "Transaction Type": "Test"}])

    engine = RAGEngine()
    
    # 1. Ingest
    docs = generate_regulatory_docs()
    engine.ingest_data(docs)
    
    # 2. Retrieve & Generate
    alerts = generate_mock_alerts()
    if not alerts.empty:
        test_alert = alerts.iloc[0].to_dict()
        
        query = test_alert.get("Description", "Suspicious activity")
        context = engine.retrieve_context(query)
        
        print(f"\n--- Retrieved Context ({len(context)}) ---")
        for c in context:
            print(f"[Rule Match]: {c.page_content}")
            
        # 3. Generate
        sar = engine.generate_sar_narrative(test_alert, context)
        print(f"\n{sar}")
    else:
        print("No alerts to process.")
