"""
AI-Powered ERP Quality Module - Streamlit Dashboard
Main application entry point
"""

import streamlit as st

st.set_page_config(
    page_title="AI-ERP Quality Module",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar navigation
st.sidebar.title("🏭 AI-ERP Quality Module")
st.sidebar.markdown("---")
st.sidebar.markdown("### Navigation")
st.sidebar.markdown("""
- 🏠 **Home** — Overview & KPIs
- 🔮 **Quality Prediction** — Predictive Analytics
- 🔧 **Maintenance** — Predictive Maintenance
- 🚚 **Supplier** — Supplier Risk Scoring
- 👁️ **Vision** — Visual Inspection
- 📊 **Reports** — KPI Reports & Alerts
"""
)

st.title("🏭 AI-Powered ERP Quality Module")
st.markdown("### Real-Time Manufacturing Intelligence Dashboard")
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="🟢 OEE", value="87.3%", delta="+2.1%")

with col2:
    st.metric(label="✅ First Pass Yield", value="96.8%", delta="+0.5%")

with col3:
    st.metric(label="🔴 DPMO", value="32,000", delta="-1,200")

with col4:
    st.metric(label="📐 Cpk", value="1.45", delta="+0.03")

st.markdown("---")
st.info("👈 Use the sidebar to navigate to specific modules. Each module provides real-time AI-powered insights.")

st.markdown("### 📦 Available Modules")

m1, m2, m3 = st.columns(3)
with m1:
    st.markdown("#### 🔮 Quality Prediction")
    st.markdown("XGBoost-based failure prediction with SHAP explainability and SPC control charts.")

with m2:
    st.markdown("#### 🔧 Predictive Maintenance")
    st.markdown("Random Forest RUL estimation with 8-machine real-time sensor monitoring.")

with m3:
    st.markdown("#### 🚚 Supplier Scoring")
    st.markdown("K-Means clustering + IsolationForest anomaly detection for supplier risk.")

m4, m5, m6 = st.columns(3)
with m4:
    st.markdown("#### 👁️ Visual Inspection")
    st.markdown("YOLOv8 defect detection with OpenCV fallback and anomaly autoencoder.")

with m5:
    st.markdown("#### 📊 KPI Reporting")
    st.markdown("Real-time OEE, FPY, DPMO, Cpk dashboards with alert management.")

with m6:
    st.markdown("#### 🔔 Alert System")
    st.markdown("SQLite-backed alert queue with threshold-based callback notifications.")

st.markdown("---")
st.caption("AI-ERP Quality Module v1.0.0 | LED Yazılım Staj Projesi | 2025")