"""
Real-Time Sensor Monitoring System
Monitors machine health and sensor status across the production floor

This module provides real-time machine status monitoring for 8 machines (M001-M008)
with sensor readings, RUL estimation, and maintenance schedules.
"""

import logging
from typing import Dict, List
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)


class SensorMonitor:
    """
    Real-time sensor monitoring system for manufacturing equipment.
    
    Monitors 8 machines (M001-M008) with simulated sensor readings
    and provides machine health status.
    """
    
    MACHINE_IDS = [f"M{i:03d}" for i in range(1, 9)]  # M001 to M008
    
    def __init__(self):
        """Initialize the sensor monitor."""
        random.seed(42)  # For consistent simulated data
        self._machine_states = {}
        self._initialize_machines()
    
    def _initialize_machines(self):
        """Initialize baseline states for all machines."""
        base_date = datetime.now()
        
        for i, machine_id in enumerate(self.MACHINE_IDS):
            # Vary machine conditions
            condition_factor = 0.7 + (i * 0.05)  # 0.7 to 1.05
            
            self._machine_states[machine_id] = {
                'baseline_tool_wear': 50 + i * 20,
                'baseline_vibration': 0.4 + i * 0.05,
                'condition_factor': condition_factor,
                'last_maintenance': base_date - timedelta(days=10 + i * 5),
                'total_runtime_hours': 5000 + i * 500
            }
    
    def get_machine_status(self, machine_id: str) -> Dict:
        """
        Get current status of a specific machine.
        
        Args:
            machine_id: Machine identifier (e.g., 'M001')
            
        Returns:
            Dictionary with machine status and sensor readings
        """
        if machine_id not in self.MACHINE_IDS:
            raise ValueError(f"Invalid machine_id: {machine_id}. Must be one of {self.MACHINE_IDS}")
        
        state = self._machine_states[machine_id]
        sensor_readings = self._generate_sensor_readings(machine_id, state)
        
        # Calculate RUL using rule-based estimation
        rul_hours = self._estimate_rul(sensor_readings)
        status = self._determine_status(rul_hours, sensor_readings)
        
        last_maint = state['last_maintenance']
        next_maint = last_maint + timedelta(days=30)
        
        return {
            'machine_id': machine_id,
            'status': status,
            'rul_hours': round(rul_hours, 1),
            'rul_days': round(rul_hours / 24, 1),
            'last_maintenance': last_maint.strftime('%Y-%m-%d'),
            'next_maintenance': next_maint.strftime('%Y-%m-%d'),
            'total_runtime_hours': state['total_runtime_hours'],
            'sensor_readings': sensor_readings,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_all_machines(self) -> List[Dict]:
        """
        Get status of all machines.
        
        Returns:
            List of machine status dictionaries
        """
        return [self.get_machine_status(mid) for mid in self.MACHINE_IDS]
    
    def _generate_sensor_readings(self, machine_id: str, state: Dict) -> Dict[str, float]:
        """Generate realistic sensor readings for a machine."""
        # Use machine index for variation
        machine_idx = self.MACHINE_IDS.index(machine_id)
        condition = state['condition_factor']
        
        # Add some time-based variation (simulate drift)
        time_factor = (hash(str(datetime.now().minute)) % 100) / 100.0
        
        readings = {
            'air_temperature': round(296 + machine_idx * 0.5 + time_factor * 3, 2),
            'process_temperature': round(307 + machine_idx * 0.4 + time_factor * 2, 2),
            'rotational_speed': round(1500 - machine_idx * 30 + time_factor * 100, 1),
            'torque': round(38 + machine_idx * 2 + time_factor * 5, 2),
            'tool_wear': round(state['baseline_tool_wear'] + machine_idx * 5, 1),
            'vibration': round(state['baseline_vibration'] + time_factor * 0.2, 3),
            'humidity': round(58 + machine_idx * 1.5 + time_factor * 5, 1),
            'pressure': round(0.98 + machine_idx * 0.01 + time_factor * 0.03, 3)
        }
        
        # Apply condition factor (worse condition = worse readings)
        if condition > 1.0:
            readings['vibration'] *= condition
            readings['tool_wear'] *= condition
            readings['process_temperature'] += (condition - 1.0) * 5
        
        return readings
    
    def _estimate_rul(self, sensor_readings: Dict[str, float]) -> float:
        """Estimate RUL based on sensor readings using heuristics."""
        rul = 600.0  # Base RUL
        
        # Tool wear impact
        tool_wear = sensor_readings.get('tool_wear', 0)
        if tool_wear > 180:
            rul -= (tool_wear - 180) * 2.5
        elif tool_wear > 120:
            rul -= (tool_wear - 120) * 1.5
        
        # Vibration impact
        vibration = sensor_readings.get('vibration', 0.5)
        if vibration > 0.8:
            rul -= (vibration - 0.8) * 150
        elif vibration > 0.6:
            rul -= (vibration - 0.6) * 80
        
        # Temperature impact
        process_temp = sensor_readings.get('process_temperature', 308)
        if process_temp > 312:
            rul -= (process_temp - 312) * 15
        elif process_temp > 310:
            rul -= (process_temp - 310) * 8
        
        # Torque impact
        torque = sensor_readings.get('torque', 40)
        if torque > 60:
            rul -= (torque - 60) * 8
        elif torque > 50:
            rul -= (torque - 50) * 4
        
        return max(24, rul)  # Minimum 24 hours
    
    def _determine_status(self, rul_hours: float, sensor_readings: Dict[str, float]) -> str:
        """Determine machine operational status."""
        # Check for critical conditions
        vibration = sensor_readings.get('vibration', 0.5)
        tool_wear = sensor_readings.get('tool_wear', 0)
        process_temp = sensor_readings.get('process_temperature', 308)
        
        if rul_hours < 48 or vibration > 1.2 or tool_wear > 220:
            return "CRITICAL"
        elif rul_hours < 120 or vibration > 0.9 or tool_wear > 180 or process_temp > 312:
            return "WARNING"
        elif rul_hours < 240:
            return "RUNNING"
        else:
            return "RUNNING"
    
    def get_machine_trends(self, machine_id: str, hours: int = 24) -> Dict:
        """
        Get historical trends for a machine (simulated).
        
        Args:
            machine_id: Machine identifier
            hours: Number of hours of historical data
            
        Returns:
            Dictionary with time-series trend data
        """
        if machine_id not in self.MACHINE_IDS:
            raise ValueError(f"Invalid machine_id: {machine_id}")
        
        state = self._machine_states[machine_id]
        timestamps = []
        rul_values = []
        vibration_values = []
        
        # Generate historical trend (simulated)
        now = datetime.now()
        for i in range(hours):
            ts = now - timedelta(hours=hours - i)
            timestamps.append(ts.isoformat())
            
            # Simulate gradual RUL decrease
            rul_values.append(400 - i * 2 + random.uniform(-10, 10))
            
            # Simulate vibration increase
            vibration_values.append(0.5 + i * 0.005 + random.uniform(-0.05, 0.05))
        
        return {
            'machine_id': machine_id,
            'timestamps': timestamps,
            'rul_hours': rul_values,
            'vibration': vibration_values
        }
    
    def get_fleet_summary(self) -> Dict:
        """
        Get summary statistics for the entire machine fleet.
        
        Returns:
            Dictionary with fleet-level KPIs
        """
        all_machines = self.get_all_machines()
        
        critical_count = sum(1 for m in all_machines if m['status'] == 'CRITICAL')
        warning_count = sum(1 for m in all_machines if m['status'] == 'WARNING')
        running_count = sum(1 for m in all_machines if m['status'] == 'RUNNING')
        
        avg_rul = sum(m['rul_hours'] for m in all_machines) / len(all_machines)
        min_rul = min(m['rul_hours'] for m in all_machines)
        
        return {
            'total_machines': len(all_machines),
            'status_breakdown': {
                'CRITICAL': critical_count,
                'WARNING': warning_count,
                'RUNNING': running_count
            },
            'fleet_health_score': round((running_count / len(all_machines)) * 100, 1),
            'average_rul_hours': round(avg_rul, 1),
            'minimum_rul_hours': round(min_rul, 1),
            'machines_needing_attention': critical_count + warning_count,
            'timestamp': datetime.now().isoformat()
        }
