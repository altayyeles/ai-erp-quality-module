"""
Quality Prediction Dashboard Page

Streamlit page for predictive quality analysis with sensor input,
defect probability prediction, SHAP feature analysis, and SPC charts.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from modules.quality.predictive_model import QualityPredictiveModel, create_demo_model

st.set_page_config(page_title="Quality Prediction", page_icon="🔮", layout="wide")

st.title("🔮 Quality Prediction")
st.markdown("### Predictive Quality Analysis with XGBoost + SHAP")
st.markdown("---")

# Initialize model
@st.cache_resource
def get_model():
    return create_demo_model()

model = get_model()

# Sensor input form
st.sidebar.header("⚙️ Sensor Readings")
st.sidebar.markdown("Adjust sensor values to predict quality:")

sensor_readings = {
    'air_temperature': st.sidebar.slider(
        "Air Temperature (K)",
        min_value=290.0, max_value=310.0, value=298.0, step=0.5
    ),
    'process_temperature': st.sidebar.slider(
        "Process Temperature (K)",
        min_value=300.0, max_value=320.0, value=308.0, step=0.5
    ),
    'rotational_speed': st.sidebar.slider(
        "Rotational Speed (rpm)",
        min_value=1000, max_value=2000, value=1500, step=50
    ),
    'torque': st.sidebar.slider(
        "Torque (Nm)",
        min_value=20.0, max_value=80.0, value=40.0, step=1.0
    ),
    'tool_wear': st.sidebar.slider(
        "Tool Wear (min)",
        min_value=0, max_value=250, value=100, step=10
    ),
    'vibration': st.sidebar.slider(
        "Vibration (mm/s)",
        min_value=0.0, max_value=1.5, value=0.5, step=0.05
    ),
    'humidity': st.sidebar.slider(
        "Humidity (%)",
        min_value=30.0, max_value=90.0, value=60.0, step=1.0
    ),
    'pressure': st.sidebar.slider(
        "Pressure (bar)",
        min_value=0.8, max_value=1.2, value=1.0, step=0.01
    )
}

if st.sidebar.button("🔍 Run Prediction", type="primary"):
    with st.spinner("Running prediction..."):
        result = model.predict_defect_probability(sensor_readings)
        
        # Display results
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Defect Probability",
                f"{result.defect_probability*100:.1f}%"
            )
        
        with col2:
            risk_color = {
                "LOW": "🟢",
                "MEDIUM": "🟡",
                "HIGH": "🟠",
                "CRITICAL": "🔴"
            }
            st.metric(
                "Risk Level",
                f"{risk_color.get(result.risk_level, '⚪')} {result.risk_level}"
            )
        
        with col3:
            prediction = "DEFECT" if result.is_defect_predicted else "OK"
            st.metric(
                "Prediction",
                prediction
            )
        
        st.markdown("---")
        
        # Feature contributions (SHAP values)
        st.subheader("📊 Feature Contributions (SHAP)")
        
        contributions_df = pd.DataFrame([
            {"Feature": k, "Contribution": v}
            for k, v in result.feature_contributions.items()
        ]).sort_values("Contribution", ascending=True)
        
        fig = px.bar(
            contributions_df,
            x="Contribution",
            y="Feature",
            orientation='h',
            title="SHAP Feature Importance",
            color="Contribution",
            color_continuous_scale="RdYlGn_r"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Recommendations
        st.subheader("💡 Recommendations")
        for rec in result.recommendations:
            if "🚨" in rec or "CRITICAL" in rec:
                st.error(rec)
            elif "⚠️" in rec:
                st.warning(rec)
            else:
                st.info(rec)
        
        # Sensor readings table
        st.subheader("📋 Input Sensor Readings")
        readings_df = pd.DataFrame([sensor_readings]).T
        readings_df.columns = ["Value"]
        st.dataframe(readings_df, use_container_width=True)

else:
    st.info("👈 Adjust sensor readings in the sidebar and click 'Run Prediction'")
    
    # Show feature importance from model
    st.subheader("📊 Model Feature Importance")
    importance = model.get_feature_importance()
    importance_df = pd.DataFrame([
        {"Feature": k, "Importance": v}
        for k, v in importance.items()
    ]).sort_values("Importance", ascending=False)
    
    fig = px.bar(
        importance_df,
        x="Importance",
        y="Feature",
        orientation='h',
        title="XGBoost Feature Importance",
        color="Importance",
        color_continuous_scale="Blues"
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("Quality Prediction Module | Powered by XGBoost + SHAP")
