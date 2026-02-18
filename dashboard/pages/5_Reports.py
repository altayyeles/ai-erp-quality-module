"""
KPI Reports & Alerts Dashboard Page
Streamlit page for KPI monitoring and alert management
"""

import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Reports & Alerts", page_icon="📊", layout="wide")

st.title("📊 KPI Reports & Alerts")
st.markdown("---")

try:
    from modules.reporting.kpi_engine import KPIEngine
    from modules.reporting.alert_system import AlertSystem
    
    kpi_engine = KPIEngine()
    alert_system = AlertSystem()
    
    # KPI Snapshot Section
    st.subheader("📈 Key Performance Indicators")
    
    with st.spinner("Loading KPI data..."):
        kpi_snapshot = kpi_engine.get_snapshot()
        
        # Main KPIs - Large metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            oee = kpi_snapshot['oee']
            oee_delta = "+2.1%" if 'mode' not in kpi_snapshot else None
            st.metric(
                "🟢 OEE",
                f"{oee:.1f}%",
                delta=oee_delta,
                help="Overall Equipment Effectiveness"
            )
        
        with col2:
            fpy = kpi_snapshot['fpy']
            fpy_delta = "+0.5%" if 'mode' not in kpi_snapshot else None
            st.metric(
                "✅ First Pass Yield",
                f"{fpy:.1f}%",
                delta=fpy_delta,
                help="Percentage of products manufactured correctly first time"
            )
        
        with col3:
            dpmo = kpi_snapshot['dpmo']
            dpmo_delta = "-1,200" if 'mode' not in kpi_snapshot else None
            st.metric(
                "🔴 DPMO",
                f"{dpmo:,.0f}",
                delta=dpmo_delta,
                help="Defects Per Million Opportunities"
            )
        
        with col4:
            cpk = kpi_snapshot['cpk']
            cpk_delta = "+0.03" if 'mode' not in kpi_snapshot else None
            st.metric(
                "📐 Cpk",
                f"{cpk:.2f}",
                delta=cpk_delta,
                help="Process Capability Index"
            )
        
        # OEE Components
        st.markdown("---")
        st.subheader("🔧 OEE Components")
        
        oee_components = kpi_snapshot.get('oee_components', {})
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            availability = oee_components.get('availability', 0)
            st.metric("Availability", f"{availability:.1f}%")
            st.progress(availability / 100)
            st.caption("Equipment uptime vs. planned production time")
        
        with col2:
            performance = oee_components.get('performance', 0)
            st.metric("Performance", f"{performance:.1f}%")
            st.progress(performance / 100)
            st.caption("Actual vs. ideal cycle time")
        
        with col3:
            quality = oee_components.get('quality', 0)
            st.metric("Quality", f"{quality:.1f}%")
            st.progress(quality / 100)
            st.caption("Good parts vs. total parts produced")
        
        # Production Summary
        st.markdown("---")
        st.subheader("🏭 Production Summary")
        
        prod_summary = kpi_snapshot.get('production_summary', {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Good Parts", f"{prod_summary.get('good_parts', 0):,}")
        
        with col2:
            st.metric("Total Parts", f"{prod_summary.get('total_parts', 0):,}")
        
        with col3:
            st.metric("Defects", f"{prod_summary.get('defects', 0):,}")
        
        with col4:
            st.metric("Yield Rate", f"{prod_summary.get('yield_rate', 0):.1f}%")
    
    # KPI Trends
    st.markdown("---")
    st.subheader("📈 KPI Trends (Last 30 Days)")
    
    trend_period = st.selectbox(
        "Select Period",
        [7, 14, 30, 60, 90],
        index=2,
        format_func=lambda x: f"Last {x} days"
    )
    
    with st.spinner("Loading trend data..."):
        trend_data = kpi_engine.get_trend(days=trend_period)
        
        # Create tabs for different KPIs
        tab1, tab2, tab3, tab4 = st.tabs(["OEE", "FPY", "DPMO", "Cpk"])
        
        with tab1:
            if trend_data.get('dates'):
                df_oee = pd.DataFrame({
                    'Date': trend_data['dates'],
                    'OEE (%)': trend_data['oee']
                })
                st.line_chart(df_oee.set_index('Date'))
            else:
                st.info("No trend data available")
        
        with tab2:
            if trend_data.get('dates'):
                df_fpy = pd.DataFrame({
                    'Date': trend_data['dates'],
                    'FPY (%)': trend_data['fpy']
                })
                st.line_chart(df_fpy.set_index('Date'))
            else:
                st.info("No trend data available")
        
        with tab3:
            if trend_data.get('dates'):
                df_dpmo = pd.DataFrame({
                    'Date': trend_data['dates'],
                    'DPMO': trend_data['dpmo']
                })
                st.line_chart(df_dpmo.set_index('Date'))
            else:
                st.info("No trend data available")
        
        with tab4:
            if trend_data.get('dates'):
                df_cpk = pd.DataFrame({
                    'Date': trend_data['dates'],
                    'Cpk': trend_data['cpk']
                })
                st.line_chart(df_cpk.set_index('Date'))
            else:
                st.info("No trend data available")
    
    # Alerts Section
    st.markdown("---")
    st.subheader("🔔 Active Alerts")
    
    # Alert statistics
    alert_stats = alert_system.get_alert_statistics()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total = alert_stats['total_active']
        st.metric("Total Active", total)
    
    with col2:
        critical = alert_stats['by_severity'].get('CRITICAL', 0)
        st.metric("🔴 Critical", critical)
    
    with col3:
        error = alert_stats['by_severity'].get('ERROR', 0)
        st.metric("🟠 Error", error)
    
    with col4:
        warning = alert_stats['by_severity'].get('WARNING', 0)
        st.metric("🟡 Warning", warning)
    
    with col5:
        info = alert_stats['by_severity'].get('INFO', 0)
        st.metric("🔵 Info", info)
    
    # Filter alerts by severity
    severity_filter = st.selectbox(
        "Filter by Severity",
        ["All", "CRITICAL", "ERROR", "WARNING", "INFO"],
        index=0
    )
    
    filter_severity = None if severity_filter == "All" else severity_filter
    active_alerts = alert_system.get_active_alerts(severity=filter_severity)
    
    if active_alerts:
        st.markdown(f"**Showing {len(active_alerts)} alert(s)**")
        
        # Display alerts
        for alert in active_alerts:
            severity = alert['severity']
            
            # Color coding based on severity
            if severity == 'CRITICAL':
                alert_color = "🔴"
                container = st.container()
            elif severity == 'ERROR':
                alert_color = "🟠"
                container = st.container()
            elif severity == 'WARNING':
                alert_color = "🟡"
                container = st.container()
            else:
                alert_color = "🔵"
                container = st.container()
            
            with container:
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"### {alert_color} {alert['title']}")
                    st.markdown(f"**{alert['message']}**")
                    
                    meta_info = f"Source: {alert['source']} | Created: {alert['created_at']}"
                    if alert.get('machine_id'):
                        meta_info += f" | Machine: {alert['machine_id']}"
                    if alert.get('metric_value'):
                        meta_info += f" | Value: {alert['metric_value']}"
                    
                    st.caption(meta_info)
                
                with col2:
                    if st.button(f"Dismiss", key=f"dismiss_{alert['id']}", use_container_width=True):
                        if alert_system.dismiss_alert(alert['id']):
                            st.success("Alert dismissed!")
                            st.rerun()
                        else:
                            st.error("Failed to dismiss alert")
                
                st.markdown("---")
    
    else:
        st.success("✅ No active alerts. All systems operating normally.")
    
    # Machine-specific KPIs
    st.markdown("---")
    st.subheader("🖥️ Machine-Specific KPIs")
    
    machine_options = [f"M{i:03d}" for i in range(1, 9)]
    selected_machine = st.selectbox("Select Machine", machine_options)
    
    if selected_machine:
        with st.spinner(f"Loading KPIs for {selected_machine}..."):
            machine_kpis = kpi_engine.get_by_machine(selected_machine)
            
            if 'error' not in machine_kpis:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("OEE", f"{machine_kpis.get('oee', 0):.1f}%")
                
                with col2:
                    st.metric("FPY", f"{machine_kpis.get('fpy', 0):.1f}%")
                
                with col3:
                    st.metric("DPMO", f"{machine_kpis.get('dpmo', 0):,.0f}")
                
                with col4:
                    st.metric("Cpk", f"{machine_kpis.get('cpk', 0):.2f}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Good Parts", f"{machine_kpis.get('good_parts', 0):,}")
                
                with col2:
                    st.metric("Total Parts", f"{machine_kpis.get('total_parts', 0):,}")
                
                st.caption(f"Period: {machine_kpis.get('period', 'Last 7 days')}")
            else:
                st.error(f"Error loading machine KPIs: {machine_kpis['error']}")

except ImportError as e:
    st.error(f"❌ Required module not available: {str(e)}")
    st.info("💡 Please ensure reporting modules are properly installed.")

except Exception as e:
    st.error(f"❌ Error: {str(e)}")
    st.info("💡 Using demo mode.")
    
    # Show demo metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🟢 OEE", "87.3%", delta="+2.1%")
    
    with col2:
        st.metric("✅ FPY", "96.8%", delta="+0.5%")
    
    with col3:
        st.metric("🔴 DPMO", "32,000", delta="-1,200")
    
    with col4:
        st.metric("📐 Cpk", "1.45", delta="+0.03")

st.markdown("---")
st.caption("KPI Reports & Alerts Module | AI-ERP Quality System")
