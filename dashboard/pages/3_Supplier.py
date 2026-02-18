"""
Supplier Scoring Dashboard Page
Streamlit page for supplier performance evaluation and procurement advice
"""

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Supplier Scoring", page_icon="🚚", layout="wide")

st.title("🚚 Supplier Scoring & Procurement Advisory")
st.markdown("---")

# Supplier input form
st.subheader("📝 Supplier Performance Metrics")

with st.form("supplier_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        supplier_id = st.text_input(
            "Supplier ID",
            value="SUP-001",
            help="Unique supplier identifier"
        )
        
        quality_score = st.slider(
            "Quality Score",
            min_value=0.0,
            max_value=1.0,
            value=0.85,
            step=0.05,
            help="Overall quality rating (0-1)"
        )
        
        on_time_delivery = st.slider(
            "On-Time Delivery Rate",
            min_value=0.0,
            max_value=1.0,
            value=0.90,
            step=0.05,
            help="Percentage of on-time deliveries"
        )
        
        defect_rate = st.slider(
            "Defect Rate",
            min_value=0.0,
            max_value=0.20,
            value=0.03,
            step=0.01,
            help="Percentage of defective products"
        )
    
    with col2:
        price_competitiveness = st.slider(
            "Price Competitiveness",
            min_value=0.0,
            max_value=1.0,
            value=0.75,
            step=0.05,
            help="Price competitiveness score (0-1)"
        )
        
        response_time = st.number_input(
            "Response Time (days)",
            min_value=0.5,
            max_value=15.0,
            value=2.0,
            step=0.5,
            help="Average response time in days"
        )
        
        partnership_years = st.number_input(
            "Years of Partnership",
            min_value=0.0,
            max_value=20.0,
            value=3.0,
            step=0.5,
            help="Years working together"
        )
    
    col1, col2 = st.columns(2)
    
    with col1:
        score_button = st.form_submit_button("📊 Score Supplier", use_container_width=True)
    
    with col2:
        advise_button = st.form_submit_button("💡 Get Procurement Advice", use_container_width=True)

# Prepare supplier data
supplier_data = {
    'supplier_id': supplier_id,
    'quality_score': quality_score,
    'on_time_delivery_rate': on_time_delivery,
    'price_competitiveness': price_competitiveness,
    'defect_rate': defect_rate,
    'response_time_days': response_time,
    'years_of_partnership': partnership_years
}

try:
    from modules.supplier.supplier_score import SupplierScorer
    from modules.supplier.procurement_advisor import ProcurementAdvisor
    
    if score_button:
        st.markdown("---")
        st.subheader("📊 Supplier Scoring Results")
        
        with st.spinner("Calculating supplier score..."):
            scorer = SupplierScorer()
            result = scorer.score(supplier_data)
            
            # Overall metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Overall Score", f"{result['overall_score']}/100")
            
            with col2:
                risk_colors = {
                    'LOW': '🟢',
                    'MEDIUM': '🟡',
                    'HIGH': '🟠',
                    'CRITICAL': '🔴'
                }
                risk_icon = risk_colors.get(result['risk_level'], '⚪')
                st.metric("Risk Level", f"{risk_icon} {result['risk_level']}")
            
            with col3:
                category_icons = {
                    'PREFERRED': '⭐',
                    'APPROVED': '✅',
                    'CONDITIONAL': '⚠️',
                    'DISQUALIFIED': '🚫'
                }
                cat_icon = category_icons.get(result['category'], '⚪')
                st.metric("Category", f"{cat_icon} {result['category']}")
            
            with col4:
                st.metric("Supplier ID", result['supplier_id'])
            
            # Breakdown radar chart simulation
            st.markdown("---")
            st.subheader("📈 Performance Breakdown")
            
            breakdown_df = pd.DataFrame([
                {"Metric": "Quality", "Score": result['breakdown']['quality']},
                {"Metric": "Delivery", "Score": result['breakdown']['delivery']},
                {"Metric": "Defect Control", "Score": result['breakdown']['defects']},
                {"Metric": "Price", "Score": result['breakdown']['price']},
                {"Metric": "Responsiveness", "Score": result['breakdown']['responsiveness']},
            ])
            
            st.bar_chart(breakdown_df.set_index('Metric'))
            
            # Detailed metrics
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Detailed Scores")
                for metric, score in result['breakdown'].items():
                    st.progress(score / 100, text=f"{metric.title()}: {score:.1f}/100")
            
            with col2:
                st.markdown("#### Metrics Summary")
                for key, value in result['metrics_summary'].items():
                    st.caption(f"**{key.replace('_', ' ').title()}**: {value}%")
            
            # Recommendations
            st.markdown("---")
            st.subheader("💡 Recommendations")
            
            for rec in result['recommendations']:
                if "CRITICAL" in rec or "🚨" in rec:
                    st.error(rec)
                elif "⚠️" in rec or "WARNING" in rec:
                    st.warning(rec)
                elif "✅" in rec or "LOW RISK" in rec:
                    st.success(rec)
                else:
                    st.info(rec)
    
    if advise_button:
        st.markdown("---")
        st.subheader("💡 Procurement Advisory")
        
        with st.spinner("Generating procurement advice..."):
            advisor = ProcurementAdvisor()
            advice = advisor.advise(supplier_data)
            
            # Action summary
            action_colors = {
                'RECOMMEND': '🟢',
                'MONITOR': '🟡',
                'REVIEW': '🟠',
                'REJECT': '🔴'
            }
            action_icon = action_colors.get(advice['action'], '⚪')
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Action", f"{action_icon} {advice['action']}")
            
            with col2:
                confidence_pct = advice['confidence'] * 100
                st.metric("Confidence", f"{confidence_pct:.0f}%")
            
            with col3:
                volume_icons = {
                    'HIGH': '📈',
                    'MEDIUM': '📊',
                    'LOW': '📉',
                    'MINIMAL': '⬇️',
                    'NONE': '🚫'
                }
                volume_icon = volume_icons.get(advice['suggested_order_volume'], '📊')
                st.metric("Order Volume", f"{volume_icon} {advice['suggested_order_volume']}")
            
            # Reasoning
            st.markdown("---")
            st.markdown("#### 📋 Analysis")
            st.info(advice['reasoning'])
            
            # Strategy
            st.markdown("#### 📌 Procurement Strategy")
            st.markdown(advice['procurement_strategy'])
            
            # Risk factors and opportunities
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### ⚠️ Risk Factors")
                for risk in advice['risk_factors']:
                    st.warning(f"• {risk}")
            
            with col2:
                st.markdown("#### 🎯 Opportunities")
                for opp in advice['opportunities']:
                    st.success(f"• {opp}")
    
    # If neither button clicked, show example
    if not score_button and not advise_button:
        st.info("👆 Enter supplier metrics above and click 'Score Supplier' or 'Get Procurement Advice' to analyze.")
        
        # Show example
        st.markdown("---")
        st.subheader("📊 Example Analysis")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Example Score", "85/100")
        with col2:
            st.metric("Example Risk", "🟢 LOW")
        with col3:
            st.metric("Example Category", "✅ APPROVED")

except ImportError as e:
    st.error(f"❌ Required module not available: {str(e)}")
    st.info("💡 Please ensure supplier modules are properly installed.")

except Exception as e:
    st.error(f"❌ Error: {str(e)}")
    st.info("💡 Using demo mode.")

# Batch supplier comparison
st.markdown("---")
st.subheader("📊 Supplier Comparison Tool")

st.markdown("""
**Coming Soon**: Compare multiple suppliers side-by-side to identify the best procurement options.

Features:
- Multi-supplier scoring
- Side-by-side comparison
- Ranking and recommendations
- Anomaly detection
""")

st.markdown("---")
st.caption("Supplier Scoring Module | AI-ERP Quality System")
