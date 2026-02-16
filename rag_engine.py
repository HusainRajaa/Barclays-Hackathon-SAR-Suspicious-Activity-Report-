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
*** CONFIDENTIAL SUSPICIOUS ACTIVITY REPORT (SAR) ***
**REPORT STATUS**: DRAFT
**LEGAL DISCLAIMER**: This document contains sensitive financial intelligence.

---

### 1. EXECUTIVE SUMMARY
**Subject**: {alert_data.get('Customer Name')}
**Alert Date**: {alert_data.get('Date')}
**Total Suspicious Amount**: ${alert_data.get('Amount', 0):,.2f}

** Synopsis**:
[Generate a high-level summary of why this behaviour is anomalous. clearly state the primary suspicion (e.g., Structuring, Layering).]

---

### 2. SUBJECT PROFILE & ACCOUNT ACTIVITY
**Customer Name**: {alert_data.get('Customer Name')}
**Transaction Type**: {alert_data.get('Transaction Type')}
**Risk Rating**: {alert_data.get('Risk Score', 'High')}

**Activity Overview**:
The customer executed the following specific transaction(s):
- **Date**: {alert_data.get('Date')}
- **Amount**: ${alert_data.get('Amount', 0):,.2f}
- **Description**: {alert_data.get('Description')}

**Behavioral Analysis**:
[Analyze how this specific transaction deviates from expected behavior for this customer profile. Mention if the volume or frequency is unusual.]

---

### 3. INVESTIGATION FINDINGS & RED FLAGS
The investigation identified the following specific red flags indicative of potential illicit activity:

**Regulatory Indicators Identified**:
{context_text}

**Detailed Analysis of Suspicion**:
[Elaborate on how the transaction details align with the regulatory indicators above. For example, explain *why* the specific amount or pattern constitutes 'Structuring' or 'Layering' under the law. Be verbose and specific.]

---

### 4. LAW ENFORCEMENT SECTION
**Suspected Violation**: Money Laundering / Terrorist Financing
**Recommended Action**: File SAR with Financial Intelligence Unit (FIU).

**Conclusion**:
Based on the convergence of the red flags identified above and the lack of apparent economic rationale, this activity is deemed highly suspicious. We recommend immediate filing and enhanced monitoring of the customer relationship.

---
**Analyst signature**: ______________________
**Date**: {pd.Timestamp.now().strftime('%Y-%m-%d')}
"""
        return sar_draft
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
