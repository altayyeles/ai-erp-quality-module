"""
Maintenance Dashboard Page

Streamlit page for predictive maintenance monitoring with
8-machine status tracking, RUL predictions, and sensor readings.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from modules.maintenance.sensor_monitor import SensorMonitor

st.set_page_config(page_title="Maintenance", page_icon="🔧", layout="wide")

st.title("🔧 Predictive Maintenance")
st.markdown("### Real-Time Machine Monitoring & RUL Prediction")
st.markdown("---")

# Initialize monitor
@st.cache_resource
def get_monitor():
    return SensorMonitor()

monitor = get_monitor()

# Get all machines
machines = monitor.get_all_machines()

# Summary metrics
col1, col2, col3, col4 = st.columns(4)

status_counts = {}
for machine in machines:
    status = machine.get('status', 'UNKNOWN')
    status_counts[status] = status_counts.get(status, 0) + 1

with col1:
    st.metric("🟢 Running", status_counts.get('RUNNING', 0))

with col2:
    st.metric("🟡 Warning", status_counts.get('WARNING', 0))

with col3:
    st.metric("🔴 Critical", status_counts.get('CRITICAL', 0))

with col4:
    st.metric("⚫ Offline", status_counts.get('OFFLINE', 0))

st.markdown("---")

# Machine status table
st.subheader("🏭 Machine Status Overview")

# Prepare data for table
table_data = []
for machine in machines:
    status_icon = {
        'RUNNING': '🟢',
        'WARNING': '🟡',
        'CRITICAL': '🔴',
        'OFFLINE': '⚫'
    }
    
    urgency_icon = {
        'NORMAL': '✅',
        'WARNING': '⚠️',
        'CRITICAL': '🚨'
    }
    
    table_data.append({
        'Machine': machine['machine_id'],
        'Status': f"{status_icon.get(machine['status'], '⚪')} {machine['status']}",
        'RUL (hours)': f"{machine.get('rul_hours', 0):.1f}",
        'Urgency': f"{urgency_icon.get(machine.get('maintenance_urgency', 'NORMAL'), '❓')} {machine.get('maintenance_urgency', 'N/A')}",
        'Last Maintenance': machine.get('last_maintenance', 'N/A'),
        'Next Maintenance': machine.get('next_maintenance', 'N/A')
    })

df = pd.DataFrame(table_data)
st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown("---")

# Detailed machine view
st.subheader("🔍 Detailed Machine View")

# Machine selector
selected_machine = st.selectbox(
    "Select Machine",
    [m['machine_id'] for m in machines]
)

# Get selected machine data
selected_data = next((m for m in machines if m['machine_id'] == selected_machine), None)

if selected_data:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status = selected_data['status']
        status_color = {
            'RUNNING': 'green',
            'WARNING': 'orange',
            'CRITICAL': 'red',
            'OFFLINE': 'gray'
        }
        st.markdown(f"**Status:** :{status_color.get(status, 'blue')}[{status}]")
        st.markdown(f"**RUL:** {selected_data.get('rul_hours', 0):.2f} hours")
    
    with col2:
        st.markdown(f"**Urgency:** {selected_data.get('maintenance_urgency', 'N/A')}")
        st.markdown(f"**Last Maintenance:** {selected_data.get('last_maintenance', 'N/A')}")
    
    with col3:
        st.markdown(f"**Next Maintenance:** {selected_data.get('next_maintenance', 'N/A')}")
    
    # Sensor readings
    st.markdown("#### 📊 Sensor Readings")
    
    sensor_data = selected_data.get('sensor_readings', {})
    
    if sensor_data:
        # Create gauge charts for key sensors
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=sensor_data.get('air_temperature', 0),
                title={'text': "Air Temp (K)"},
                gauge={'axis': {'range': [290, 310]},
                       'bar': {'color': "darkblue"},
                       'steps': [
                           {'range': [290, 295], 'color': "lightgray"},
                           {'range': [295, 305], 'color': "lightgreen"},
                           {'range': [305, 310], 'color': "lightyellow"}
                       ]}
            ))
            fig.update_layout(height=200, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=sensor_data.get('tool_wear', 0),
                title={'text': "Tool Wear (min)"},
                gauge={'axis': {'range': [0, 250]},
                       'bar': {'color': "darkorange"},
                       'steps': [
                           {'range': [0, 150], 'color': "lightgreen"},
                           {'range': [150, 200], 'color': "lightyellow"},
                           {'range': [200, 250], 'color': "lightcoral"}
                       ]}
            ))
            fig.update_layout(height=200, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=sensor_data.get('vibration', 0),
                title={'text': "Vibration (mm/s)"},
                gauge={'axis': {'range': [0, 1.5]},
                       'bar': {'color': "darkred"},
                       'steps': [
                           {'range': [0, 0.6], 'color': "lightgreen"},
                           {'range': [0.6, 1.0], 'color': "lightyellow"},
                           {'range': [1.0, 1.5], 'color': "lightcoral"}
                       ]}
            ))
            fig.update_layout(height=200, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig, use_container_width=True)
        
        with col4:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=sensor_data.get('rotational_speed', 0),
                title={'text': "Speed (rpm)"},
                gauge={'axis': {'range': [1000, 2000]},
                       'bar': {'color': "darkgreen"},
                       'steps': [
                           {'range': [1000, 1300], 'color': "lightcoral"},
                           {'range': [1300, 1700], 'color': "lightgreen"},
                           {'range': [1700, 2000], 'color': "lightyellow"}
                       ]}
            ))
            fig.update_layout(height=200, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig, use_container_width=True)
        
        # Full sensor table
        st.markdown("#### 📋 All Sensor Values")
        sensor_df = pd.DataFrame([sensor_data]).T
        sensor_df.columns = ["Value"]
        st.dataframe(sensor_df, use_container_width=True)

# Maintenance schedule
st.markdown("---")
st.subheader("📅 Maintenance Schedule (Sorted by Urgency)")

schedule = monitor.get_maintenance_schedule()
schedule_df = pd.DataFrame(schedule)

# Add urgency icons
urgency_icon_map = {'CRITICAL': '🚨', 'WARNING': '⚠️', 'NORMAL': '✅'}
schedule_df['urgency'] = schedule_df['urgency'].apply(
    lambda x: f"{urgency_icon_map.get(x, '❓')} {x}"
)

st.dataframe(schedule_df, use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("Predictive Maintenance Module | Powered by Random Forest RUL Model")
