"""
Supplier Scoring Dashboard Page
K-Means clustering + IsolationForest supplier risk scoring
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Supplier Scoring", page_icon="🚚", layout="wide")

st.title("🚚 Supplier Scoring & Procurement Advisory")
st.markdown("### Intelligent Supplier Risk Assessment")
st.markdown("---")

# Sidebar input form
st.sidebar.header("📝 Supplier Metrics")

with st.sidebar.form("supplier_form"):
    supplier_id = st.text_input("Supplier ID", value="SUP-001")
    
    st.markdown("##### Performance Metrics")
    quality_score = st.slider("Quality Score", 0.0, 1.0, 0.85, 0.01)
    on_time_delivery = st.slider("On-Time Delivery Rate", 0.0, 1.0, 0.90, 0.01)
    defect_rate = st.slider("Defect Rate", 0.0, 0.20, 0.03, 0.01)
    
    st.markdown("##### Business Metrics")
    price_comp = st.slider("Price Competitiveness", 0.0, 1.0, 0.75, 0.01)
    response_time = st.number_input("Response Time (days)", 0.0, 10.0, 2.0, 0.5)
    years_partnership = st.number_input("Years of Partnership", 0.0, 20.0, 3.0, 0.5)
    
    score_button = st.form_submit_button("📊 Score Supplier", use_container_width=True)
    advise_button = st.form_submit_button("💡 Get Procurement Advice", use_container_width=True)

# Main content
if score_button or advise_button:
    supplier_data = {
        'supplier_id': supplier_id,
        'quality_score': quality_score,
        'on_time_delivery_rate': on_time_delivery,
        'defect_rate': defect_rate,
        'price_competitiveness': price_comp,
        'response_time_days': response_time,
        'years_of_partnership': years_partnership
    }
    
    try:
        from modules.supplier.supplier_score import SupplierScorer
        from modules.supplier.procurement_advisor import ProcurementAdvisor
        
        if score_button:
            st.markdown("### 📊 Supplier Scoring Results")
            
            with st.spinner("Analyzing supplier performance..."):
                scorer = SupplierScorer()
                result = scorer.score(supplier_data)
            
            # Display overall score
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Score gauge
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=result['overall_score'],
                    title={'text': "Overall Score"},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkgreen" if result['overall_score'] >= 85 else "orange" if result['overall_score'] >= 70 else "red"},
                        'steps': [
                            {'range': [0, 55], 'color': "lightcoral"},
                            {'range': [55, 70], 'color': "lightyellow"},
                            {'range': [70, 85], 'color': "lightblue"},
                            {'range': [85, 100], 'color': "lightgreen"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 70
                        }
                    }
                ))
                fig_gauge.update_layout(height=300)
                st.plotly_chart(fig_gauge, use_container_width=True)
            
            with col2:
                # Risk level
                risk_badges = {
                    "LOW": "🟢 LOW RISK",
                    "MEDIUM": "🟡 MEDIUM RISK",
                    "HIGH": "🟠 HIGH RISK",
                    "CRITICAL": "🔴 CRITICAL RISK"
                }
                
                st.markdown("#### Risk Level")
                if result['risk_level'] == "CRITICAL":
                    st.error(risk_badges[result['risk_level']])
                elif result['risk_level'] == "HIGH":
                    st.warning(risk_badges[result['risk_level']])
                elif result['risk_level'] == "MEDIUM":
                    st.info(risk_badges[result['risk_level']])
                else:
                    st.success(risk_badges[result['risk_level']])
                
                st.markdown("#### Category")
                category_colors = {
                    "PREFERRED": "success",
                    "APPROVED": "info",
                    "CONDITIONAL": "warning",
                    "DISQUALIFIED": "error"
                }
                
                if result['category'] == "PREFERRED":
                    st.success(f"✅ {result['category']}")
                elif result['category'] == "APPROVED":
                    st.info(f"✓ {result['category']}")
                elif result['category'] == "CONDITIONAL":
                    st.warning(f"⚠️ {result['category']}")
                else:
                    st.error(f"❌ {result['category']}")
            
            with col3:
                # Key metrics
                st.metric("Quality Score", f"{result['metrics']['quality_score']:.0%}")
                st.metric("On-Time Delivery", f"{result['metrics']['on_time_delivery_rate']:.0%}")
                st.metric("Defect Rate", f"{result['metrics']['defect_rate']:.1%}")
                st.metric("Partnership", f"{result['metrics']['years_of_partnership']:.1f} years")
            
            st.markdown("---")
            
            # Score breakdown
            st.markdown("### 📈 Score Breakdown")
            
            breakdown = result['breakdown']
            
            # Radar chart
            categories = [
                'Quality Score',
                'On-Time Delivery',
                'Defect Rate Score',
                'Price Competitiveness',
                'Response Time Score'
            ]
            
            values = [
                breakdown['quality_score'],
                breakdown['on_time_delivery'],
                breakdown['defect_rate_score'],
                breakdown['price_competitiveness'],
                breakdown['response_time_score']
            ]
            
            fig_radar = go.Figure(data=go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                line_color='blue'
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )
                ),
                showlegend=False,
                title="Performance Radar Chart",
                height=400
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
            
            # Breakdown table
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Component Scores")
                breakdown_df = pd.DataFrame([
                    {"Metric": "Quality Score", "Value": breakdown['quality_score']},
                    {"Metric": "On-Time Delivery", "Value": breakdown['on_time_delivery']},
                    {"Metric": "Defect Rate Score", "Value": breakdown['defect_rate_score']},
                    {"Metric": "Price Competitiveness", "Value": breakdown['price_competitiveness']},
                    {"Metric": "Response Time Score", "Value": breakdown['response_time_score']},
                    {"Metric": "Partnership Bonus", "Value": breakdown['partnership_bonus']}
                ])
                st.dataframe(breakdown_df, use_container_width=True, hide_index=True)
            
            with col2:
                st.markdown("#### Recommendations")
                for rec in result['recommendations']:
                    if "CRITICAL" in rec or "🚨" in rec or "❌" in rec:
                        st.error(rec)
                    elif "WARNING" in rec or "HIGH RISK" in rec or "⚠️" in rec:
                        st.warning(rec)
                    elif "EXCELLENT" in rec or "GOOD" in rec or "✅" in rec:
                        st.success(rec)
                    else:
                        st.info(rec)
            
            # Anomaly detection
            if result.get('anomaly_detected'):
                st.warning("⚠️ **Anomaly Detected:** This supplier's metrics show unusual patterns. Additional review recommended.")
        
        if advise_button:
            st.markdown("### 💡 Procurement Advisory")
            
            with st.spinner("Generating procurement advice..."):
                advisor = ProcurementAdvisor()
                advice = advisor.advise(supplier_data)
            
            # Display advice
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### Recommended Action")
                
                action_display = {
                    "RECOMMEND": ("🟢 RECOMMEND", "success"),
                    "MONITOR": ("🟡 MONITOR", "info"),
                    "REVIEW": ("🟠 REVIEW", "warning"),
                    "REJECT": ("🔴 REJECT", "error")
                }
                
                action_text, action_type = action_display.get(advice['action'], ("UNKNOWN", "info"))
                
                if action_type == "success":
                    st.success(action_text)
                elif action_type == "error":
                    st.error(action_text)
                elif action_type == "warning":
                    st.warning(action_text)
                else:
                    st.info(action_text)
                
                st.metric("Confidence", f"{advice['confidence'] * 100:.0f}%")
            
            with col2:
                st.markdown("#### Suggested Order Volume")
                volume_colors = {
                    "NONE": "error",
                    "LOW": "warning",
                    "MEDIUM": "info",
                    "HIGH": "success"
                }
                
                volume = advice['suggested_order_volume']
                if volume == "NONE":
                    st.error(f"❌ {volume}")
                elif volume == "LOW":
                    st.warning(f"🔻 {volume}")
                elif volume == "MEDIUM":
                    st.info(f"➖ {volume}")
                else:
                    st.success(f"🔺 {volume}")
                
                st.metric("Composite Score", f"{advice['composite_score']:.1f}")
            
            with col3:
                st.markdown("#### Risk vs Opportunity")
                st.metric("Risk Factors", len(advice['risk_factors']))
                st.metric("Opportunities", len(advice['opportunities']))
            
            st.markdown("---")
            
            # Reasoning
            st.markdown("### 📝 Advisory Reasoning")
            st.info(advice['reasoning'])
            
            # Risk factors and opportunities
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### ⚠️ Risk Factors")
                if advice['risk_factors']:
                    for risk in advice['risk_factors']:
                        st.warning(f"• {risk}")
                else:
                    st.success("✓ No significant risk factors identified")
            
            with col2:
                st.markdown("#### 💎 Opportunities")
                if advice['opportunities']:
                    for opp in advice['opportunities']:
                        st.success(f"• {opp}")
                else:
                    st.info("• No specific opportunities identified")
    
    except Exception as e:
        st.error(f"❌ Error during analysis: {str(e)}")
        st.info("💡 Make sure all supplier modules are properly installed.")

else:
    st.info("👈 Configure supplier metrics in the sidebar and click **Score Supplier** or **Get Procurement Advice** to see results.")
    
    # Sample supplier comparison
    st.markdown("### 📊 Sample Supplier Comparison")
    
    sample_data = pd.DataFrame([
        {"Supplier": "SUP-001", "Score": 87.5, "Risk": "LOW", "Category": "PREFERRED"},
        {"Supplier": "SUP-002", "Score": 76.2, "Risk": "MEDIUM", "Category": "APPROVED"},
        {"Supplier": "SUP-003", "Score": 92.1, "Risk": "LOW", "Category": "PREFERRED"},
        {"Supplier": "SUP-004", "Score": 65.8, "Risk": "HIGH", "Category": "CONDITIONAL"},
        {"Supplier": "SUP-005", "Score": 71.3, "Risk": "MEDIUM", "Category": "APPROVED"},
    ])
    
    st.dataframe(sample_data, use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("AI-ERP Quality Module v1.0.0 | Supplier Scoring Module")
