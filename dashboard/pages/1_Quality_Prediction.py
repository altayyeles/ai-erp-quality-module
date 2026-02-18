"""
Quality Prediction Dashboard Page
XGBoost-based defect prediction with SHAP explainability and SPC charts
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Quality Prediction", page_icon="🔮", layout="wide")

st.title("🔮 Quality Prediction")
st.markdown("### Predictive Quality Analytics with SHAP Explainability")
st.markdown("---")

# Sidebar input form
st.sidebar.header("⚙️ Sensor Input Parameters")

with st.sidebar.form("sensor_form"):
    air_temp = st.number_input("Air Temperature (K)", value=298.0, min_value=290.0, max_value=310.0, step=0.5)
    process_temp = st.number_input("Process Temperature (K)", value=308.0, min_value=300.0, max_value=320.0, step=0.5)
    rotational_speed = st.number_input("Rotational Speed (RPM)", value=1500.0, min_value=1000.0, max_value=2000.0, step=50.0)
    torque = st.number_input("Torque (Nm)", value=40.0, min_value=20.0, max_value=80.0, step=1.0)
    tool_wear = st.number_input("Tool Wear (min)", value=100.0, min_value=0.0, max_value=250.0, step=10.0)
    vibration = st.number_input("Vibration (mm/s)", value=0.5, min_value=0.0, max_value=2.0, step=0.05)
    humidity = st.number_input("Humidity (%)", value=60.0, min_value=30.0, max_value=90.0, step=5.0)
    pressure = st.number_input("Pressure (bar)", value=1.0, min_value=0.8, max_value=1.2, step=0.05)
    
    predict_button = st.form_submit_button("🔮 Predict Quality", use_container_width=True)

# Main content
if predict_button:
    st.markdown("### 🔍 Prediction Results")
    
    try:
        from modules.quality.predictive_model import QualityPredictiveModel, create_demo_model
        from pathlib import Path
        
        with st.spinner("Running quality prediction..."):
            # Try to load model
            model_path = Path("models/quality_model.pkl")
            
            try:
                if model_path.exists():
                    model = QualityPredictiveModel(model_path=model_path)
                else:
                    model = create_demo_model()
                    model_path.parent.mkdir(parents=True, exist_ok=True)
                    model.save_model(model_path)
            except Exception:
                model = create_demo_model()
            
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
            
            # Predict
            result = model.predict_defect_probability(sensor_data)
        
        # Display results in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Defect probability gauge
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=result.defect_probability * 100,
                title={'text': "Defect Probability (%)"},
                delta={'reference': 50},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkred" if result.defect_probability > 0.75 else "orange" if result.defect_probability > 0.5 else "yellow" if result.defect_probability > 0.25 else "green"},
                    'steps': [
                        {'range': [0, 25], 'color': "lightgreen"},
                        {'range': [25, 50], 'color': "lightyellow"},
                        {'range': [50, 75], 'color': "orange"},
                        {'range': [75, 100], 'color': "lightcoral"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 50
                    }
                }
            ))
            fig_gauge.update_layout(height=300)
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        with col2:
            # Risk level
            risk_color = {
                "LOW": "🟢",
                "MEDIUM": "🟡",
                "HIGH": "🟠",
                "CRITICAL": "🔴"
            }
            st.metric(
                label="Risk Level",
                value=result.risk_level,
                delta=risk_color.get(result.risk_level, "")
            )
            
            st.metric(
                label="Prediction",
                value="DEFECT" if result.is_defect_predicted else "OK",
                delta="Reject" if result.is_defect_predicted else "Accept"
            )
        
        with col3:
            st.metric(
                label="Confidence",
                value=f"{(1 - abs(result.defect_probability - 0.5) * 2) * 100:.1f}%"
            )
            
            st.metric(
                label="Quality Score",
                value=f"{(1 - result.defect_probability) * 100:.1f}%"
            )
        
        st.markdown("---")
        
        # Feature contributions
        st.markdown("### 📊 Feature Contributions (SHAP Values)")
        st.markdown("Features that increase defect risk are shown in red, those that decrease it in blue.")
        
        # Sort features by absolute contribution
        contributions = result.feature_contributions
        sorted_features = sorted(contributions.items(), key=lambda x: abs(x[1]), reverse=True)
        
        feature_names = [f[0].replace('_', ' ').title() for f in sorted_features]
        feature_values = [f[1] for f in sorted_features]
        
        # Create horizontal bar chart
        colors = ['red' if v > 0 else 'blue' for v in feature_values]
        
        fig_features = go.Figure(go.Bar(
            y=feature_names,
            x=feature_values,
            orientation='h',
            marker=dict(color=colors),
            text=[f"{v:+.3f}" for v in feature_values],
            textposition='auto'
        ))
        
        fig_features.update_layout(
            title="Feature Impact on Defect Probability",
            xaxis_title="SHAP Value (Impact on Prediction)",
            yaxis_title="Feature",
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig_features, use_container_width=True)
        
        # Recommendations
        st.markdown("### 💡 Recommendations")
        for rec in result.recommendations:
            if "CRITICAL" in rec or "🚨" in rec:
                st.error(rec)
            elif "WARNING" in rec or "HIGH RISK" in rec or "⚠️" in rec:
                st.warning(rec)
            elif "MEDIUM" in rec:
                st.info(rec)
            else:
                st.success(rec)
    
    except Exception as e:
        st.error(f"❌ Error during prediction: {str(e)}")
        st.info("💡 Make sure all required dependencies are installed and the model can be loaded.")

else:
    st.info("👈 Configure sensor parameters in the sidebar and click **Predict Quality** to get results.")

# SPC Analysis Section
st.markdown("---")
st.markdown("### 📈 Statistical Process Control (SPC) Analysis")

try:
    from modules.quality.spc_analysis import SPCAnalyzer
    
    # Generate demo data for SPC chart
    np.random.seed(42)
    n_samples = 100
    data = pd.Series(np.random.normal(100, 5, n_samples))
    
    analyzer = SPCAnalyzer()
    spc_result = analyzer.analyze_xbar(data, subgroup_size=5, usl=115, lsl=85)
    
    # Display SPC metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Center Line (X̄)", f"{spc_result.center_line:.2f}")
    with col2:
        st.metric("UCL", f"{spc_result.ucl:.2f}")
    with col3:
        st.metric("LCL", f"{spc_result.lcl:.2f}")
    with col4:
        if spc_result.process_capability:
            st.metric("Cpk", f"{spc_result.process_capability['Cpk']:.2f}")
    
    # Create SPC control chart
    subgroup_size = 5
    n_subgroups = len(data) // subgroup_size
    subgroup_means = [np.mean(data[i*subgroup_size:(i+1)*subgroup_size]) for i in range(n_subgroups)]
    
    fig_spc = go.Figure()
    
    # Add subgroup means
    fig_spc.add_trace(go.Scatter(
        x=list(range(len(subgroup_means))),
        y=subgroup_means,
        mode='lines+markers',
        name='Subgroup Mean',
        line=dict(color='blue')
    ))
    
    # Add control limits
    fig_spc.add_hline(y=spc_result.center_line, line_dash="dash", line_color="green", annotation_text="X̄")
    fig_spc.add_hline(y=spc_result.ucl, line_dash="dash", line_color="red", annotation_text="UCL")
    fig_spc.add_hline(y=spc_result.lcl, line_dash="dash", line_color="red", annotation_text="LCL")
    
    if spc_result.usl:
        fig_spc.add_hline(y=spc_result.usl, line_dash="dot", line_color="orange", annotation_text="USL")
    if spc_result.lsl:
        fig_spc.add_hline(y=spc_result.lsl, line_dash="dot", line_color="orange", annotation_text="LSL")
    
    # Highlight out-of-control points
    if spc_result.out_of_control_points:
        ooc_x = spc_result.out_of_control_points
        ooc_y = [subgroup_means[i] for i in ooc_x if i < len(subgroup_means)]
        fig_spc.add_trace(go.Scatter(
            x=ooc_x,
            y=ooc_y,
            mode='markers',
            name='Out of Control',
            marker=dict(color='red', size=12, symbol='x')
        ))
    
    fig_spc.update_layout(
        title="X-bar Control Chart",
        xaxis_title="Subgroup Number",
        yaxis_title="Mean Value",
        height=400,
        showlegend=True
    )
    
    st.plotly_chart(fig_spc, use_container_width=True)
    
    # Show violations if any
    if spc_result.violations:
        st.warning("⚠️ Control Chart Violations Detected:")
        for idx, violation_type in spc_result.violations[:5]:  # Show first 5
            st.markdown(f"- Subgroup {idx}: {violation_type}")
    else:
        st.success("✅ Process is in statistical control")

except Exception as e:
    st.error(f"Error in SPC analysis: {str(e)}")

st.markdown("---")
st.caption("AI-ERP Quality Module v1.0.0 | Quality Prediction Module")
