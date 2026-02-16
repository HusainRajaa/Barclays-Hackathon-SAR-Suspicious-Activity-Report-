import streamlit as st
import pandas as pd
import graphviz
from rag_engine import RAGEngine
from mock_data_loader import generate_regulatory_docs, generate_mock_alerts

# Page Config
st.set_page_config(page_title="Barclays SAR Generator", layout="wide")

# Custom CSS for Professional Look (No Emojis)
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stApp > header {
        background-color: #00AEEF;
    }
    .stSidebar {
        background-color: #00395D;
        color: white;
    }
    h1, h2, h3 {
        color: #00395D;
        font-family: 'Helvetica', sans-serif;
    }
    .stButton>button {
        background-color: #00395D;
        color: white;
        border-radius: 4px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #00AEEF;
        color: white;
    }
    .nav-btn {
        margin: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize Engine (Cached)
@st.cache_resource
def load_engine():
    engine = RAGEngine()
    docs = generate_regulatory_docs()
    engine.ingest_data(docs)
    return engine

try:
    engine = load_engine()
except Exception as e:
    st.error(f"Failed to load engine: {e}")
    st.stop()

# Navigation State
if 'page' not in st.session_state:
    st.session_state.page = 'Generator'

def set_page(page_name):
    st.session_state.page = page_name

# Top Navigation Bar
col_nav1, col_nav2, col_nav3 = st.columns(3)
with col_nav1:
    if st.button("SAR Generator", use_container_width=True):
        set_page('Generator')
with col_nav2:
    if st.button("RAG Architecture Details", use_container_width=True):
        set_page('RAG Architecture')
with col_nav3:
    if st.button("ML Model Logic", use_container_width=True):
        set_page('ML Model')

st.markdown("---")

# --- PAGE 1: SAR GENERATOR ---
if st.session_state.page == 'Generator':
    st.title("Barclays SAR Narrative Generator")
    st.markdown("Automated generation of Suspicious Activity Reports using Llama 3 and Vector Search.")

    # Sidebar for Input Method
    st.sidebar.header("Input Controls")
    input_method = st.sidebar.radio("Select Input Method:", ("Upload Transaction File", "Manual Entry"))

    alert_data = {}

    if input_method == "Upload Transaction File":
        uploaded_file = st.sidebar.file_uploader("Upload CSV File", type=["csv"])
        
        # Download Sample Template
        sample_data = pd.DataFrame([{
            "Customer Name": "John Smith",
            "Transaction Type": "Cash Deposit", 
            "Amount": 9500,
            "Date": "2023-10-25",
            "Description": "Customer made 3 separate cash deposits of $9,500, $9,000, and $8,500 in consecutive days."
        }])
        csv = sample_data.to_csv(index=False)
        st.sidebar.download_button("⬇️ Download Sample CSV", csv, "sample_sar_data.csv", "text/csv")

        if uploaded_file is not None:
            try:
                alerts = pd.read_csv(uploaded_file)
                st.sidebar.success(f"✅ Loaded {len(alerts)} records")
                
                # Validation
                required_cols = ["Customer Name", "Description", "Amount"]
                missing_cols = [col for col in required_cols if col not in alerts.columns]
                
                if missing_cols:
                    st.error(f"CSV missing columns: {', '.join(missing_cols)}")
                else:
                    # Select Specific Transaction
                    # Create a standard list for dropdown
                    options = [f"Row {i+1}: {row['Customer Name']} (${row['Amount']})" for i, row in alerts.iterrows()]
                    selected_option = st.sidebar.selectbox("Select Transaction to Analyze", options)
                    
                    # Get Data
                    selected_idx = options.index(selected_option)
                    alert_data = alerts.iloc[selected_idx].to_dict()
                    
                    # Fill missing optional fields
                    if "Date" not in alert_data: alert_data["Date"] = "N/A"
                    if "Transaction Type" not in alert_data: alert_data["Transaction Type"] = "General Transaction"
            
            except Exception as e:
                st.sidebar.error(f"Error reading CSV: {e}")
        else:
            st.info("👈 Upload a CSV file to begin.")
            # Stop execution here if no file to avoid errors in main layout
            if input_method == "Upload Transaction File":
                st.warning("Please upload a CSV file or switch to Manual Entry.")
    else:
        st.sidebar.subheader("Manual Transaction Details")
        cust_name = st.sidebar.text_input("Customer Name", "Jane Doe")
        trans_type = st.sidebar.selectbox("Transaction Type", ["Cash Deposit", "Wire Transfer", "Crypto Purchase"])
        amount = st.sidebar.number_input("Amount ($)", min_value=0.0, value=9500.0)
        date = st.sidebar.date_input("Transaction Date")
        desc = st.sidebar.text_area("Description of Activity", "Customer made multiple cash deposits just under the reporting threshold.")
        
        alert_data = {
            "Customer Name": cust_name,
            "Transaction Type": trans_type,
            "Amount": amount,
            "Date": str(date),
            "Description": desc,
            "Risk Flag": "Manual Entry"
        }

    # Main Layout
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Transaction Context")
        st.info(f"Customer: {alert_data.get('Customer Name')}")
        st.write(f"Type: {alert_data.get('Transaction Type')}")
        st.write(f"Amount: ${alert_data.get('Amount', 0):,.2f}")
        st.write(f"Date: {alert_data.get('Date')}")
        st.warning(f" Activity: {alert_data.get('Description')}")

        st.markdown("---")
        if st.button("Generate Narrative", type="primary"):
            with st.spinner("Analyzing regulations and drafting narrative..."):
                query = alert_data.get("Description")
                context = engine.retrieve_context(query)
                sar_narrative = engine.generate_sar_narrative(alert_data, context)
                st.session_state["sar"] = sar_narrative
                st.session_state["context"] = context

    with col2:
        st.subheader("Generated Output")
        
        if "sar" in st.session_state:
            tab1, tab2 = st.tabs(["Narrative Draft", "Audit Trail"])
            
            with tab1:
                st.text_area("Final SAR Narrative", st.session_state["sar"], height=350)
                
            with tab2:
                st.markdown("#### Regulatory Citations")
                audit_data = []
                for i, doc in enumerate(st.session_state["context"]):
                    source = doc.metadata.get('source', 'FCA Handbook')
                    audit_data.append({
                        "Citation ID": f"CIT-{i+1:03d}",
                        "Source": source,
                        "Excerpt": doc.page_content[:100] + "..."
                    })
                    with st.expander(f"Citation {i+1}: {source}"):
                        st.write(doc.page_content)
                
                # Export
                st.markdown("---")
                df_audit = pd.DataFrame(audit_data)
                st.download_button(
                    label="Download Audit Log (CSV)",
                    data=df_audit.to_csv(index=False),
                    file_name="audit_log.csv",
                    mime="text/csv"
                )
        else:
            st.write("Select an alert and generate the narrative to view results.")

# --- PAGE 2: RAG ARCHITECTURE ---
elif st.session_state.page == 'RAG Architecture':
    st.title("Retrieval-Augmented Generation (RAG) Architecture")
    st.markdown("### How the System Grounds AI in Law")
    st.write("Our system uses RAG to ensure that every word generated by the AI is backed by a specific regulation. This solves the 'hallucination' problem common in Large Language Models.")
    
    # Graphviz Diagram for RAG
    rag_graph = graphviz.Digraph()
    rag_graph.attr(rankdir='LR')
    
    rag_graph.node('A', 'Transaction Data')
    rag_graph.node('B', 'Query Encoder')
    rag_graph.node('C', 'Vector Database\n(Regulatory Rules)')
    rag_graph.node('D', 'Relevant Context')
    rag_graph.node('E', 'Llama 3 Model')
    rag_graph.node('F', 'Final SAR Narrative')
    
    rag_graph.edge('A', 'B')
    rag_graph.edge('B', 'C', label=' Similarity Search')
    rag_graph.edge('C', 'D', label=' Top-k Matches')
    rag_graph.edge('A', 'E')
    rag_graph.edge('D', 'E')
    rag_graph.edge('E', 'F', label=' Generation')
    
    st.graphviz_chart(rag_graph)
    
    st.markdown("#### Process Flow")
    st.markdown("""
    1. **Ingestion**: Transaction details are converted into a query vector.
    2. **Retrieval**: The system searches the Vector Database (ChromaDB/FAISS) for the most relevant regulatory guidelines.
    3. **Augmentation**: The original transaction data is combined with the retrieved regulations.
    4. **Generation**: The Augmented Prompt is sent to Llama 3, which writes the narrative using the provided laws as citations.
    """)

# --- PAGE 3: ML MODEL ARCHITECTURE ---
elif st.session_state.page == 'ML Model':
    st.title("Machine Learning Architecture")
    st.markdown("### The Dual-Engine Approach")
    st.write("We utilize a hybrid approach combining supervised learning for known patterns and unsupervised learning for anomalies.")
    
    # Graphviz Diagram for ML
    ml_graph = graphviz.Digraph()
    ml_graph.attr(rankdir='TB')
    
    with ml_graph.subgraph(name='cluster_0') as c:
        c.attr(style='filled', color='lightgrey')
        c.node_attr.update(style='filled', color='white')
        c.node('XGB', 'XGBoost\n(Supervised)')
        c.node('ISO', 'Isolation Forest\n(Anomaly)')
        c.attr(label='The Detection Core')
    
    ml_graph.node('Input', 'Raw Transaction Data')
    ml_graph.node('Feat', 'Feature Engineering')
    ml_graph.node('Ens', 'Ensemble Decision')
    ml_graph.node('Alert', 'Generate Alert')
    ml_graph.node('Active', 'Active Learning Loop')
    
    ml_graph.edge('Input', 'Feat')
    ml_graph.edge('Feat', 'XGB')
    ml_graph.edge('Feat', 'ISO')
    ml_graph.edge('XGB', 'Ens')
    ml_graph.edge('ISO', 'Ens')
    ml_graph.edge('Ens', 'Alert')
    ml_graph.edge('Alert', 'Active', label=' Human Feedback')
    ml_graph.edge('Active', 'XGB', label=' Retraining')
    
    st.graphviz_chart(ml_graph)
    
    st.markdown("#### Key Components")
    st.markdown("""
    - **XGBoost**: Detects known money laundering typologies based on historical labeled data.
    - **Isolation Forest**: Identifies statistical anomalies (outliers) that do not match normal customer behavior.
    - **Active Learning**: Feeds analyst decisions (True/False Positives) back into the model to improve accuracy over time.
    """)

# Footer
st.markdown("---")
st.caption("Barclays Financial Crime Operations | Hackathon 2026")
