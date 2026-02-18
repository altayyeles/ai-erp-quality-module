"""
Predictive Maintenance Dashboard Page
Streamlit page for machine health monitoring and RUL prediction
"""

import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Predictive Maintenance", page_icon="🔧", layout="wide")

st.title("🔧 Predictive Maintenance")
st.markdown("---")

try:
    from modules.maintenance.sensor_monitor import SensorMonitor
    from modules.maintenance.rul_model import RULModel
    
    monitor = SensorMonitor()
    
    # Get all machines
    machines = monitor.get_all_machines()
    
    # Fleet summary
    fleet_summary = monitor.get_fleet_summary()
    
    st.subheader("🏭 Fleet Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Machines", fleet_summary['total_machines'])
    
    with col2:
        health_score = fleet_summary['fleet_health_score']
        st.metric("Fleet Health", f"{health_score:.1f}%", delta=None)
    
    with col3:
        st.metric("Avg RUL", f"{fleet_summary['average_rul_hours']:.0f} hrs")
    
    with col4:
        critical = fleet_summary['status_breakdown']['CRITICAL']
        warning = fleet_summary['status_breakdown']['WARNING']
        st.metric("Needs Attention", critical + warning)
    
    st.markdown("---")
    
    # Machine status cards
    st.subheader("🖥️ Machine Status")
    
    # Group machines into rows
    num_cols = 4
    for i in range(0, len(machines), num_cols):
        cols = st.columns(num_cols)
        
        for j, col in enumerate(cols):
            if i + j < len(machines):
                machine = machines[i + j]
                
                with col:
                    # Status color coding
                    status_colors = {
                        'RUNNING': '🟢',
                        'WARNING': '🟡',
                        'CRITICAL': '🔴',
                        'OFFLINE': '⚫'
                    }
                    
                    status_icon = status_colors.get(machine['status'], '⚪')
                    
                    st.markdown(f"### {status_icon} {machine['machine_id']}")
                    st.caption(f"Status: **{machine['status']}**")
                    
                    # RUL progress bar
                    rul_pct = min(100, (machine['rul_hours'] / 500) * 100)
                    st.progress(rul_pct / 100)
                    st.caption(f"RUL: {machine['rul_days']:.1f} days ({machine['rul_hours']:.0f} hrs)")
                    
                    # Key sensors
                    sensors = machine['sensor_readings']
                    st.caption(f"🌡️ {sensors['process_temperature']:.1f}K | "
                             f"⚙️ {sensors['tool_wear']:.0f} min | "
                             f"📊 {sensors['vibration']:.2f} mm/s")
    
    st.markdown("---")
    
    # Detailed machine analysis
    st.subheader("🔍 Detailed Analysis")
    
    machine_ids = [m['machine_id'] for m in machines]
    selected_machine = st.selectbox("Select Machine", machine_ids)
    
    if selected_machine:
        machine_data = monitor.get_machine_status(selected_machine)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"#### Machine {selected_machine}")
            
            # Sensor readings table
            sensors_df = pd.DataFrame([
                {"Parameter": "Air Temperature", "Value": f"{machine_data['sensor_readings']['air_temperature']:.2f} K"},
                {"Parameter": "Process Temperature", "Value": f"{machine_data['sensor_readings']['process_temperature']:.2f} K"},
                {"Parameter": "Rotational Speed", "Value": f"{machine_data['sensor_readings']['rotational_speed']:.1f} rpm"},
                {"Parameter": "Torque", "Value": f"{machine_data['sensor_readings']['torque']:.2f} Nm"},
                {"Parameter": "Tool Wear", "Value": f"{machine_data['sensor_readings']['tool_wear']:.1f} min"},
                {"Parameter": "Vibration", "Value": f"{machine_data['sensor_readings']['vibration']:.3f} mm/s"},
                {"Parameter": "Humidity", "Value": f"{machine_data['sensor_readings']['humidity']:.1f} %"},
                {"Parameter": "Pressure", "Value": f"{machine_data['sensor_readings']['pressure']:.3f} bar"},
            ])
            
            st.dataframe(sensors_df, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("#### Maintenance Schedule")
            st.metric("Last Maintenance", machine_data['last_maintenance'])
            st.metric("Next Maintenance", machine_data['next_maintenance'])
            st.metric("Total Runtime", f"{machine_data['total_runtime_hours']:,} hrs")
            
            # RUL prediction
            st.markdown("#### RUL Prediction")
            
            rul_model = RULModel()
            prediction = rul_model.predict(machine_data['sensor_readings'])
            
            # Urgency badge
            urgency_colors = {
                'NORMAL': '🟢',
                'WARNING': '🟡',
                'CRITICAL': '🔴'
            }
            urgency_icon = urgency_colors.get(prediction['maintenance_urgency'], '⚪')
            
            st.markdown(f"**{urgency_icon} {prediction['maintenance_urgency']}**")
            st.caption(f"Estimated: {prediction['days_to_maintenance']} days")
        
        # Recommendations
        st.markdown("---")
        st.markdown("#### 💡 Recommendations")
        
        for rec in prediction.get('recommendations', []):
            if "🚨" in rec or "URGENT" in rec:
                st.error(rec)
            elif "⚠️" in rec:
                st.warning(rec)
            else:
                st.info(rec)
        
        # Sensor health
        if 'sensor_health' in prediction:
            st.markdown("---")
            st.markdown("#### 🩺 Sensor Health Status")
            
            health_cols = st.columns(4)
            health_items = list(prediction['sensor_health'].items())
            
            for i, (sensor, status) in enumerate(health_items):
                col_idx = i % 4
                with health_cols[col_idx]:
                    status_icon = '🟢' if status == 'GOOD' else '🟡' if status == 'WARNING' else '🔴'
                    st.caption(f"{status_icon} {sensor.replace('_', ' ').title()}")
    
    # Trend visualization
    st.markdown("---")
    st.subheader("📈 Historical Trends")
    
    if selected_machine:
        trends = monitor.get_machine_trends(selected_machine, hours=24)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### RUL Trend (24h)")
            trend_df = pd.DataFrame({
                'Hour': range(24),
                'RUL (hours)': trends['rul_hours']
            })
            st.line_chart(trend_df.set_index('Hour'))
        
        with col2:
            st.markdown("##### Vibration Trend (24h)")
            vib_df = pd.DataFrame({
                'Hour': range(24),
                'Vibration (mm/s)': trends['vibration']
            })
            st.line_chart(vib_df.set_index('Hour'))

except ImportError as e:
    st.error(f"❌ Required module not available: {str(e)}")
    st.info("💡 Please ensure maintenance modules are properly installed.")

except Exception as e:
    st.error(f"❌ Error: {str(e)}")
    st.info("💡 Using demo mode with simulated data.")
    
    # Show demo placeholder
    st.metric("Demo Machine M001", "🟢 RUNNING")
    st.progress(0.8)
    st.caption("RUL: 12.5 days (300 hrs)")

st.markdown("---")
st.caption("Predictive Maintenance Module | AI-ERP Quality System")
