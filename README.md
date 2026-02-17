# 🦅 Suspicious Activity Report Generator

**AI-Powered Financial Crime Compliance | Hackathon 2026**

![Status](https://img.shields.io/badge/Status-Prototype-Success) ![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red) ![Llama](https://img.shields.io/badge/AI-Llama%203-purple)

## 📖 Project Overview
Financial institutions face a massive backlog of **Suspicious Activity Reports (SARs)**. Current processes are manual, slow (4-6 hours per report), and prone to inconsistency.

This solution is a **Generative AI-powered Dashboard** that automates the drafting of regulator-ready SAR narratives.

### 🚀 Key Features
- **Dual-Engine Architecture**: Combines **XGBoost** (for detection) with **Llama 3** (for explanation).
- **RAG Pipeline**: Retrieves real-time regulatory guidelines (FCA/FinCEN) from a Vector Database (Chroma/FAISS) to ground every narrative in law.
- **Active Learning**: Analyst feedback loops back to retrain the risk models.
- **Audit Trail**: Every generated claim is cited with a source document for full defensibility.

## 🛠️ Tech Stack
- **Frontend**: Streamlit (Python)
- **AI Core**: LangChain, Llama 3 (via Ollama/HuggingFace)
- **Vector DB**: FAISS (Local) / ChromaDB
- **Data Processing**: Pandas, NumPy

## 🏃‍♂️ How to Run Locally

1. **Clone the Repo**
   ```bash
   git clone https://github.com/HusainRajaa/Barclays-Hackathon-SAR-Suspicious-Activity-Report-.git
   cd Barclays-Hackathon-SAR-Suspicious-Activity-Report-
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the App**
   ```bash
   streamlit run app.py
   ```

## ☁️ Deployment
This app is designed to be hosted on **Streamlit Cloud**.
1. Fork/Clone this repo.
2. Make the repo **Public**.
3. Connect to [share.streamlit.io](https://share.streamlit.io).
4. Deploy `app.py`.

---
*Developed for the Barclays Global Hackathon 2026.*
