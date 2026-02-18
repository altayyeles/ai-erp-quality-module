"""
Visual Inspection Dashboard Page
Streamlit page for computer vision-based quality inspection
"""

import streamlit as st
from io import BytesIO
from PIL import Image
import numpy as np

st.set_page_config(page_title="Visual Inspection", page_icon="👁️", layout="wide")

st.title("👁️ Visual Inspection & Anomaly Detection")
st.markdown("---")

# File uploader
st.subheader("📤 Upload Image for Inspection")

uploaded_file = st.file_uploader(
    "Choose an image file (JPG, PNG, BMP)",
    type=['jpg', 'jpeg', 'png', 'bmp'],
    help="Upload a product image for quality inspection"
)

if uploaded_file is not None:
    # Display uploaded image
    image = Image.open(uploaded_file)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 📸 Uploaded Image")
        st.image(image, use_column_width=True)
        st.caption(f"Size: {image.size[0]} x {image.size[1]} pixels")
    
    with col2:
        st.markdown("#### 🔍 Inspection Options")
        
        inspection_mode = st.radio(
            "Select Inspection Mode",
            ["Visual Inspection", "Anomaly Detection", "Both"],
            help="Choose the type of analysis to perform"
        )
        
        inspect_button = st.button("🔍 Run Inspection", use_container_width=True, type="primary")
    
    if inspect_button:
        # Convert image to bytes
        img_bytes = BytesIO()
        image.save(img_bytes, format=image.format or 'PNG')
        image_bytes = img_bytes.getvalue()
        
        try:
            if inspection_mode in ["Visual Inspection", "Both"]:
                st.markdown("---")
                st.subheader("🔬 Visual Inspection Results")
                
                with st.spinner("Performing visual inspection..."):
                    from modules.vision.visual_inspection import VisualInspector
                    
                    inspector = VisualInspector()
                    result = inspector.inspect_bytes(image_bytes)
                    
                    # Metrics row
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        defect_status = "🔴 YES" if result['defects_found'] else "🟢 NO"
                        st.metric("Defects Found", defect_status)
                    
                    with col2:
                        st.metric("Defect Count", result['defect_count'])
                    
                    with col3:
                        quality_color = "🟢" if result['quality_score'] >= 80 else "🟡" if result['quality_score'] >= 60 else "🔴"
                        st.metric("Quality Score", f"{quality_color} {result['quality_score']:.1f}/100")
                    
                    with col4:
                        st.metric("Inspection Time", f"{result['inspection_time_ms']:.1f} ms")
                    
                    # Image quality metrics
                    st.markdown("#### 📊 Image Quality Metrics")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Brightness", f"{result.get('brightness_score', 0):.1f}/100")
                    
                    with col2:
                        st.metric("Contrast", f"{result.get('contrast_score', 0):.1f}/100")
                    
                    with col3:
                        if result.get('total_defect_area'):
                            img_area = result['image_size']['width'] * result['image_size']['height']
                            defect_pct = (result['total_defect_area'] / img_area) * 100
                            st.metric("Defect Area", f"{defect_pct:.2f}%")
                        else:
                            st.metric("Defect Area", "0%")
                    
                    # Defect regions
                    if result['defect_regions']:
                        st.markdown("#### 🎯 Detected Defect Regions")
                        
                        regions_data = []
                        for i, region in enumerate(result['defect_regions'][:10], 1):
                            regions_data.append({
                                "ID": i,
                                "X": region['x'],
                                "Y": region['y'],
                                "Width": region['width'],
                                "Height": region['height'],
                                "Area": region['area']
                            })
                        
                        import pandas as pd
                        st.dataframe(pd.DataFrame(regions_data), use_container_width=True, hide_index=True)
                    
                    # Recommendations
                    st.markdown("#### 💡 Inspection Recommendations")
                    
                    for rec in result['recommendations']:
                        if "FAIL" in rec or "🚫" in rec:
                            st.error(rec)
                        elif "WARNING" in rec or "⚠️" in rec or "MARGINAL" in rec:
                            st.warning(rec)
                        elif "PASS" in rec or "✅" in rec or "Excellent" in rec:
                            st.success(rec)
                        else:
                            st.info(rec)
            
            if inspection_mode in ["Anomaly Detection", "Both"]:
                st.markdown("---")
                st.subheader("🔮 Anomaly Detection Results")
                
                with st.spinner("Detecting anomalies..."):
                    from modules.vision.anomaly_detector import AnomalyDetector
                    
                    detector = AnomalyDetector()
                    result = detector.detect_bytes(image_bytes)
                    
                    # Metrics row
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        anomaly_status = "🔴 YES" if result['is_anomaly'] else "🟢 NO"
                        st.metric("Anomaly Detected", anomaly_status)
                    
                    with col2:
                        score_pct = result['anomaly_score'] * 100
                        st.metric("Anomaly Score", f"{score_pct:.1f}%")
                    
                    with col3:
                        st.metric("Anomaly Type", result['anomaly_type'])
                    
                    with col4:
                        confidence_pct = result['confidence'] * 100
                        st.metric("Confidence", f"{confidence_pct:.0f}%")
                    
                    # Detailed analysis
                    st.markdown("#### 📊 Detailed Analysis")
                    
                    details = result.get('details', {})
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Brightness Analysis**")
                        brightness = details.get('brightness', {})
                        st.progress(brightness.get('score', 0), 
                                  text=f"Score: {brightness.get('score', 0):.2f}")
                        st.caption(f"Mean: {brightness.get('mean', 0):.1f} | "
                                 f"Deviation: {brightness.get('deviation', 0):.1f}")
                        
                        st.markdown("**Texture Analysis**")
                        texture = details.get('texture', {})
                        st.progress(texture.get('score', 0), 
                                  text=f"Score: {texture.get('score', 0):.2f}")
                        st.caption(f"Uniformity: {texture.get('uniformity', 'unknown')}")
                    
                    with col2:
                        st.markdown("**Noise Analysis**")
                        noise = details.get('noise', {})
                        st.progress(noise.get('score', 0), 
                                  text=f"Score: {noise.get('score', 0):.2f}")
                        st.caption(f"Sharpness: {noise.get('sharpness', 'unknown')}")
                        
                        st.markdown("**Histogram Analysis**")
                        histogram = details.get('histogram', {})
                        st.progress(histogram.get('score', 0), 
                                  text=f"Score: {histogram.get('score', 0):.2f}")
                        st.caption(f"Distribution: {histogram.get('distribution', 'unknown')}")
                    
                    # Recommendations
                    st.markdown("#### 💡 Anomaly Detection Recommendations")
                    
                    for rec in result['recommendations']:
                        if "CRITICAL" in rec or "🚨" in rec:
                            st.error(rec)
                        elif "ANOMALY" in rec or "⚠️" in rec:
                            st.warning(rec)
                        elif "✅" in rec or "No significant" in rec:
                            st.success(rec)
                        else:
                            st.info(rec)
        
        except ImportError as e:
            st.error(f"❌ Required module not available: {str(e)}")
            st.info("💡 Please ensure vision modules (OpenCV, PIL) are properly installed.")
        
        except Exception as e:
            st.error(f"❌ Error during inspection: {str(e)}")
            st.info("💡 The image may be corrupted or in an unsupported format.")

else:
    # Placeholder when no image uploaded
    st.info("👆 Upload an image to begin inspection")
    
    st.markdown("---")
    st.subheader("📋 Inspection Capabilities")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔬 Visual Inspection")
        st.markdown("""
        - Edge detection using Canny algorithm
        - Contour analysis for defect identification
        - Brightness and contrast evaluation
        - Defect region mapping with coordinates
        - Quality scoring (0-100 scale)
        - Actionable recommendations
        """)
    
    with col2:
        st.markdown("#### 🔮 Anomaly Detection")
        st.markdown("""
        - Brightness anomaly detection
        - Noise and blur analysis
        - Texture uniformity assessment
        - Histogram distribution analysis
        - Multi-factor anomaly scoring
        - Confidence-based classification
        """)
    
    st.markdown("---")
    st.subheader("🎯 Supported Image Formats")
    st.markdown("• JPEG/JPG • PNG • BMP")
    
    st.markdown("---")
    st.subheader("💡 Tips for Best Results")
    st.markdown("""
    1. **Good Lighting**: Ensure uniform, adequate lighting without glare
    2. **Sharp Focus**: Use clear, in-focus images
    3. **Proper Framing**: Center the product in the frame
    4. **High Resolution**: Use at least 800x600 pixels
    5. **Clean Background**: Minimize background clutter
    """)

st.markdown("---")
st.caption("Visual Inspection Module | AI-ERP Quality System")
