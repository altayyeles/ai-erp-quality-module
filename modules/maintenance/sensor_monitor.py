"""
Real-time Sensor Monitoring System

This module provides real-time monitoring of machine sensors across
multiple production machines (M001-M008).

Key Features:
- 8-machine monitoring system
- Real-time sensor readings simulation
- Machine status tracking (RUNNING/WARNING/CRITICAL/OFFLINE)
- RUL-based maintenance scheduling
- Historical maintenance tracking
"""

import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
from modules.maintenance.rul_model import RULModel
import pandas as pd

logger = logging.getLogger(__name__)


class SensorMonitor:
    """
    Real-time sensor monitoring for multiple machines.
    
    Monitors 8 production machines (M001-M008) with simulated sensor data
    and provides maintenance recommendations based on RUL predictions.
    """
    
    MACHINE_IDS = [f"M{i:03d}" for i in range(1, 9)]  # M001 to M008
    
    def __init__(self):
        """Initialize the sensor monitor with RUL model."""
        self.rul_model = RULModel()
        np.random.seed(42)  # For consistent simulated data
    
    def get_machine_status(self, machine_id: str) -> Dict:
        """
        Get current status of a specific machine.
        
        Args:
            machine_id: Machine identifier (e.g., 'M001')
            
        Returns:
            Dictionary with machine status and sensor readings
            
        Raises:
            ValueError: If machine_id is not valid
        """
        if machine_id not in self.MACHINE_IDS:
            raise ValueError(f"Invalid machine_id: {machine_id}. Valid IDs: {self.MACHINE_IDS}")
        
        # Generate simulated sensor data for the machine
        sensor_data = self._generate_sensor_data(machine_id)
        
        # Predict RUL
        X = pd.DataFrame([sensor_data])
        rul_prediction = self.rul_model.predict(X)
        
        # Determine machine status based on RUL
        rul_hours = rul_prediction['rul_hours']
        if rul_hours < 24:
            status = "CRITICAL"
        elif rul_hours < 72:
            status = "WARNING"
        elif rul_hours == 0:
            status = "OFFLINE"
        else:
            status = "RUNNING"
        
        # Calculate maintenance dates
        last_maintenance = datetime.now() - timedelta(days=np.random.randint(5, 30))
        next_maintenance = datetime.now() + timedelta(hours=rul_hours)
        
        return {
            'machine_id': machine_id,
            'status': status,
            'rul_hours': rul_hours,
            'maintenance_urgency': rul_prediction['maintenance_urgency'],
            'last_maintenance': last_maintenance.strftime('%Y-%m-%d'),
            'next_maintenance': next_maintenance.strftime('%Y-%m-%d'),
            'sensor_readings': sensor_data
        }
    
    def get_all_machines(self) -> List[Dict]:
        """
        Get status of all monitored machines.
        
        Returns:
            List of dictionaries with each machine's status
        """
        logger.info(f"Fetching status for {len(self.MACHINE_IDS)} machines...")
        
        machines = []
        for machine_id in self.MACHINE_IDS:
            try:
                machine_status = self.get_machine_status(machine_id)
                machines.append(machine_status)
            except Exception as e:
                logger.error(f"Error fetching status for {machine_id}: {e}")
                machines.append({
                    'machine_id': machine_id,
                    'status': 'OFFLINE',
                    'error': str(e)
                })
        
        return machines
    
    def _generate_sensor_data(self, machine_id: str) -> Dict[str, float]:
        """
        Generate simulated sensor data for a machine.
        
        Uses a seed based on machine_id for consistency but with variations.
        
        Args:
            machine_id: Machine identifier
            
        Returns:
            Dictionary of sensor readings
        """
        # Use machine ID to seed for consistency per machine
        machine_num = int(machine_id[1:])
        seed = 42 + machine_num
        rng = np.random.RandomState(seed)
        
        # Add time-based variation to make it look more realistic
        time_factor = (datetime.now().hour % 24) / 24.0
        
        # Different machines have different "health" levels
        # Machines M003, M005, M007 have higher wear/stress
        if machine_num in [3, 5, 7]:
            wear_factor = 1.3
            stress_factor = 1.2
        else:
            wear_factor = 1.0
            stress_factor = 1.0
        
        sensor_data = {
            'air_temperature': float(rng.normal(298, 2) + time_factor * 2),
            'process_temperature': float(rng.normal(308, 1.5) * stress_factor),
            'rotational_speed': float(rng.normal(1500, 100) / stress_factor),
            'torque': float(rng.normal(40, 8) * stress_factor),
            'tool_wear': float(rng.uniform(50, 200) * wear_factor),
            'vibration': float(rng.normal(0.5, 0.1) * stress_factor),
            'humidity': float(rng.normal(60, 8)),
            'pressure': float(rng.normal(1.0, 0.08))
        }
        
        return sensor_data
    
    def get_critical_machines(self) -> List[str]:
        """
        Get list of machines in CRITICAL status.
        
        Returns:
            List of machine IDs that require immediate attention
        """
        critical = []
        for machine_id in self.MACHINE_IDS:
            status = self.get_machine_status(machine_id)
            if status['status'] == 'CRITICAL':
                critical.append(machine_id)
        
        return critical
    
    def get_maintenance_schedule(self) -> List[Dict]:
        """
        Get maintenance schedule for all machines sorted by urgency.
        
        Returns:
            List of machines with maintenance info, sorted by RUL ascending
        """
        machines = self.get_all_machines()
        
        # Sort by RUL (ascending) - most urgent first
        machines.sort(key=lambda m: m.get('rul_hours', float('inf')))
        
        schedule = []
        for machine in machines:
            schedule.append({
                'machine_id': machine['machine_id'],
                'status': machine['status'],
                'rul_hours': machine.get('rul_hours', 0),
                'next_maintenance': machine.get('next_maintenance', 'Unknown'),
                'urgency': machine.get('maintenance_urgency', 'UNKNOWN')
            })
        
        return schedule


def create_demo_monitor() -> SensorMonitor:
    """
    Create a demo sensor monitor.
    
    Returns:
        Initialized SensorMonitor
    """
    return SensorMonitor()
