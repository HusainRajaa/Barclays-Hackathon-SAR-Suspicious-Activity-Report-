import streamlit as st
import pandas as pd
import graphviz
from fpdf import FPDF
from rag_engine import RAGEngine
from mock_data_loader import generate_regulatory_docs, generate_mock_alerts

# --- CONFIGURATION & STYLES ---
st.set_page_config(
    page_title="Barclays SAR Generator",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Barclays" Aesthetic
st.markdown("""
    <style>
    /* Global Font & Background */
    body {
        font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
        background-color: #f4f5f7;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #00395D; /* Dark Blue */
        font-weight: 600;
    }
    
    /* Barclays Blue Accents */
    .stButton>button {
        background-color: #00AEEF; /* Barclays Cyan/Blue */
        color: white;
        border: none;
        border-radius: 4px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #008AC5;
        color: white;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #00395D; /* Dark Corporate Blue */
        color: white;
    }
    section[data-testid="stSidebar"] .css-17lntkn {
        color: white;
    }
    
    /* Alerts/Dataframes */
    .stDataFrame {
        border: 1px solid #e0e0e0;
        border-radius: 5px;
    }
    
    /* Cards (Expander/Metric) */
    div[data-testid="stMetricValue"] {
        color: #00AEEF;
    }
    
    /* Custom Card Class */
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- UTILS: PDF GENERATOR ---
def create_pdf(sar_text, audit_data, alert_data):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Suspicious Activity Report (SAR)", ln=True, align='C')
    pdf.ln(10)
    
    # Metadata
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f"Customer Name: {alert_data.get('Customer Name')}", ln=True)
    pdf.cell(0, 8, f"Transaction Date: {alert_data.get('Date')}", ln=True)
    pdf.cell(0, 8, f"Amount: ${alert_data.get('Amount', 0):,.2f}", ln=True)
    pdf.cell(0, 8, f"Alert ID: {alert_data.get('AlertID', 'N/A')}", ln=True)
    pdf.ln(10)
    
    # Narrative Body
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Narrative", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 6, sar_text)
    pdf.ln(10)
    
    # Audit Trail
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Audit Trail / Regulatory Citations", ln=True)
    
    pdf.set_font("Arial", '', 9)
    for item in audit_data:
        pdf.set_text_color(100, 100, 100)
        source = item.get("Source", "Unknown")
        excerpt = item.get("Excerpt", "").replace("\n", " ")
        pdf.multi_cell(0, 5, f"[{source}] {excerpt}")
        pdf.ln(2)
        
    return pdf.output(dest='S').encode('latin-1')

# --- INITIALIZATION ---
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

if 'page' not in st.session_state:
    st.session_state.page = 'Dashboard'

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Barclays_Logo.svg/1200px-Barclays_Logo.svg.png", width=150)
    st.markdown("### Financial Crime Operations")
    st.markdown("---")
    
    if st.button("📊 Dashboard", use_container_width=True):
        st.session_state.page = 'Dashboard'
    if st.button("📝 SAR Generator", use_container_width=True):
        st.session_state.page = 'Generator'
    if st.button("⚙️ System Architecture", use_container_width=True):
        st.session_state.page = 'Architecture'
        
    st.markdown("---")
    st.caption("v2.0.0 | Connected to RAG Engine")

# --- PAGE: DASHBOARD ---
if st.session_state.page == 'Dashboard':
    st.title("Operations Dashboard")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Pending Alerts", "12", "+2")
    col2.metric("SARs Drafted", "45", "+5")
    col3.metric("Regulatory Updates", "2", "New FCA Rules")
    col4.metric("Avg. Processing Time", "1.2h", "-15%")
    
    st.markdown("### Recent Alerts")
    mock_alerts = generate_mock_alerts()
    st.dataframe(mock_alerts, use_container_width=True)

# --- PAGE: SAR GENERATOR ---
elif st.session_state.page == 'Generator':
    st.title("SAR Narrative Generator")
    
    # Workflow Steps
    step = st.selectbox("Current Step", ["1. Select Alert", "2. Review Context", "3. Generate & Export"])
    
    # Load Alerts
    alerts = generate_mock_alerts()
    
    if step == "1. Select Alert":
        st.subheader("Select a Transaction to Investigate")
        
        # Bug Fix: Use index to allow duplicate selection
        selected_index = st.selectbox(
            "Choose Alert",
            range(len(alerts)),
            format_func=lambda x: f"{alerts.iloc[x]['AlertID']} | {alerts.iloc[x]['Customer Name']} | ${alerts.iloc[x]['Amount']:,.2f}"
        )
        
        selected_alert = alerts.iloc[selected_index].to_dict()
        st.session_state['selected_alert'] = selected_alert
        
        st.info("Alert Select. Proceed to Step 2.")
        
        # Preview
        st.json(selected_alert)

    elif step == "2. Review Context":
        if 'selected_alert' not in st.session_state:
            st.warning("Please select an alert first.")
        else:
            alert = st.session_state['selected_alert']
            st.subheader(f"Analyzing Alert: {alert.get('AlertID')}")
            
            with st.spinner("Retrieving Regulatory Context..."):
                query = alert.get("Description")
                context = engine.retrieve_context(query)
                st.session_state['context'] = context
                
            st.success("✅ Relevant Regulations Found")
            
            for doc in context:
                with st.expander(f"📖 {doc.metadata.get('source', 'Regulation')}"):
                    st.write(doc.page_content)
                    
            st.info("Review complete. Proceed to Step 3 to generate the narrative.")

    elif step == "3. Generate & Export":
        if 'selected_alert' not in st.session_state or 'context' not in st.session_state:
            st.warning("Please complete previous steps.")
        else:
            st.subheader("Drafting Narrative")
            
            if st.button("✨ Draft SAR Narrative"):
                with st.spinner("Drafting with AI..."):
                    sar = engine.generate_sar_narrative(
                        st.session_state['selected_alert'],
                        st.session_state['context']
                    )
                    st.session_state['sar_draft'] = sar
            
            if 'sar_draft' in st.session_state:
                st.text_area("Final Narrative", st.session_state['sar_draft'], height=300)
                
                # Prepare Audit Data for PDF
                audit_list = []
                for doc in st.session_state['context']:
                    audit_list.append({
                        "Source": doc.metadata.get('source', 'FCA'),
                        "Excerpt": doc.page_content
                    })
                
                # Generate PDF
                pdf_bytes = create_pdf(
                    st.session_state['sar_draft'],
                    audit_list,
                    st.session_state['selected_alert']
                )
                
                st.download_button(
                    label="📥 Download Official SAR (PDF)",
                    data=pdf_bytes,
                    file_name=f"SAR_{st.session_state['selected_alert'].get('AlertID')}.pdf",
                    mime="application/pdf"
                )

# --- PAGE: ARCHITECTURE ---
elif st.session_state.page == 'Architecture':
    st.title("System Architecture")
    
    st.markdown("### RAG Pipeline Visualization")
    try:
        rag_graph = graphviz.Digraph()
        rag_graph.attr(rankdir='LR')
        rag_graph.node('A', 'Transaction Data')
        rag_graph.node('B', 'Query Encoder')
        rag_graph.node('C', 'Vector DB\n(FCA Rules)')
        rag_graph.node('D', 'Context')
        rag_graph.node('E', 'Llama 3')
        rag_graph.node('F', 'SAR Report')
        
        rag_graph.edge('A', 'B')
        rag_graph.edge('B', 'C')
        rag_graph.edge('C', 'D')
        rag_graph.edge('A', 'E')
        rag_graph.edge('D', 'E')
        rag_graph.edge('E', 'F')
        
        st.graphviz_chart(rag_graph)
    except Exception as e:
        st.error("Graphviz visualization not available (tool missing). Displaying text flow instead.")
        st.code("""
        [Transaction Data] -> [Query Encoder] -> [Vector DB]
                                      |
                                      v
        [Llama 3] <---------------- [Context]
           |
           v
        [SAR Report]
        """)

# --- FOOTER ---
st.markdown("---")
st.caption("© 2026 Barclays PLC | Financial Crime Global Operations | Confidential")
