"""
Reports Dashboard Page

Streamlit page for KPI dashboard with real-time metrics,
gauge visualizations, and alert management.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.reporting.kpi_engine import KPIEngine
from modules.reporting.alert_system import AlertSystem

st.set_page_config(page_title="Reports & KPIs", page_icon="📊", layout="wide")

st.title("📊 KPI Dashboard & Alerts")
st.markdown("### Real-Time Manufacturing Intelligence")
st.markdown("---")

# Initialize engines
@st.cache_resource
def get_kpi_engine():
    return KPIEngine()

@st.cache_resource
def get_alert_system():
    return AlertSystem()

kpi_engine = get_kpi_engine()
alert_system = get_alert_system()

# Auto-refresh option
auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (every 30s)", value=False)
if auto_refresh:
    import time
    time.sleep(30)
    st.rerun()

# Get KPI snapshot
kpi_snapshot = kpi_engine.get_snapshot()

# Display summary
st.subheader("📈 Overall Performance")
summary = kpi_snapshot['summary']

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Overall Status", summary['overall_status'])

with col2:
    st.metric("Targets Met", f"{summary['targets_met']}/{summary['total_kpis']}")

with col3:
    st.metric("Performance", f"{summary['performance_percentage']:.1f}%")

with col4:
    status_color = {
        'EXCELLENT': '🟢',
        'GOOD': '🟡',
        'FAIR': '🟠',
        'POOR': '🔴'
    }
    st.markdown(f"### {status_color.get(summary['overall_status'], '⚪')}")

st.info(summary['message'])

st.markdown("---")

# KPI Gauges
st.subheader("🎯 Key Performance Indicators")

kpis = kpi_snapshot['kpis']

# Create gauge charts for each KPI
col1, col2 = st.columns(2)

with col1:
    # OEE Gauge
    oee = kpis['oee']
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=oee['value'],
        delta={'reference': oee['target'], 'increasing': {'color': "green"}},
        title={'text': f"{oee['name']}<br><span style='font-size:0.8em;color:gray'>{oee['description']}</span>"},
        gauge={
            'axis': {'range': [None, 100], 'ticksuffix': '%'},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 70], 'color': "lightcoral"},
                {'range': [70, 85], 'color': "lightyellow"},
                {'range': [85, 100], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': oee['target']
            }
        }
    ))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    status_emoji = {'GOOD': '✅', 'WARNING': '⚠️', 'CRITICAL': '🚨'}
    st.markdown(f"**Status:** {status_emoji.get(oee['status'], '❓')} {oee['status']} | **Trend:** {oee['trend']}")
    
    # FPY Gauge
    fpy = kpis['fpy']
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=fpy['value'],
        delta={'reference': fpy['target'], 'increasing': {'color': "green"}},
        title={'text': f"{fpy['name']}<br><span style='font-size:0.8em;color:gray'>{fpy['description']}</span>"},
        gauge={
            'axis': {'range': [None, 100], 'ticksuffix': '%'},
            'bar': {'color': "darkgreen"},
            'steps': [
                {'range': [0, 85], 'color': "lightcoral"},
                {'range': [85, 95], 'color': "lightyellow"},
                {'range': [95, 100], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': fpy['target']
            }
        }
    ))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f"**Status:** {status_emoji.get(fpy['status'], '❓')} {fpy['status']} | **Trend:** {fpy['trend']}")

with col2:
    # DPMO Gauge
    dpmo = kpis['dpmo']
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=dpmo['value'],
        delta={'reference': dpmo['target'], 'decreasing': {'color': "green"}},
        title={'text': f"{dpmo['name']}<br><span style='font-size:0.8em;color:gray'>{dpmo['description']}</span>"},
        gauge={
            'axis': {'range': [0, 60000]},
            'bar': {'color': "darkorange"},
            'steps': [
                {'range': [0, 35000], 'color': "lightgreen"},
                {'range': [35000, 50000], 'color': "lightyellow"},
                {'range': [50000, 60000], 'color': "lightcoral"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': dpmo['target']
            }
        }
    ))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f"**Status:** {status_emoji.get(dpmo['status'], '❓')} {dpmo['status']} | **Trend:** {dpmo['trend']}")
    
    # Cpk Gauge
    cpk = kpis['cpk']
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=cpk['value'],
        delta={'reference': cpk['target'], 'increasing': {'color': "green"}},
        title={'text': f"{cpk['name']}<br><span style='font-size:0.8em;color:gray'>{cpk['description']}</span>"},
        gauge={
            'axis': {'range': [0, 2.5]},
            'bar': {'color': "darkpurple"},
            'steps': [
                {'range': [0, 1.0], 'color': "lightcoral"},
                {'range': [1.0, 1.33], 'color': "lightyellow"},
                {'range': [1.33, 2.5], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': cpk['target']
            }
        }
    ))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f"**Status:** {status_emoji.get(cpk['status'], '❓')} {cpk['status']} | **Trend:** {cpk['trend']}")

st.markdown("---")

# KPI Details Table
st.subheader("📋 Detailed KPI Metrics")

kpi_details = []
for kpi_key, kpi_data in kpis.items():
    kpi_details.append({
        'KPI': kpi_data['name'],
        'Description': kpi_data['description'],
        'Current': f"{kpi_data['value']}{kpi_data['unit']}",
        'Target': f"{kpi_data['target']}{kpi_data['unit']}",
        'Status': f"{status_emoji.get(kpi_data['status'], '❓')} {kpi_data['status']}",
        'Trend': kpi_data['trend'],
        'Performance': f"{kpi_data['performance_ratio']:.1%}"
    })

kpi_df = pd.DataFrame(kpi_details)
st.dataframe(kpi_df, use_container_width=True, hide_index=True)

st.markdown("---")

# Alerts Section
st.header("🔔 Alert Management")

# Get active alerts
active_alerts = alert_system.get_active_alerts()

# Alert statistics
col1, col2, col3, col4 = st.columns(4)

critical_count = len([a for a in active_alerts if a['severity'] == 'CRITICAL'])
warning_count = len([a for a in active_alerts if a['severity'] == 'WARNING'])
info_count = len([a for a in active_alerts if a['severity'] == 'INFO'])

with col1:
    st.metric("🔴 Critical", critical_count)

with col2:
    st.metric("🟡 Warning", warning_count)

with col3:
    st.metric("🔵 Info", info_count)

with col4:
    st.metric("📊 Total Active", len(active_alerts))

st.markdown("---")

# Display alerts
if active_alerts:
    st.subheader("📋 Active Alerts")
    
    for alert in active_alerts:
        severity_color = {
            'CRITICAL': '🔴',
            'WARNING': '🟡',
            'INFO': '🔵'
        }
        
        severity_icon = severity_color.get(alert['severity'], '⚪')
        
        with st.expander(f"{severity_icon} [{alert['severity']}] {alert['title']}", expanded=alert['severity'] == 'CRITICAL'):
            st.markdown(f"**Message:** {alert['message']}")
            st.markdown(f"**Source:** {alert['source']}")
            st.markdown(f"**Time:** {alert['timestamp']}")
            
            if st.button(f"✅ Dismiss Alert #{alert['id']}", key=f"dismiss_{alert['id']}"):
                try:
                    alert_system.dismiss_alert(alert['id'])
                    st.success(f"Alert #{alert['id']} dismissed!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error dismissing alert: {e}")
else:
    st.success("✅ No active alerts. All systems operational!")

# Alert creation
st.markdown("---")
st.subheader("➕ Create New Alert")

with st.form("new_alert_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        alert_title = st.text_input("Alert Title")
        alert_severity = st.selectbox("Severity", ["INFO", "WARNING", "CRITICAL"])
    
    with col2:
        alert_message = st.text_area("Alert Message")
        alert_source = st.selectbox("Source", ["quality", "maintenance", "supplier", "vision", "dashboard", "system"])
    
    if st.form_submit_button("Create Alert"):
        if alert_title and alert_message:
            try:
                new_alert = alert_system.create_alert(
                    title=alert_title,
                    message=alert_message,
                    severity=alert_severity,
                    source=alert_source
                )
                st.success(f"✅ Alert #{new_alert['id']} created successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating alert: {e}")
        else:
            st.warning("Please fill in all fields")

st.markdown("---")
st.caption(f"Last updated: {kpi_snapshot['timestamp']} | KPI Dashboard Module")
