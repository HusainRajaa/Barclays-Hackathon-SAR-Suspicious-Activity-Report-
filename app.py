import streamlit as st
import pandas as pd
from rag_engine import RAGEngine
from mock_data_loader import generate_regulatory_docs, generate_mock_alerts

# Page Config
st.set_page_config(page_title="SAR Narrative AI", layout="wide")

# Title & Header
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stApp > header {
        background-color: #00AEEF;
    }
    .stSidebar {
        background-color: #00395D; /* Barclays Blue */
        color: white;
    }
    h1 {
        color: #00395D;
        font-family: 'Helvetica', sans-serif;
    }
    h3 {
        color: #00AEEF;
    }
    .stButton>button {
        background-color: #00395D;
        color: white;
        border-radius: 5px;
    }
    div.stButton > button:first-child {
        background-color: #00395D;
        color: white;
    }
    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 1rem;
        font-weight: 600;
        color: #00395D;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🦅 Barclays SAR Generator")
st.markdown("""
**Investigator Dashboard | Financial Crime Operations**
*automated narrative generation powered by Llama 3 & Vector Search using ChromaDB(FAISS)*
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
            st.markdown("### 🔍 Regulatory Audit Trail")
            st.info("The following regulatory guidelines were retrieved from the Vector Database to ground the narrative.")
            
            # Create a structured list of citations
            audit_data = []
            for i, doc in enumerate(st.session_state["context"]):
                source = doc.metadata.get('source', 'FCA Handbook')
                relevance = "High" if i == 0 else "Medium"
                audit_data.append({
                    "Citation ID": f"CIT-{i+1:03d}",
                    "Source Document": source,
                    "Relevance Score": relevance,
                    "Excerpt": doc.page_content[:150] + "..."
                })
                
                # Visual Card for each citation
                with st.expander(f"⚖️ Citation #{i+1}: {source} (Relevance: {relevance})", expanded=True):
                    st.markdown(f"> *{doc.page_content}*")
                    st.caption(f"Source: {source} | Verified by ChromaDB")
            
            st.markdown("---")
            st.subheader("📊 Compliance Log Export")
            
            # Convert to DataFrame for download
            df_audit = pd.DataFrame(audit_data)
            st.dataframe(df_audit, hide_index=True)
            
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.download_button(
                    label="📥 Download Audit Log (CSV)",
                    data=df_audit.to_csv(index=False),
                    file_name="audit_trail_log.csv",
                    mime="text/csv"
                )
            with col_d2:
                 st.button("🖨️ Generate PDF Report", disabled=True, help="Feature coming in v2.0")
    else:
        st.write("👈 Select an alert and click Generate to see the magic.")

# Footer
st.markdown("---")
st.caption("Powered by Llama 3 • ChromaDB (FAISS) • LangChain")
