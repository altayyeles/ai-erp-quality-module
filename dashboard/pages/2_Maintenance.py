"""
Predictive Maintenance Dashboard Page
Random Forest RUL prediction with 8-machine real-time monitoring
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="Predictive Maintenance", page_icon="🔧", layout="wide")

st.title("🔧 Predictive Maintenance")
st.markdown("### Real-Time Machine Monitoring & RUL Prediction")
st.markdown("---")

try:
    from modules.maintenance.sensor_monitor import SensorMonitor
    from modules.maintenance.rul_model import RULModel
    
    # Initialize
    monitor = SensorMonitor()
    rul_model = RULModel()
    
    # Get all machines
    machines = monitor.get_all_machines()
    
    # Display machine overview
    st.markdown("### 🏭 Machine Status Overview")
    
    # Create columns for machine cards (4 per row)
    for row in range(2):  # 2 rows for 8 machines
        cols = st.columns(4)
        for col_idx in range(4):
            machine_idx = row * 4 + col_idx
            if machine_idx < len(machines):
                machine = machines[machine_idx]
                
                with cols[col_idx]:
                    # Status color
                    status_color = {
                        "RUNNING": "🟢",
                        "WARNING": "🟡",
                        "CRITICAL": "🔴",
                        "OFFLINE": "⚫"
                    }
                    
                    # Machine card
                    st.markdown(f"#### {status_color.get(machine['status'], '⚪')} {machine['machine_id']}")
                    st.markdown(f"**Status:** {machine['status']}")
                    st.markdown(f"**RUL:** {machine['rul_hours']:.1f}h ({machine['rul_hours']/24:.1f} days)")
                    
                    # RUL progress bar
                    rul_percentage = min(100, (machine['rul_hours'] / 720) * 100)  # 720h = 30 days max
                    if machine['rul_hours'] < 72:  # < 3 days
                        bar_color = "red"
                    elif machine['rul_hours'] < 168:  # < 7 days
                        bar_color = "orange"
                    else:
                        bar_color = "green"
                    
                    st.progress(rul_percentage / 100)
                    
                    # Next maintenance
                    next_maint = datetime.fromisoformat(machine['next_maintenance'])
                    days_until = (next_maint - datetime.now()).days
                    st.caption(f"Maintenance in {days_until} days")
    
    st.markdown("---")
    
    # Detailed machine selection
    st.markdown("### 🔍 Detailed Machine Analysis")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Machine selector
        machine_ids = [m['machine_id'] for m in machines]
        selected_machine_id = st.selectbox("Select Machine", machine_ids)
        
        # Get selected machine data
        selected_machine = next((m for m in machines if m['machine_id'] == selected_machine_id), None)
        
        if selected_machine:
            st.markdown("#### Current Sensor Readings")
            
            sensors = selected_machine['sensor_readings']
            
            # Display sensor values
            st.metric("Air Temperature", f"{sensors['air_temperature']:.2f} K")
            st.metric("Process Temperature", f"{sensors['process_temperature']:.2f} K")
            st.metric("Rotational Speed", f"{sensors['rotational_speed']:.1f} RPM")
            st.metric("Torque", f"{sensors['torque']:.2f} Nm")
            st.metric("Tool Wear", f"{sensors['tool_wear']:.1f} min")
            st.metric("Vibration", f"{sensors['vibration']:.3f} mm/s")
            st.metric("Humidity", f"{sensors['humidity']:.1f} %")
            st.metric("Pressure", f"{sensors['pressure']:.3f} bar")
            
            # RUL Prediction button
            if st.button("🔮 Predict RUL", use_container_width=True):
                with st.spinner("Calculating RUL..."):
                    rul_result = rul_model.predict(sensors)
                    
                    st.markdown("#### 📊 RUL Prediction Results")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("RUL Hours", f"{rul_result['rul_hours']:.1f}")
                    with col_b:
                        st.metric("Days to Maintenance", f"{rul_result['days_to_maintenance']:.1f}")
                    
                    urgency = rul_result['maintenance_urgency']
                    if urgency == "CRITICAL":
                        st.error(f"🔴 Urgency: {urgency}")
                    elif urgency == "WARNING":
                        st.warning(f"🟡 Urgency: {urgency}")
                    else:
                        st.success(f"🟢 Urgency: {urgency}")
                    
                    st.markdown("**Recommendations:**")
                    for rec in rul_result['recommendations']:
                        if "CRITICAL" in rec or "🚨" in rec:
                            st.error(rec)
                        elif "WARNING" in rec or "⚠️" in rec:
                            st.warning(rec)
                        else:
                            st.info(rec)
    
    with col2:
        if selected_machine:
            st.markdown(f"#### {selected_machine['machine_id']} - Sensor Trends")
            
            # Get historical sensor data
            history = monitor.get_sensor_history(selected_machine_id, hours=24)
            
            if history:
                # Create trend dataframe
                df_history = pd.DataFrame(history)
                df_history['timestamp'] = pd.to_datetime(df_history['timestamp'])
                
                # Plot sensor trends
                fig = go.Figure()
                
                # Temperature traces
                fig.add_trace(go.Scatter(
                    x=df_history['timestamp'],
                    y=df_history['process_temperature'],
                    mode='lines',
                    name='Process Temp (K)',
                    line=dict(color='red', width=2)
                ))
                
                fig.add_trace(go.Scatter(
                    x=df_history['timestamp'],
                    y=df_history['air_temperature'],
                    mode='lines',
                    name='Air Temp (K)',
                    line=dict(color='orange', width=2)
                ))
                
                fig.update_layout(
                    title="Temperature Trends (24h)",
                    xaxis_title="Time",
                    yaxis_title="Temperature (K)",
                    height=250,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Vibration and Tool Wear
                fig2 = go.Figure()
                
                fig2.add_trace(go.Scatter(
                    x=df_history['timestamp'],
                    y=df_history['vibration'],
                    mode='lines',
                    name='Vibration (mm/s)',
                    line=dict(color='purple', width=2),
                    yaxis='y'
                ))
                
                fig2.add_trace(go.Scatter(
                    x=df_history['timestamp'],
                    y=df_history['tool_wear'],
                    mode='lines',
                    name='Tool Wear (min)',
                    line=dict(color='brown', width=2),
                    yaxis='y2'
                ))
                
                fig2.update_layout(
                    title="Vibration & Tool Wear Trends (24h)",
                    xaxis_title="Time",
                    yaxis=dict(title="Vibration (mm/s)", side='left'),
                    yaxis2=dict(title="Tool Wear (min)", overlaying='y', side='right'),
                    height=250,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                
                st.plotly_chart(fig2, use_container_width=True)
                
                # Torque and Speed
                fig3 = go.Figure()
                
                fig3.add_trace(go.Scatter(
                    x=df_history['timestamp'],
                    y=df_history['torque'],
                    mode='lines',
                    name='Torque (Nm)',
                    line=dict(color='blue', width=2),
                    yaxis='y'
                ))
                
                fig3.add_trace(go.Scatter(
                    x=df_history['timestamp'],
                    y=df_history['rotational_speed'],
                    mode='lines',
                    name='Speed (RPM)',
                    line=dict(color='green', width=2),
                    yaxis='y2'
                ))
                
                fig3.update_layout(
                    title="Torque & Rotational Speed Trends (24h)",
                    xaxis_title="Time",
                    yaxis=dict(title="Torque (Nm)", side='left'),
                    yaxis2=dict(title="Speed (RPM)", overlaying='y', side='right'),
                    height=250,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                
                st.plotly_chart(fig3, use_container_width=True)
    
    # Summary statistics
    st.markdown("---")
    st.markdown("### 📊 Fleet Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        running = sum(1 for m in machines if m['status'] == 'RUNNING')
        st.metric("Running Machines", f"{running}/{len(machines)}")
    
    with col2:
        critical = sum(1 for m in machines if m['status'] == 'CRITICAL')
        st.metric("Critical Machines", critical)
    
    with col3:
        avg_rul = sum(m['rul_hours'] for m in machines) / len(machines)
        st.metric("Average RUL", f"{avg_rul:.1f}h")
    
    with col4:
        need_maint = sum(1 for m in machines if m['rul_hours'] < 168)  # < 7 days
        st.metric("Need Maintenance (7d)", need_maint)

except Exception as e:
    st.error(f"❌ Error loading maintenance data: {str(e)}")
    st.info("💡 Make sure all maintenance modules are properly installed.")

st.markdown("---")
st.caption("AI-ERP Quality Module v1.0.0 | Predictive Maintenance Module")
