"""
Vision Inspection Dashboard Page

Streamlit page for visual inspection and anomaly detection
with image upload, defect detection, and quality assessment.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from modules.vision.visual_inspection import VisualInspector
from modules.vision.anomaly_detector import AnomalyDetector
import io
from PIL import Image

st.set_page_config(page_title="Vision Inspection", page_icon="👁️", layout="wide")

st.title("👁️ Visual Inspection & Anomaly Detection")
st.markdown("### OpenCV-based Quality Inspection")
st.markdown("---")

# Initialize inspectors
@st.cache_resource
def get_inspector():
    return VisualInspector()

@st.cache_resource
def get_detector():
    return AnomalyDetector()

inspector = get_inspector()
detector = get_detector()

# File uploader
uploaded_file = st.file_uploader(
    "📤 Upload an image for inspection",
    type=['png', 'jpg', 'jpeg', 'bmp'],
    help="Upload an image to perform visual inspection and anomaly detection"
)

if uploaded_file is not None:
    # Display uploaded image
    image = Image.open(uploaded_file)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📷 Uploaded Image")
        st.image(image, use_container_width=True)
    
    with col2:
        st.subheader("ℹ️ Image Information")
        st.markdown(f"""
        - **Filename:** {uploaded_file.name}
        - **Format:** {image.format}
        - **Size:** {image.size[0]} x {image.size[1]} pixels
        - **File Size:** {uploaded_file.size / 1024:.2f} KB
        """)
    
    st.markdown("---")
    
    # Perform inspections
    if st.button("🔍 Run Inspection", type="primary"):
        with st.spinner("Analyzing image..."):
            # Reset file pointer
            uploaded_file.seek(0)
            image_bytes = uploaded_file.read()
            
            # Visual inspection
            try:
                inspection_result = inspector.inspect_bytes(image_bytes)
            except Exception as e:
                st.error(f"Visual inspection failed: {e}")
                inspection_result = None
            
            # Anomaly detection
            try:
                anomaly_result = detector.detect_bytes(image_bytes)
            except Exception as e:
                st.error(f"Anomaly detection failed: {e}")
                anomaly_result = None
            
            # Display results
            if inspection_result:
                st.header("🔍 Visual Inspection Results")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    defect_icon = "❌" if inspection_result['defects_found'] else "✅"
                    st.metric(
                        "Defects Found",
                        f"{defect_icon} {inspection_result['defect_count']}"
                    )
                
                with col2:
                    score = inspection_result['quality_score']
                    if score >= 90:
                        score_color = "🟢"
                    elif score >= 75:
                        score_color = "🟡"
                    elif score >= 60:
                        score_color = "🟠"
                    else:
                        score_color = "🔴"
                    st.metric(
                        "Quality Score",
                        f"{score_color} {score}/100"
                    )
                
                with col3:
                    st.metric(
                        "Inspection Time",
                        f"{inspection_result['inspection_time_ms']:.1f} ms"
                    )
                
                with col4:
                    brightness = inspection_result['image_metrics']['brightness']
                    st.metric(
                        "Brightness",
                        f"{brightness:.1f}"
                    )
                
                # Defect regions
                if inspection_result['defect_regions']:
                    st.subheader("📍 Defect Regions")
                    defect_df = pd.DataFrame(inspection_result['defect_regions'])
                    st.dataframe(defect_df, use_container_width=True, hide_index=True)
                
                # Image metrics
                st.subheader("📊 Image Quality Metrics")
                metrics = inspection_result['image_metrics']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=metrics['brightness'],
                        title={'text': "Brightness"},
                        gauge={'axis': {'range': [0, 255]},
                               'bar': {'color': "darkblue"},
                               'steps': [
                                   {'range': [0, 85], 'color': "lightgray"},
                                   {'range': [85, 170], 'color': "lightgreen"},
                                   {'range': [170, 255], 'color': "lightyellow"}
                               ]}
                    ))
                    fig.update_layout(height=250)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=metrics['contrast'],
                        title={'text': "Contrast (Std Dev)"},
                        gauge={'axis': {'range': [0, 100]},
                               'bar': {'color': "darkgreen"},
                               'steps': [
                                   {'range': [0, 30], 'color': "lightcoral"},
                                   {'range': [30, 70], 'color': "lightgreen"},
                                   {'range': [70, 100], 'color': "lightyellow"}
                               ]}
                    ))
                    fig.update_layout(height=250)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Recommendations
                st.subheader("💡 Inspection Recommendations")
                for rec in inspection_result['recommendations']:
                    if "🚨" in rec:
                        st.error(rec)
                    elif "⚠️" in rec:
                        st.warning(rec)
                    else:
                        st.info(rec)
            
            st.markdown("---")
            
            # Anomaly detection results
            if anomaly_result:
                st.header("🔎 Anomaly Detection Results")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    anomaly_icon = "⚠️" if anomaly_result['is_anomaly'] else "✅"
                    st.metric(
                        "Anomaly Status",
                        f"{anomaly_icon} {'DETECTED' if anomaly_result['is_anomaly'] else 'NONE'}"
                    )
                
                with col2:
                    st.metric(
                        "Anomaly Score",
                        f"{anomaly_result['anomaly_score']:.3f}"
                    )
                
                with col3:
                    type_icon = {
                        'NONE': '✅',
                        'BRIGHTNESS': '💡',
                        'NOISE': '📡',
                        'TEXTURE': '🎨',
                        'DEFECT': '❌'
                    }
                    st.metric(
                        "Anomaly Type",
                        f"{type_icon.get(anomaly_result['anomaly_type'], '❓')} {anomaly_result['anomaly_type']}"
                    )
                
                with col4:
                    st.metric(
                        "Confidence",
                        f"{anomaly_result['confidence']:.1%}"
                    )
                
                # Detailed scores
                st.subheader("📊 Anomaly Detection Breakdown")
                
                details = anomaly_result['details']
                scores_df = pd.DataFrame([{
                    'Analysis Type': 'Brightness Anomaly',
                    'Score': details['brightness_score']
                }, {
                    'Analysis Type': 'Noise Anomaly',
                    'Score': details['noise_score']
                }, {
                    'Analysis Type': 'Texture Anomaly',
                    'Score': details['texture_score']
                }, {
                    'Analysis Type': 'Defect Anomaly',
                    'Score': details['defect_score']
                }])
                
                fig = px.bar(
                    scores_df,
                    x='Score',
                    y='Analysis Type',
                    orientation='h',
                    title='Anomaly Scores by Type (0.0 - 1.0)',
                    color='Score',
                    color_continuous_scale='Reds'
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
                
                # Additional metrics
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Brightness Analysis**")
                    st.markdown(f"- Mean: {details['brightness_mean']:.2f}")
                    st.markdown(f"- Std Dev: {details['brightness_std']:.2f}")
                
                with col2:
                    st.markdown("**Detection Summary**")
                    if anomaly_result['is_anomaly']:
                        st.warning(f"⚠️ {anomaly_result['anomaly_type']} anomaly detected with {anomaly_result['confidence']:.0%} confidence")
                    else:
                        st.success("✅ No significant anomalies detected")

else:
    st.info("👆 Upload an image to begin inspection")
    
    st.markdown("---")
    
    st.subheader("📚 Inspection Capabilities")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Visual Inspection
        
        - ✅ Edge detection (Canny algorithm)
        - ✅ Contour analysis for defect regions
        - ✅ Brightness and contrast analysis
        - ✅ Quality scoring (0-100)
        - ✅ Defect counting and localization
        - ✅ Actionable recommendations
        """)
    
    with col2:
        st.markdown("""
        ### Anomaly Detection
        
        - ✅ Brightness anomaly detection
        - ✅ Noise level analysis
        - ✅ Texture analysis (Laplacian variance)
        - ✅ Defect-like pattern detection
        - ✅ Multi-method scoring
        - ✅ Confidence assessment
        """)
    
    st.markdown("---")
    
    st.subheader("💡 Usage Tips")
    st.markdown("""
    - **Best Results**: Upload clear, well-lit images with good contrast
    - **Supported Formats**: PNG, JPEG, JPG, BMP
    - **Image Size**: Larger images may take longer to process
    - **Multiple Inspections**: Upload different images to compare results
    """)

st.markdown("---")
st.caption("Vision Inspection Module | Powered by OpenCV")
