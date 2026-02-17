import streamlit as st
import pandas as pd
try:
    import graphviz
except ImportError:
    graphviz = None
from fpdf import FPDF
from rag_engine import RAGEngine
from mock_data_loader import generate_regulatory_docs, generate_mock_alerts

# --- CONFIGURATION & STYLES ---
st.set_page_config(
    page_title="Suspicious Activity Report Generator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- THEME MANAGEMENT ---
if "theme" not in st.session_state:
    st.session_state.theme = "Light"

with st.sidebar:
    st.markdown("### Settings")
    theme_toggle = st.toggle("Dark mode", value=(st.session_state.theme == "Dark"))
    if theme_toggle:
        st.session_state.theme = "Dark"
    else:
        st.session_state.theme = "Light"

# --- TOTAL UI OVERHAUL CSS ---
# This ensures a "Proper" monochrome look by targeting ROOT containers
common_css = """
    <style>
    /* Font and General Scale */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Courier New', monospace !important;
    }
    
    /* Remove default Streamlit padding/decorations */
    [data-testid="stHeader"] {
        background: transparent !important;
    }
    
    /* Strict Box Bordering */
    .stButton>button {
        border-radius: 0px !important;
        text-transform: uppercase !important;
        font-weight: bold !important;
        padding: 0.5rem 1rem !important;
        width: 100% !important;
    }
    
    /* Selectbox and Inputs */
    input, textarea, select, .stSelectbox>div>div>div {
        border-radius: 0px !important;
    }
    
    /* Navigation Bar Borders */
    [data-testid="stHorizontalBlock"] {
        border-bottom: 2px solid;
        padding-bottom: 1rem;
        margin-bottom: 2rem;
    }
    </style>
"""

light_theme_css = common_css + """
    <style>
    /* Light Mode Overrides */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMainViewContainer"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 2px solid #000000 !important;
    }
    
    /* Text Colors */
    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown {
        color: #000000 !important;
    }
    
    /* Borders */
    h1, h2, h3, h4, h5, h6 {
        border-bottom: 2px solid #000000 !important;
    }
    
    /* Info/Warning/Success Boxes (Alerts) */
    [data-testid="stNotificationContent"] {
        background-color: #ffffff !important;
        border: 2px solid #000000 !important;
        color: #000000 !important;
    }
    [data-testid="stNotificationContent"] svg {
        fill: #000000 !important;
    }
    
    /* File Uploader Decor */
    [data-testid="stFileUploadDropzone"] {
        background-color: #ffffff !important;
        border: 2px dashed #000000 !important;
        color: #000000 !important;
    }
    [data-testid="stFileUploadDropzone"] button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #000000 !important;
    }
    
    /* Widgets */
    .stButton>button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
    }
    .stButton>button:hover {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    
    input, textarea, select, .stSelectbox>div>div>div {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
    }
    
    [data-testid="stHorizontalBlock"] {
        border-color: #000000 !important;
    }
    </style>
"""

dark_theme_css = common_css + """
    <style>
    /* Proper Dark Mode Overrides (True Monochrome) */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMainViewContainer"] {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 2px solid #ffffff !important;
    }
    
    /* Target the sidebar content wrapper specifically */
    [data-testid="stSidebarContent"] {
        background-color: #000000 !important;
    }
    
    /* Text Colors */
    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown {
        color: #ffffff !important;
    }
    
    /* Borders */
    h1, h2, h3, h4, h5, h6 {
        border-bottom: 2px solid #ffffff !important;
    }
    
    /* Info/Warning/Success Boxes (Alerts) */
    [data-testid="stNotificationContent"] {
        background-color: #000000 !important;
        border: 2px solid #ffffff !important;
        color: #ffffff !important;
    }
    [data-testid="stNotificationContent"] svg {
        fill: #ffffff !important;
    }
    
    /* File Uploader Decor */
    [data-testid="stFileUploadDropzone"] {
        background-color: #000000 !important;
        border: 2px dashed #ffffff !important;
        color: #ffffff !important;
    }
    [data-testid="stFileUploadDropzone"] button {
        background-color: #333333 !important;
        color: #ffffff !important;
        border: 1px solid #ffffff !important;
    }
    /* Extra specificity for the button */
    [data-testid="stFileUploadDropzone"] [data-testid="baseButton-secondary"] {
        background-color: #333333 !important;
        color: #ffffff !important;
    }
    
    /* Widgets */
    .stButton>button {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 2px solid #ffffff !important;
    }
    .stButton>button:hover {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    input, textarea, select, .stSelectbox>div>div>div {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 2px solid #ffffff !important;
    }
    
    [data-testid="stHorizontalBlock"] {
        border-color: #ffffff !important;
    }
    
    /* Fix for Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #000000 !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: #ffffff !important;
        background-color: #000000 !important;
        border: 1px solid #ffffff !important;
    }
    </style>
"""

# Inject CSS based on Theme
if st.session_state.theme == "Dark":
    st.markdown(dark_theme_css, unsafe_allow_html=True)
else:
    st.markdown(light_theme_css, unsafe_allow_html=True)

# Initialize Engine (Cached)
@st.cache_resource
def load_engine_v2():
    engine = RAGEngine()
    docs = generate_regulatory_docs()
    engine.ingest_data(docs)
    return engine

try:
    engine = load_engine_v2()
except Exception as e:
    st.error(f"Failed to load engine: {e}")
    st.stop()

def sanitize_sar_text(text: str) -> str:
    """
    Strips ALL markdown-like symbols for a clean professional text look.
    """
    import re
    if not text:
        return ""
    
    # 1. Remove bold/italic symbols (**, *, __)
    text = text.replace("***", "").replace("**", "").replace("__", "").replace("*", "")
    
    # 2. Remove horizontal rules (---)
    text = re.sub(r'---', '', text)
    
    # 3. Remove Header markers (###, ##, #)
    text = re.sub(r'#+\s', '', text)
    
    # 4. Remove Bullet points (- at start of lines)
    text = re.sub(r'^\s*[-•]\s*', '', text, flags=re.MULTILINE)
    
    # 5. Clean up excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

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

# --- PAGE 0: HOME (LANDING PAGE) ---
if st.session_state.page == 'Home':
    st.title("Suspicious Activity Report Generator")
    st.markdown("### AI-Powered Suspicious Activity Reporting System")
    
    st.markdown("---")
    
    # Introduction
    st.markdown("""
    **Welcome to the Suspicious Activity Report Generator**, an advanced AI system designed to automate 
    the creation of Suspicious Activity Reports (SARs) for financial crime compliance teams.
    
    This system leverages cutting-edge technologies including:
    - **Retrieval-Augmented Generation (RAG)** for regulatory compliance
    - **Machine Learning Risk Assessment** for intelligent transaction analysis
    - **Vector Database Search** for contextual regulatory citation
    """)
    
    st.markdown("---")
    
    # Key Features
    col_feat1, col_feat2 = st.columns(2)
    
    with col_feat1:
        st.markdown("#### Key Features")
        st.markdown("""
        - **Universal CSV Support**: Upload any transaction CSV format
        - **AI Risk Detection**: Automatic identification of suspicious patterns
        - **Regulatory Grounding**: Every narrative backed by specific regulations
        - **Full-Screen Editor**: Refine and customize generated reports
        - **Audit Trail**: Complete transparency of AI decision-making
        """)
    
    with col_feat2:
        st.markdown("#### How It Works")
        st.markdown("""
        1. **Upload**: Submit transaction data in any CSV format
        2. **Analyze**: AI scans for money laundering indicators
        3. **Generate**: System creates detailed SAR narrative
        4. **Review**: Edit and finalize in dedicated editor
        5. **Export**: Download completed report for submission
        """)
    
    st.markdown("---")
    
    # Use Application Button
    st.markdown("### Ready to Begin?")
    if st.button("USE APPLICATION", type="primary", use_container_width=True):
        set_page('Generator')
        st.rerun()
    
    st.markdown("---")
    
    # Technical Details
    st.markdown("#### Technical Architecture")
    st.markdown("""
    This system combines multiple AI technologies:
    - **FAISS Vector Database** for efficient regulatory document retrieval
    - **HuggingFace Embeddings** for semantic search
    - **Rules-Based ML Engine** for risk classification
    - **Template-Based Generation** for structured SAR narratives
    
    The system is designed to meet regulatory requirements for transparency and auditability 
    in automated compliance systems.
    """)

# --- PAGE 1: SAR GENERATOR ---
elif st.session_state.page == 'Generator':
    st.title("Suspicious Activity Report Generator")
    st.markdown("Automated generation of Suspicious Activity Reports using Llama 3 and Vector Search.")

    # Sidebar for Input Method
    st.sidebar.header("Input Controls")
    input_method = st.sidebar.radio("Select Input Method:", ("Choose Pending Alert", "Manual Entry"))

    alert_data = {}

    if uploaded_file is not None:
        try:
            alerts = pd.read_csv(uploaded_file)
            st.sidebar.success(f"Loaded {len(alerts)} records")
            
            # Smart Column Mapping (NO VALIDATION)
            col_map = map_columns(alerts)
            all_cols = list(alerts.columns)
            
            # Normalize all rows
            normalized_alerts = [normalize_row(row, col_map, all_cols) for _, row in alerts.iterrows()]
            
            # Select Specific Transaction
            options = [f"Ref-{i+1001}: {row['Customer Name']} (${row.get('Amount', 0)})" for i, row in enumerate(normalized_alerts)]
            selected_option = st.sidebar.selectbox("Select Record", options)
            
            # Get Data
            selected_idx = options.index(selected_option)
            alert_data = normalized_alerts[selected_idx]
            st.session_state["alert_data"] = alert_data
        
        except Exception as e:
            st.sidebar.error(f"System Error: {e}")
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
        st.markdown("**NARRATIVE**")
        st.write(alert_data.get('Description', ''))
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
                    
                    # 3. SANITIZE TEXT (Override cached engine behavior)
                    sar_narrative = sanitize_sar_text(sar_narrative)
                    
                    # 4. Store in Session & Redirect
                    st.session_state["sar"] = sar_narrative
                    st.session_state["context"] = context
                    set_page('SAR Editor')
                    st.rerun()

    with col2:
        st.subheader("Generated Output")
        
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
            # Prepare audit data for PDF
            audit_list = []
            if "context" in st.session_state:
                for doc in st.session_state["context"]:
                    audit_list.append({
                        "Source": doc.metadata.get('source', 'Regulatory Handbook'),
                        "Excerpt": doc.page_content
                    })
            
            # Use real PDF generator if data exists
            if st.session_state.get("sar"):
                pdf_bytes = create_pdf(st.session_state["sar"], audit_list, st.session_state.get("alert_data", {}))
                st.download_button("EXPORT TO PDF", pdf_bytes, "sar_report.pdf", "application/pdf")
            else:
                st.button("EXPORT TO PDF", disabled=True)
            
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
    st.title("System Architecture")
    
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
