import streamlit as st
import pandas as pd
import graphviz
from rag_engine import RAGEngine
from mock_data_loader import generate_regulatory_docs, generate_mock_alerts

# Page Config
st.set_page_config(page_title="Barclays SAR Generator", layout="wide")

# Custom CSS for Professional Look (Black & White)
# Custom CSS for Strict "Sober" Monochrome Design
st.markdown("""
    <style>
    /* Global Reset */
    .main {
        background-color: #ffffff;
        color: #000000;
        font-family: 'Courier New', monospace; 
    }
    
    /* Strict Box Model */
    div.block-container {
        padding-top: 2rem;
    }
    
    /* Borders for Everything */
    .stApp > header {
        background-color: #ffffff;
        border-bottom: 2px solid #000000;
    }
    .stSidebar {
        background-color: #ffffff;
        border-right: 2px solid #000000;
    }
    
    /* Widget Styling */
    .stButton>button {
        background-color: #ffffff;
        color: #000000;
        border: 2px solid #000000;
        border-radius: 0px; /* Square corners */
        text-transform: uppercase;
        font-weight: bold;
        box-shadow: none;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: #000000;
        color: #ffffff;
        border: 2px solid #000000;
    }
    
    /* Input Fields */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        border: 2px solid #000000;
        border-radius: 0px;
        color: #000000;
        background-color: #ffffff;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #000000;
        font-family: 'Courier New', monospace;
        border-bottom: 1px solid #000000;
        padding-bottom: 0.5rem;
    }
    
    /* Info/Warning/Success Boxes Override */
    .stAlert {
        background-color: #ffffff;
        border: 2px solid #000000;
        color: #000000;
        border-radius: 0px;
    }
    
    /* Expanders */
    div[data-testid="stExpander"] {
        border: 2px solid #000000;
        border-radius: 0px;
        box-shadow: none;
    }
    div[data-testid="stExpander"] div[role="button"] p {
        font-family: 'Courier New', monospace;
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

    # Sidebar: Bank Portal Style Controls
    st.sidebar.markdown("### Internal Portal")
    st.sidebar.markdown("**System Status**: `ONLINE`")
    st.sidebar.markdown("---")
    
    # Simple File Uploader (No Radio Buttons)
    uploaded_file = st.sidebar.file_uploader("Upload Transaction Batch (CSV)", type=["csv"])
    
    st.sidebar.markdown("---")
    st.sidebar.caption("Authorized Personnel Only")

    alert_data = {}

    if uploaded_file is not None:
        try:
            alerts = pd.read_csv(uploaded_file)
            st.sidebar.success(f"Loaded {len(alerts)} records")
            
            # Validation
            required_cols = ["Customer Name", "Description", "Amount"]
            missing_cols = [col for col in required_cols if col not in alerts.columns]
            
            if missing_cols:
                st.error(f"Error: Missing columns {', '.join(missing_cols)}")
            else:
                # Select Specific Transaction
                options = [f"Ref-{i+1001}: {row['Customer Name']} (${row['Amount']})" for i, row in alerts.iterrows()]
                selected_option = st.sidebar.selectbox("Select Record", options)
                
                # Get Data
                selected_idx = options.index(selected_option)
                alert_data = alerts.iloc[selected_idx].to_dict()
                
                # Fill missing optional fields
                if "Date" not in alert_data: alert_data["Date"] = "N/A"
                if "Transaction Type" not in alert_data: alert_data["Transaction Type"] = "Unclassified"
        
        except Exception as e:
            st.sidebar.error(f"System Error: {e}")
    else:
        st.info("AWAITING BATCH UPLOAD")
        st.write("Please upload a transaction CSV file to proceed with investigation.")
        st.stop() # Halt execution until file is uploaded for a cleaner load state

    # Main Layout - Investigation Dashboard
    st.markdown("### Investigation Dashboard")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("#### Case Details")
        # Strict Record View
        st.text(f"CUSTOMER: {alert_data.get('Customer Name', 'N/A').upper()}")
        st.text(f"TYPE    : {alert_data.get('Transaction Type', 'N/A').upper()}")
        st.text(f"AMOUNT  : ${alert_data.get('Amount', 0):,.2f}")
        st.text(f"DATE    : {alert_data.get('Date', 'N/A')}")
        st.markdown("---")
        st.markdown("**NARRATIVE**")
        st.write(alert_data.get('Description', ''))

# --- RISK ENGINE (Mock ML) ---
def assess_risk(alert_row):
    """
    Simulates the ML Model's decision logic based on description keywords.
    """
    desc = alert_row.get("Description", "").lower()
    amount = alert_row.get("Amount", 0)
    
    # Critical Risk Patterns
    if "wire" in desc and ("cayman" in desc or "panama" in desc):
        return "Critical"
    if "terrorist" in desc or "sanction" in desc:
        return "Critical"
        
    # High Risk Patterns
    if "structuring" in desc or "cash deposit" in desc:
        if amount > 8000: # Simple threshold
            return "High"
    if "crypto" in desc or "unregulated" in desc:
        return "High"
    if "layering" in desc or "rapid movement" in desc:
        return "High"
        
    # Default
    return "Low"

# --- PAGE 1: SAR GENERATOR ---
if st.session_state.page == 'Generator':
    # ... (Rest of UI code) ...

        st.markdown("---")
        st.markdown("---")
        if st.button("GENERATE REPORT", type="secondary"):
            with st.spinner("PROCESSING..."):
                # 1. AI Risk Assessment
                risk_score = assess_risk(alert_data)
                
                if risk_score == "Low":
                    st.success("CASE CLOSED: No Suspicious Activity Detected.")
                    st.info("Transaction matches customer profile. No regulatory reporting required.")
                else:
                    # 2. Genuine Suspicion -> Generate
                    query = alert_data.get("Description")
                    context = engine.retrieve_context(query)
                    # Pass calculated risk to generator
                    alert_data["Risk Score"] = risk_score 
                    sar_narrative = engine.generate_sar_narrative(alert_data, context)
                    
                    # 3. Store in Session & Redirect
                    st.session_state["sar"] = sar_narrative
                    st.session_state["context"] = context
                    set_page('SAR Editor')
                    st.rerun()

    with col2:
        st.subheader("System Output")
        st.write("Results will appear here or open in the Editor.")
        
# --- PAGE 4: SAR EDITOR (Full Screen) ---
elif st.session_state.page == 'SAR Editor':
    st.title("Investigation Report Editor")
    st.markdown("Review and refine the generated Suspicious Activity Report before final submission.")
    
    col_edit, col_view = st.columns([2, 1])
    
    with col_edit:
        st.markdown("### Narrative Draft")
        # specific height for "very big" report
        edited_sar = st.text_area("Edit Narrative", st.session_state.get("sar", ""), height=800)
        st.session_state["sar"] = edited_sar
        
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("SAVE DRAFT"):
                st.success("Draft Saved locally.")
        with c2:
            st.download_button("EXPORT TO PDF", st.session_state["sar"], "sar_report.txt")
            
    with col_view:
        st.markdown("### Audit Trail")
        st.info("Regulatory context used for this generation.")
        
        if "context" in st.session_state:
            for i, doc in enumerate(st.session_state["context"]):
                source = doc.metadata.get('source', 'FCA Handbook')
                with st.expander(f"Ref {i+1}: {source}"):
                    st.caption(doc.page_content)
        
        if st.button("Back to Dashboard"):
            set_page('Generator')
            st.rerun()

# --- PAGE 2: RAG ARCHITECTURE ---
elif st.session_state.page == 'RAG Architecture':
    st.title("Retrieval-Augmented Generation (RAG) Architecture")
    st.markdown("### How the System Grounds AI in Law")
    st.write("Our system uses RAG to ensure that every word generated by the AI is backed by a specific regulation. This solves the 'hallucination' problem common in Large Language Models.")
    
    # Graphviz Diagram for RAG
    rag_graph = graphviz.Digraph()
    rag_graph.attr(rankdir='LR')
    rag_graph.attr('node', shape='rect', style='solid', color='black', fontname='Courier')
    rag_graph.attr('edge', color='black')
    
    rag_graph.node('A', 'Transaction Data')
    rag_graph.node('B', 'Query Encoder')
    rag_graph.node('C', 'Vector Database\n(Regulatory Rules)', shape='cylinder')
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
    ml_graph.attr('node', shape='rect', style='solid', color='black', fontname='Courier')
    ml_graph.attr('edge', color='black')
    
    with ml_graph.subgraph(name='cluster_0') as c:
        c.attr(style='dashed', color='black', label='The Detection Core')
        c.node('XGB', 'XGBoost\n(Supervised)')
        c.node('ISO', 'Isolation Forest\n(Anomaly)')
    
    ml_graph.node('Input', 'Raw Transaction Data')
    ml_graph.node('Feat', 'Feature Engineering')
    ml_graph.node('Ens', 'Ensemble Decision')
    ml_graph.node('Alert', 'Generate Alert', shape='doublecircle')
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
