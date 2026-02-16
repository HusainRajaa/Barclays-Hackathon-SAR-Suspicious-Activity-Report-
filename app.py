import streamlit as st
import pandas as pd
from rag_engine import RAGEngine
from mock_data_loader import generate_regulatory_docs, generate_mock_alerts

# Page Config
st.set_page_config(page_title="SAR Narrative AI", layout="wide")

# Title & Header
st.title("🛡️ AI-Powered SAR Narrative Generator")
st.markdown("""
**Automating Suspicious Activity Reports with Active Learning & RAG**
*Retrieves regulatory context -> Generates Audit-Ready Narratives*
""")

# Initialize Engine (Cached)
@st.cache_resource
def load_engine():
    engine = RAGEngine()
    # Pre-ingest data for demo purposes
    docs = generate_regulatory_docs()
    engine.ingest_data(docs)
    return engine

try:
    engine = load_engine()
    st.success("✅ RAG Engine & Vector DB Ready")
except Exception as e:
    st.error(f"Failed to load engine: {e}")
    st.stop()

# Sidebar: Select Alert
st.sidebar.header("🔍 Alert Dashboard")
alerts = generate_mock_alerts()

# Select box for alert
alert_options = alerts["AlertID"] + " - " + alerts["Customer Name"]
selected_option = st.sidebar.selectbox("Select Pending Alert", alert_options)

# Get selected alert data
selected_alert_idx = alert_options.tolist().index(selected_option)
current_alert = alerts.iloc[selected_alert_idx].to_dict()

# Main Layout
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 Transaction Details")
    st.info(f"**Customer**: {current_alert['Customer Name']}")
    st.write(f"**Type**: {current_alert['Transaction Type']}")
    st.write(f"**Amount**: ${current_alert['Amount']:,.2f}")
    st.write(f"**Date**: {current_alert['Date']}")
    st.warning(f"**Risk Flag**: {current_alert['Description']}")

    st.markdown("---")
    if st.button("🚀 Generate SAR Narrative", type="primary"):
        with st.spinner("Consulting Vector DB & Generating Narrative..."):
            # 1. Retrieve Context
            query = current_alert["Description"]
            context = engine.retrieve_context(query)
            
            # 2. Generate SAR
            sar_narrative = engine.generate_sar_narrative(current_alert, context)
            
            # Store in session state to persist
            st.session_state["sar"] = sar_narrative
            st.session_state["context"] = context

with col2:
    st.subheader("📝 Generated Output")
    
    if "sar" in st.session_state:
        # Tabs for Narrative and Audit Trail
        tab1, tab2 = st.tabs(["📄 Narrative", "🔍 Audit Trail (Context)"])
        
        with tab1:
            st.text_area("Final SAR Draft", st.session_state["sar"], height=300)
            st.button("Total Submit to FinCEN", disabled=True)
            
        with tab2:
            st.write("The AI used the following regulations to justify the report:")
            for i, doc in enumerate(st.session_state["context"]):
                with st.expander(f"Citation #{i+1}: {doc.metadata.get('source', 'Regulation')}"):
                    st.write(doc.page_content)
    else:
        st.write("👈 Select an alert and click Generate to see the magic.")

# Footer
st.markdown("---")
st.caption("Powered by Llama 3 • ChromaDB (FAISS) • LangChain")
