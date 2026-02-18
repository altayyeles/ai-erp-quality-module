"""
Quality Prediction Dashboard Page
Streamlit page for predictive quality analysis and SPC monitoring
"""

import streamlit as st
import numpy as np
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Quality Prediction", page_icon="🔮", layout="wide")

st.title("🔮 Quality Prediction")
st.markdown("---")

# Sidebar for sensor inputs
st.sidebar.header("📊 Sensor Inputs")

with st.sidebar.form("sensor_form"):
    st.subheader("Process Parameters")
    
    air_temp = st.number_input(
        "Air Temperature (K)",
        min_value=290.0,
        max_value=310.0,
        value=298.0,
        step=0.5,
        help="Ambient air temperature"
    )
    
    process_temp = st.number_input(
        "Process Temperature (K)",
        min_value=300.0,
        max_value=320.0,
        value=308.0,
        step=0.5,
        help="Process/tool temperature"
    )
    
    rotational_speed = st.number_input(
        "Rotational Speed (rpm)",
        min_value=1000,
        max_value=2000,
        value=1500,
        step=50,
        help="Spindle speed"
    )
    
    torque = st.number_input(
        "Torque (Nm)",
        min_value=20.0,
        max_value=80.0,
        value=40.0,
        step=1.0,
        help="Tool torque"
    )
    
    tool_wear = st.number_input(
        "Tool Wear (min)",
        min_value=0.0,
        max_value=250.0,
        value=100.0,
        step=10.0,
        help="Accumulated tool wear"
    )
    
    vibration = st.number_input(
        "Vibration (mm/s)",
        min_value=0.0,
        max_value=2.0,
        value=0.5,
        step=0.1,
        help="Machine vibration level"
    )
    
    humidity = st.number_input(
        "Humidity (%)",
        min_value=30.0,
        max_value=90.0,
        value=60.0,
        step=5.0,
        help="Relative humidity"
    )
    
    pressure = st.number_input(
        "Pressure (bar)",
        min_value=0.8,
        max_value=1.2,
        value=1.0,
        step=0.05,
        help="Atmospheric pressure"
    )
    
    predict_button = st.form_submit_button("🔮 Predict Quality", use_container_width=True)

# Main content
try:
    from modules.quality.predictive_model import QualityPredictiveModel, create_demo_model
    
    if predict_button:
        with st.spinner("Running prediction..."):
            # Prepare sensor data
            sensor_data = {
                'air_temperature': air_temp,
                'process_temperature': process_temp,
                'rotational_speed': rotational_speed,
                'torque': torque,
                'tool_wear': tool_wear,
                'vibration': vibration,
                'humidity': humidity,
                'pressure': pressure
            }
            
            # Load or create model
            model_path = Path("models/quality_model.pkl")
            if model_path.exists():
                model = QualityPredictiveModel(model_path)
            else:
                st.info("📦 Model not found. Training demo model...")
                model = create_demo_model()
            
            # Make prediction
            result = model.predict_defect_probability(sensor_data)
            
            # Display results
            st.success("✅ Prediction Complete")
            
            # Metrics row
            col1, col2, col3 = st.columns(3)
            
            with col1:
                prob_pct = result.defect_probability * 100
                st.metric(
                    "Defect Probability",
                    f"{prob_pct:.1f}%",
                    delta=None
                )
            
            with col2:
                # Color-code risk level
                risk_colors = {
                    'LOW': '🟢',
                    'MEDIUM': '🟡',
                    'HIGH': '🟠',
                    'CRITICAL': '🔴'
                }
                st.metric(
                    "Risk Level",
                    f"{risk_colors.get(result.risk_level, '⚪')} {result.risk_level}",
                    delta=None
                )
            
            with col3:
                prediction = "DEFECT" if result.is_defect_predicted else "OK"
                st.metric(
                    "Prediction",
                    prediction,
                    delta=None
                )
            
            st.markdown("---")
            
            # Feature contributions
            st.subheader("📊 Feature Contributions (SHAP Values)")
            
            contributions_df = pd.DataFrame(
                list(result.feature_contributions.items()),
                columns=['Feature', 'Contribution']
            )
            contributions_df = contributions_df.sort_values('Contribution', ascending=True)
            
            # Bar chart
            st.bar_chart(contributions_df.set_index('Feature'))
            
            # Recommendations
            st.markdown("---")
            st.subheader("💡 Recommendations")
            
            for rec in result.recommendations:
                if "CRITICAL" in rec:
                    st.error(rec)
                elif "HIGH RISK" in rec or "⚠️" in rec:
                    st.warning(rec)
                else:
                    st.info(rec)
    
    else:
        # Show placeholder
        st.info("👈 Enter sensor values in the sidebar and click 'Predict Quality' to analyze.")
        
        # Show example metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Example Defect Probability", "12.5%")
        with col2:
            st.metric("Example Risk Level", "🟢 LOW")
        with col3:
            st.metric("Example Prediction", "OK")

except Exception as e:
    st.error(f"❌ Error loading quality prediction model: {str(e)}")
    st.info("💡 The model may not be installed or trained yet. Using demo mode.")

# SPC Analysis Section
st.markdown("---")
st.subheader("📈 Statistical Process Control (SPC)")

try:
    from modules.quality.spc_analysis import SPCAnalyzer
    
    # Generate demo data
    np.random.seed(42)
    demo_data = np.random.normal(100, 5, 30).tolist()
    
    analyzer = SPCAnalyzer()
    spc_result = analyzer.analyze(demo_data)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create control chart
        df = pd.DataFrame({
            'Sample': range(1, len(demo_data) + 1),
            'Value': demo_data
        })
        
        st.line_chart(df.set_index('Sample'))
        
        # Add control limits info
        st.caption(f"UCL: {spc_result.ucl:.2f} | Center: {spc_result.center_line:.2f} | LCL: {spc_result.lcl:.2f}")
    
    with col2:
        st.metric("Process Status", "✅ IN CONTROL" if spc_result.in_control else "⚠️ OUT OF CONTROL")
        st.metric("Violations", len(spc_result.violations))
        
        if spc_result.violations:
            st.warning("⚠️ Control violations detected")
            for v in spc_result.violations[:3]:
                st.caption(f"• {v}")

except Exception as e:
    st.warning(f"SPC analysis unavailable: {str(e)}")
    st.info("Install required dependencies to enable SPC monitoring.")

st.markdown("---")
st.caption("Quality Prediction Module | AI-ERP Quality System")
