"""
Supplier Scoring Dashboard Page

Streamlit page for supplier risk scoring and procurement advisory
with weighted scoring and actionable recommendations.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from modules.supplier.supplier_score import SupplierScorer
from modules.supplier.procurement_advisor import ProcurementAdvisor

st.set_page_config(page_title="Supplier Scoring", page_icon="🚚", layout="wide")

st.title("🚚 Supplier Risk Scoring")
st.markdown("### Weighted Scoring & Procurement Advisory")
st.markdown("---")

# Initialize scorers
@st.cache_resource
def get_scorer():
    return SupplierScorer()

@st.cache_resource
def get_advisor():
    return ProcurementAdvisor()

scorer = get_scorer()
advisor = get_advisor()

# Supplier input form
st.sidebar.header("📋 Supplier Information")
st.sidebar.markdown("Enter supplier performance metrics:")

supplier_data = {
    'supplier_id': st.sidebar.text_input("Supplier ID", value="SUP-001"),
    'on_time_delivery_rate': st.sidebar.slider(
        "On-Time Delivery Rate (%)",
        min_value=0.0, max_value=100.0, value=90.0, step=1.0
    ) / 100,
    'quality_score': st.sidebar.slider(
        "Quality Score (%)",
        min_value=0.0, max_value=100.0, value=85.0, step=1.0
    ) / 100,
    'price_competitiveness': st.sidebar.slider(
        "Price Competitiveness (%)",
        min_value=0.0, max_value=100.0, value=75.0, step=1.0
    ) / 100,
    'defect_rate': st.sidebar.slider(
        "Defect Rate (%)",
        min_value=0.0, max_value=20.0, value=3.0, step=0.5
    ) / 100,
    'response_time_days': st.sidebar.number_input(
        "Response Time (days)",
        min_value=0.0, max_value=30.0, value=2.0, step=0.5
    ),
    'years_of_partnership': st.sidebar.number_input(
        "Years of Partnership",
        min_value=0.0, max_value=50.0, value=3.0, step=0.5
    )
}

if st.sidebar.button("📊 Analyze Supplier", type="primary"):
    with st.spinner("Analyzing supplier..."):
        # Get score
        score_result = scorer.score(supplier_data)
        
        # Get procurement advice
        advice_result = advisor.advise(supplier_data)
        
        # Display overall score
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Overall Score",
                f"{score_result['overall_score']:.1f}/100"
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
                f"{risk_color.get(score_result['risk_level'], '⚪')} {score_result['risk_level']}"
            )
        
        with col3:
            category_icon = {
                "PREFERRED": "⭐",
                "APPROVED": "✅",
                "CONDITIONAL": "⚠️",
                "DISQUALIFIED": "❌"
            }
            st.metric(
                "Category",
                f"{category_icon.get(score_result['category'], '❓')} {score_result['category']}"
            )
        
        st.markdown("---")
        
        # Score breakdown
        st.subheader("📊 Score Breakdown")
        
        breakdown = score_result['breakdown']
        breakdown_df = pd.DataFrame([
            {"Metric": k.replace('_', ' ').title(), "Score": v}
            for k, v in breakdown.items()
        ])
        
        fig = px.bar(
            breakdown_df,
            x="Score",
            y="Metric",
            orientation='h',
            title="Weighted Score Components (0-100)",
            color="Score",
            color_continuous_scale="RdYlGn"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Weighted contribution
        st.markdown("#### ⚖️ Weight Distribution")
        weights = {
            'Quality Score': 30,
            'On-Time Delivery': 25,
            'Defect Rate': 20,
            'Price Competitiveness': 15,
            'Response Time': 10
        }
        
        fig = go.Figure(data=[go.Pie(
            labels=list(weights.keys()),
            values=list(weights.values()),
            hole=.3
        )])
        fig.update_layout(title="Scoring Weights (%)", height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Procurement advice
        st.subheader("💼 Procurement Advisory")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            action_color = {
                "RECOMMEND": "green",
                "MONITOR": "blue",
                "REVIEW": "orange",
                "REJECT": "red"
            }
            st.markdown(f"**Action:** :{action_color.get(advice_result['action'], 'gray')}[{advice_result['action']}]")
        
        with col2:
            st.markdown(f"**Confidence:** {advice_result['confidence']:.1%}")
        
        with col3:
            st.markdown(f"**Order Volume:** {advice_result['suggested_order_volume']}")
        
        st.markdown("#### 💭 Reasoning")
        st.info(advice_result['reasoning'])
        
        # Risk factors
        if advice_result['risk_factors']:
            st.markdown("#### ⚠️ Risk Factors")
            for risk in advice_result['risk_factors']:
                st.warning(f"• {risk}")
        
        # Opportunities
        if advice_result['opportunities']:
            st.markdown("#### ✨ Opportunities")
            for opp in advice_result['opportunities']:
                st.success(f"• {opp}")
        
        st.markdown("---")
        
        # Recommendations
        st.subheader("💡 Recommendations")
        for rec in score_result['recommendations']:
            if "🚨" in rec:
                st.error(rec)
            elif "⚠️" in rec or "💰" in rec or "⏱️" in rec:
                st.warning(rec)
            else:
                st.info(rec)
        
        # Input data table
        st.markdown("---")
        st.subheader("📋 Supplier Input Data")
        input_df = pd.DataFrame([{
            'Metric': 'Supplier ID',
            'Value': supplier_data['supplier_id']
        }, {
            'Metric': 'On-Time Delivery Rate',
            'Value': f"{supplier_data['on_time_delivery_rate']*100:.1f}%"
        }, {
            'Metric': 'Quality Score',
            'Value': f"{supplier_data['quality_score']*100:.1f}%"
        }, {
            'Metric': 'Price Competitiveness',
            'Value': f"{supplier_data['price_competitiveness']*100:.1f}%"
        }, {
            'Metric': 'Defect Rate',
            'Value': f"{supplier_data['defect_rate']*100:.2f}%"
        }, {
            'Metric': 'Response Time',
            'Value': f"{supplier_data['response_time_days']:.1f} days"
        }, {
            'Metric': 'Years of Partnership',
            'Value': f"{supplier_data['years_of_partnership']:.1f} years"
        }])
        st.dataframe(input_df, use_container_width=True, hide_index=True)

else:
    st.info("👈 Enter supplier information in the sidebar and click 'Analyze Supplier'")
    
    st.subheader("📚 Scoring Methodology")
    
    st.markdown("""
    ### Weighted Scoring System
    
    Suppliers are evaluated based on the following weighted criteria:
    
    - **Quality Score (30%)**: Product quality assessment
    - **On-Time Delivery (25%)**: Delivery reliability
    - **Defect Rate (20%)**: Product defect frequency (inverted)
    - **Price Competitiveness (15%)**: Pricing advantage
    - **Response Time (10%)**: Communication responsiveness (inverted)
    
    ### Risk Levels
    
    - 🟢 **LOW**: Score ≥ 80, excellent performance
    - 🟡 **MEDIUM**: Score 65-79, acceptable with monitoring
    - 🟠 **HIGH**: Score 50-64, requires improvement
    - 🔴 **CRITICAL**: Score < 50, unacceptable performance
    
    ### Supplier Categories
    
    - ⭐ **PREFERRED**: Top-tier suppliers (score ≥ 85)
    - ✅ **APPROVED**: Acceptable suppliers (score 70-84)
    - ⚠️ **CONDITIONAL**: Conditional approval (score 50-69)
    - ❌ **DISQUALIFIED**: Not approved (score < 50 or critical issues)
    """)

st.markdown("---")
st.caption("Supplier Scoring Module | Weighted Multi-Criteria Analysis")
