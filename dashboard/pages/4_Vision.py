"""
Visual Inspection Dashboard Page
Computer vision-based defect detection and anomaly analysis
"""

import streamlit as st
import plotly.graph_objects as go
from PIL import Image
import io
import numpy as np

st.set_page_config(page_title="Visual Inspection", page_icon="👁️", layout="wide")

st.title("👁️ Visual Inspection & Anomaly Detection")
st.markdown("### Computer Vision-Based Quality Control")
st.markdown("---")

# File uploader
st.markdown("### 📤 Upload Image for Inspection")

uploaded_file = st.file_uploader(
    "Choose an image file (JPG, PNG, BMP)",
    type=['jpg', 'jpeg', 'png', 'bmp'],
    help="Upload a product image for visual inspection and defect detection"
)

col1, col2 = st.columns(2)

with col1:
    inspect_button = st.button("🔍 Visual Inspection", use_container_width=True, type="primary")

with col2:
    anomaly_button = st.button("⚠️ Detect Anomalies", use_container_width=True)

if uploaded_file is not None:
    # Display uploaded image
    st.markdown("### 🖼️ Uploaded Image")
    
    try:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        
        # Get image bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=image.format or 'PNG')
        image_bytes = img_byte_arr.getvalue()
        
        st.markdown("---")
        
        # Visual Inspection
        if inspect_button:
            st.markdown("### 🔍 Visual Inspection Results")
            
            try:
                from modules.vision.visual_inspection import VisualInspector
                
                with st.spinner("Analyzing image for defects..."):
                    inspector = VisualInspector()
                    result = inspector.inspect_bytes(image_bytes)
                
                # Display results
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if result['defects_found']:
                        st.error(f"❌ Defects Found")
                    else:
                        st.success(f"✅ No Defects")
                    st.metric("Defect Count", result['defect_count'])
                
                with col2:
                    st.metric("Quality Score", f"{result['quality_score']:.1f}/100")
                    
                    # Quality gauge
                    if result['quality_score'] >= 90:
                        st.success("EXCELLENT")
                    elif result['quality_score'] >= 75:
                        st.info("GOOD")
                    elif result['quality_score'] >= 60:
                        st.warning("FAIR")
                    else:
                        st.error("POOR")
                
                with col3:
                    metrics = result['image_metrics']
                    st.metric("Image Size", metrics['image_size'] if isinstance(metrics, dict) else f"{metrics.get('width', 0)}x{metrics.get('height', 0)}")
                    st.metric("Inspection Time", f"{result['inspection_time_ms']:.1f} ms")
                
                with col4:
                    if 'brightness' in metrics:
                        st.metric("Brightness", f"{metrics['brightness']:.1f}")
                        st.metric("Contrast", f"{metrics['contrast']:.1f}")
                
                # Defect regions
                if result['defect_regions'] and len(result['defect_regions']) > 0:
                    st.markdown("#### 📍 Detected Defect Regions")
                    
                    defect_df_data = []
                    for i, region in enumerate(result['defect_regions'][:10], 1):
                        defect_df_data.append({
                            "#": i,
                            "X": region['x'],
                            "Y": region['y'],
                            "Width": region['width'],
                            "Height": region['height'],
                            "Area": region['area'],
                            "Aspect Ratio": region.get('aspect_ratio', 'N/A')
                        })
                    
                    import pandas as pd
                    defect_df = pd.DataFrame(defect_df_data)
                    st.dataframe(defect_df, use_container_width=True, hide_index=True)
                    
                    # Visualize defect locations
                    if 'width' in metrics and 'height' in metrics:
                        fig = go.Figure()
                        
                        # Add image outline
                        fig.add_shape(
                            type="rect",
                            x0=0, y0=0,
                            x1=metrics['width'], y1=metrics['height'],
                            line=dict(color="gray", width=2)
                        )
                        
                        # Add defect regions
                        for region in result['defect_regions'][:10]:
                            fig.add_shape(
                                type="rect",
                                x0=region['x'],
                                y0=region['y'],
                                x1=region['x'] + region['width'],
                                y1=region['y'] + region['height'],
                                line=dict(color="red", width=2),
                                fillcolor="rgba(255, 0, 0, 0.2)"
                            )
                        
                        fig.update_layout(
                            title="Defect Location Map",
                            xaxis_title="X (pixels)",
                            yaxis_title="Y (pixels)",
                            height=400,
                            yaxis=dict(autorange="reversed")
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                
                # Recommendations
                st.markdown("#### 💡 Recommendations")
                for rec in result['recommendations']:
                    if "FAIL" in rec or "❌" in rec:
                        st.error(rec)
                    elif "WARNING" in rec or "⚠️" in rec:
                        st.warning(rec)
                    elif "PASS" in rec or "✅" in rec:
                        st.success(rec)
                    else:
                        st.info(rec)
            
            except Exception as e:
                st.error(f"❌ Visual inspection failed: {str(e)}")
        
        # Anomaly Detection
        if anomaly_button:
            st.markdown("### ⚠️ Anomaly Detection Results")
            
            try:
                from modules.vision.anomaly_detector import AnomalyDetector
                
                with st.spinner("Detecting anomalies..."):
                    detector = AnomalyDetector()
                    result = detector.detect_bytes(image_bytes)
                
                # Display results
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if result['is_anomaly']:
                        st.error("⚠️ ANOMALY DETECTED")
                    else:
                        st.success("✅ NORMAL")
                    
                    st.metric("Anomaly Score", f"{result['anomaly_score']:.3f}")
                
                with col2:
                    anomaly_type = result['anomaly_type']
                    
                    type_colors = {
                        "NONE": "success",
                        "BRIGHTNESS": "warning",
                        "NOISE": "warning",
                        "TEXTURE": "info",
                        "DEFECT": "error"
                    }
                    
                    st.markdown("**Anomaly Type**")
                    if anomaly_type == "NONE":
                        st.success(anomaly_type)
                    elif anomaly_type in ["BRIGHTNESS", "NOISE"]:
                        st.warning(anomaly_type)
                    elif anomaly_type == "DEFECT":
                        st.error(anomaly_type)
                    else:
                        st.info(anomaly_type)
                
                with col3:
                    st.metric("Confidence", f"{result['confidence'] * 100:.1f}%")
                    
                    if result['confidence'] >= 0.8:
                        st.success("HIGH")
                    elif result['confidence'] >= 0.6:
                        st.info("MEDIUM")
                    else:
                        st.warning("LOW")
                
                with col4:
                    if 'detection_time_ms' in result:
                        st.metric("Detection Time", f"{result['detection_time_ms']:.1f} ms")
                
                # Details
                st.markdown("#### 📊 Anomaly Analysis Details")
                
                details = result['details']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Image Statistics**")
                    st.metric("Brightness", f"{details.get('brightness', 'N/A')}")
                    st.metric("Contrast", f"{details.get('contrast', 'N/A')}")
                    st.metric("Noise Score", f"{details.get('noise_score', 'N/A')}")
                
                with col2:
                    st.markdown("**Quality Metrics**")
                    st.metric("Entropy", f"{details.get('entropy', 'N/A')}")
                    st.metric("Edge Density", f"{details.get('edge_density', 'N/A')}")
                    st.metric("Image Size", details.get('image_size', 'N/A'))
                
                # Detected anomalies
                if 'anomalies_detected' in details and details['anomalies_detected']:
                    st.markdown("#### 🔍 Specific Anomalies Detected")
                    anomalies = details['anomalies_detected']
                    
                    for anomaly in anomalies:
                        if isinstance(anomaly, str):
                            if 'low' in anomaly or 'excessive' in anomaly:
                                st.warning(f"• {anomaly.replace('_', ' ').title()}")
                            else:
                                st.info(f"• {anomaly.replace('_', ' ').title()}")
                
                # Anomaly score gauge
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=result['anomaly_score'] * 100,
                    title={'text': "Anomaly Score (%)"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "red" if result['anomaly_score'] > 0.7 else "orange" if result['anomaly_score'] > 0.5 else "yellow" if result['anomaly_score'] > 0.3 else "green"},
                        'steps': [
                            {'range': [0, 30], 'color': "lightgreen"},
                            {'range': [30, 50], 'color': "lightyellow"},
                            {'range': [50, 70], 'color': "orange"},
                            {'range': [70, 100], 'color': "lightcoral"}
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
            
            except Exception as e:
                st.error(f"❌ Anomaly detection failed: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Error loading image: {str(e)}")

else:
    st.info("👆 Upload an image to begin visual inspection and anomaly detection.")
    
    # Demo mode placeholder
    st.markdown("---")
    st.markdown("### 🎬 Demo Mode")
    st.markdown("""
    Without an uploaded image, you can still explore the features:
    
    **Visual Inspection Module:**
    - Edge detection using Canny algorithm
    - Contour analysis for defect identification
    - Brightness and contrast analysis
    - Quality scoring based on detected defects
    - YOLO-based detection with OpenCV fallback
    
    **Anomaly Detection Module:**
    - Histogram analysis for uniformity
    - Noise detection using Laplacian variance
    - Brightness anomaly detection
    - Texture analysis with entropy calculation
    - Edge density evaluation
    
    **Supported Formats:** JPG, JPEG, PNG, BMP
    
    **Typical Use Cases:**
    - Surface defect detection (scratches, dents, cracks)
    - Color uniformity verification
    - Dimensional anomaly detection
    - Print quality assessment
    - Assembly defect identification
    """)
    
    # Sample results visualization
    st.markdown("#### 📊 Sample Inspection Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Average Quality Score", "89.5/100")
        st.caption("Last 100 inspections")
    
    with col2:
        st.metric("Defect Detection Rate", "12.3%")
        st.caption("Products with defects")
    
    with col3:
        st.metric("Average Inspection Time", "45.2 ms")
        st.caption("Per image")

st.markdown("---")
st.caption("AI-ERP Quality Module v1.0.0 | Vision Inspection Module")
