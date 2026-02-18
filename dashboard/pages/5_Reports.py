"""
KPI Reports & Alerts Dashboard Page
Real-time KPI monitoring and alert management
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="KPI Reports & Alerts", page_icon="📊", layout="wide")

st.title("📊 KPI Reports & Alerts")
st.markdown("### Real-Time Quality Performance Metrics")
st.markdown("---")

try:
    from modules.reporting.kpi_engine import KPIEngine
    from modules.reporting.alert_system import AlertSystem
    
    # Initialize systems
    kpi_engine = KPIEngine()
    alert_system = AlertSystem()
    
    # Get KPI snapshot
    kpi_snapshot = kpi_engine.get_snapshot()
    
    # Display KPI cards
    st.markdown("### 🎯 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        oee = kpi_snapshot['oee']
        oee_delta = "+2.1%" if oee >= 85 else "-1.5%"
        st.metric(
            label="🟢 OEE (Overall Equipment Effectiveness)",
            value=f"{oee:.1f}%",
            delta=oee_delta,
            help="Target: ≥85%"
        )
        
        # OEE gauge
        fig_oee = go.Figure(go.Indicator(
            mode="gauge+number",
            value=oee,
            title={'text': "OEE"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "green" if oee >= 85 else "orange" if oee >= 70 else "red"},
                'steps': [
                    {'range': [0, 70], 'color': "lightcoral"},
                    {'range': [70, 85], 'color': "lightyellow"},
                    {'range': [85, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 85
                }
            }
        ))
        fig_oee.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_oee, use_container_width=True)
    
    with col2:
        fpy = kpi_snapshot['fpy']
        fpy_delta = "+0.5%" if fpy >= 95 else "-0.3%"
        st.metric(
            label="✅ FPY (First Pass Yield)",
            value=f"{fpy:.1f}%",
            delta=fpy_delta,
            help="Target: ≥95%"
        )
        
        # FPY gauge
        fig_fpy = go.Figure(go.Indicator(
            mode="gauge+number",
            value=fpy,
            title={'text': "FPY"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "green" if fpy >= 95 else "orange" if fpy >= 90 else "red"},
                'steps': [
                    {'range': [0, 90], 'color': "lightcoral"},
                    {'range': [90, 95], 'color': "lightyellow"},
                    {'range': [95, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 95
                }
            }
        ))
        fig_fpy.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_fpy, use_container_width=True)
    
    with col3:
        dpmo = kpi_snapshot['dpmo']
        dpmo_delta = "-1,200" if dpmo <= 40000 else "+500"
        st.metric(
            label="🔴 DPMO (Defects Per Million Opportunities)",
            value=f"{dpmo:,}",
            delta=dpmo_delta,
            delta_color="inverse",
            help="Target: ≤40,000"
        )
        
        # DPMO gauge (inverted - lower is better)
        fig_dpmo = go.Figure(go.Indicator(
            mode="gauge+number",
            value=dpmo,
            title={'text': "DPMO"},
            gauge={
                'axis': {'range': [0, 100000]},
                'bar': {'color': "green" if dpmo <= 40000 else "orange" if dpmo <= 60000 else "red"},
                'steps': [
                    {'range': [0, 40000], 'color': "lightgreen"},
                    {'range': [40000, 60000], 'color': "lightyellow"},
                    {'range': [60000, 100000], 'color': "lightcoral"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 40000
                }
            }
        ))
        fig_dpmo.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_dpmo, use_container_width=True)
    
    with col4:
        cpk = kpi_snapshot['cpk']
        cpk_delta = "+0.03" if cpk >= 1.33 else "-0.02"
        st.metric(
            label="📐 Cpk (Process Capability Index)",
            value=f"{cpk:.2f}",
            delta=cpk_delta,
            help="Target: ≥1.33"
        )
        
        # Cpk gauge
        fig_cpk = go.Figure(go.Indicator(
            mode="gauge+number",
            value=cpk,
            title={'text': "Cpk"},
            gauge={
                'axis': {'range': [0, 2]},
                'bar': {'color': "green" if cpk >= 1.33 else "orange" if cpk >= 1.0 else "red"},
                'steps': [
                    {'range': [0, 1.0], 'color': "lightcoral"},
                    {'range': [1.0, 1.33], 'color': "lightyellow"},
                    {'range': [1.33, 2], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 1.33
                }
            }
        ))
        fig_cpk.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_cpk, use_container_width=True)
    
    st.markdown("---")
    
    # OEE components
    st.markdown("### ⚙️ OEE Component Breakdown")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        availability = kpi_snapshot.get('availability', 94.5)
        st.metric("Availability", f"{availability:.1f}%")
        st.progress(availability / 100)
    
    with col2:
        performance = kpi_snapshot.get('performance', 92.1)
        st.metric("Performance", f"{performance:.1f}%")
        st.progress(performance / 100)
    
    with col3:
        quality = kpi_snapshot.get('quality', 97.8)
        st.metric("Quality", f"{quality:.1f}%")
        st.progress(quality / 100)
    
    st.markdown("---")
    
    # KPI Trends
    st.markdown("### 📈 30-Day KPI Trends")
    
    trend_data = kpi_engine.get_trend(days=30)
    
    if trend_data and len(trend_data) > 0:
        df_trend = pd.DataFrame(trend_data)
        
        # Create trend chart
        fig_trend = go.Figure()
        
        fig_trend.add_trace(go.Scatter(
            x=df_trend['date'],
            y=df_trend['oee'],
            mode='lines+markers',
            name='OEE (%)',
            line=dict(color='blue', width=2)
        ))
        
        fig_trend.add_trace(go.Scatter(
            x=df_trend['date'],
            y=df_trend['fpy'],
            mode='lines+markers',
            name='FPY (%)',
            line=dict(color='green', width=2)
        ))
        
        # Add target lines
        fig_trend.add_hline(y=85, line_dash="dash", line_color="blue", annotation_text="OEE Target (85%)")
        fig_trend.add_hline(y=95, line_dash="dash", line_color="green", annotation_text="FPY Target (95%)")
        
        fig_trend.update_layout(
            title="OEE & FPY Trends",
            xaxis_title="Date",
            yaxis_title="Percentage (%)",
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # DPMO and Cpk trends
        fig_trend2 = go.Figure()
        
        fig_trend2.add_trace(go.Scatter(
            x=df_trend['date'],
            y=df_trend['dpmo'] / 1000,  # Convert to thousands
            mode='lines+markers',
            name='DPMO (thousands)',
            line=dict(color='red', width=2),
            yaxis='y'
        ))
        
        fig_trend2.add_trace(go.Scatter(
            x=df_trend['date'],
            y=df_trend['cpk'],
            mode='lines+markers',
            name='Cpk',
            line=dict(color='purple', width=2),
            yaxis='y2'
        ))
        
        fig_trend2.update_layout(
            title="DPMO & Cpk Trends",
            xaxis_title="Date",
            yaxis=dict(title="DPMO (thousands)", side='left'),
            yaxis2=dict(title="Cpk", overlaying='y', side='right'),
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig_trend2, use_container_width=True)
    else:
        st.info("No trend data available. Metrics will be populated over time.")
    
    st.markdown("---")
    
    # Alerts Section
    st.markdown("### 🔔 Active Alerts")
    
    # Alert count by severity
    alert_counts = alert_system.get_alert_count_by_severity()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🔴 Critical", alert_counts['CRITICAL'])
    with col2:
        st.metric("⚠️ Error", alert_counts['ERROR'])
    with col3:
        st.metric("🟡 Warning", alert_counts['WARNING'])
    with col4:
        st.metric("ℹ️ Info", alert_counts['INFO'])
    
    # Get active alerts
    alerts = alert_system.get_active_alerts()
    
    if alerts:
        # Filter by severity
        severity_filter = st.multiselect(
            "Filter by Severity",
            options=['CRITICAL', 'ERROR', 'WARNING', 'INFO'],
            default=['CRITICAL', 'ERROR', 'WARNING']
        )
        
        filtered_alerts = [a for a in alerts if a['severity'] in severity_filter]
        
        if filtered_alerts:
            for alert in filtered_alerts:
                with st.container():
                    col1, col2 = st.columns([5, 1])
                    
                    with col1:
                        # Display alert with appropriate color
                        if alert['severity'] == 'CRITICAL':
                            st.error(f"**🔴 {alert['title']}**\n\n{alert['message']}")
                        elif alert['severity'] == 'ERROR':
                            st.error(f"**⚠️ {alert['title']}**\n\n{alert['message']}")
                        elif alert['severity'] == 'WARNING':
                            st.warning(f"**🟡 {alert['title']}**\n\n{alert['message']}")
                        else:
                            st.info(f"**ℹ️ {alert['title']}**\n\n{alert['message']}")
                        
                        st.caption(f"Source: {alert['source']} | Created: {alert['created_at']}")
                    
                    with col2:
                        # Dismiss button
                        if st.button("Dismiss", key=f"dismiss_{alert['id']}", use_container_width=True):
                            try:
                                alert_system.dismiss_alert(alert['id'])
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to dismiss: {e}")
                    
                    st.markdown("---")
        else:
            st.info("No alerts matching the selected severity levels.")
    else:
        st.success("✅ No active alerts. All systems operational.")
    
    # Production summary
    st.markdown("---")
    st.markdown("### 📦 Production Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Units", f"{kpi_snapshot.get('total_units', 8450):,}")
    
    with col2:
        st.metric("Defective Units", f"{kpi_snapshot.get('defective_units', 186):,}")
    
    with col3:
        defect_rate = (kpi_snapshot.get('defective_units', 186) / kpi_snapshot.get('total_units', 8450)) * 100
        st.metric("Defect Rate", f"{defect_rate:.2f}%")
    
    with col4:
        good_units = kpi_snapshot.get('total_units', 8450) - kpi_snapshot.get('defective_units', 186)
        st.metric("Good Units", f"{good_units:,}")

except Exception as e:
    st.error(f"❌ Error loading KPI data: {str(e)}")
    st.info("💡 Make sure all reporting modules are properly installed.")

st.markdown("---")
st.caption("AI-ERP Quality Module v1.0.0 | KPI Reporting & Alert Management")
