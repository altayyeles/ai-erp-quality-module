"""
Real-time Sensor Monitoring for Predictive Maintenance
Monitors 8 machines (M001-M008) with simulated sensor data
"""

import logging
from typing import Dict, List
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)


class SensorMonitor:
    """
    Real-time sensor monitoring system for manufacturing machines.
    
    Monitors 8 machines with simulated sensor data for demonstration purposes.
    In production, this would connect to actual IoT sensors.
    """
    
    MACHINES = ['M001', 'M002', 'M003', 'M004', 'M005', 'M006', 'M007', 'M008']
    
    def __init__(self):
        """Initialize sensor monitor with seed for consistent simulation."""
        self.seed = 42
        random.seed(self.seed)
    
    def get_all_machines(self) -> List[Dict]:
        """
        Get status of all machines.
        
        Returns:
            List of machine status dictionaries
        """
        machines = []
        for machine_id in self.MACHINES:
            try:
                status = self.get_machine_status(machine_id)
                machines.append(status)
            except Exception as e:
                logger.error(f"Error getting status for {machine_id}: {e}")
        
        return machines
    
    def get_machine_status(self, machine_id: str) -> Dict:
        """
        Get detailed status of a specific machine.
        
        Args:
            machine_id: Machine identifier (e.g., 'M001')
            
        Returns:
            Dictionary with machine status and sensor readings
        """
        if machine_id not in self.MACHINES:
            raise ValueError(f"Invalid machine_id: {machine_id}. Must be one of {self.MACHINES}")
        
        # Generate consistent "random" data based on machine_id
        machine_index = self.MACHINES.index(machine_id)
        random.seed(self.seed + machine_index + int(datetime.now().timestamp() / 3600))  # Changes hourly
        
        # Simulate sensor readings with machine-specific characteristics
        sensor_readings = self._generate_sensor_readings(machine_index)
        
        # Calculate RUL based on sensor readings
        rul_hours = self._estimate_rul(sensor_readings)
        
        # Determine machine status
        status = self._determine_status(rul_hours, sensor_readings)
        
        # Calculate maintenance dates
        last_maintenance = datetime.now() - timedelta(days=random.randint(5, 45))
        next_maintenance = datetime.now() + timedelta(hours=rul_hours)
        
        return {
            "machine_id": machine_id,
            "status": status,
            "rul_hours": round(rul_hours, 1),
            "last_maintenance": last_maintenance.isoformat(),
            "next_maintenance": next_maintenance.isoformat(),
            "sensor_readings": sensor_readings,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_sensor_readings(self, machine_index: int) -> Dict[str, float]:
        """Generate simulated sensor readings for a machine."""
        # Base values with slight machine-specific variations
        base_offset = machine_index * 0.5
        
        # Simulate some machines having more wear/issues
        condition_factor = 1.0
        if machine_index in [1, 4, 6]:  # M002, M005, M007 have higher wear
            condition_factor = 1.3
        elif machine_index in [0, 3]:  # M001, M004 are in good condition
            condition_factor = 0.7
        
        readings = {
            "air_temperature": round(297 + random.uniform(-2, 3) + base_offset * 0.2, 2),
            "process_temperature": round(308 + random.uniform(-1.5, 2.5) + base_offset * 0.3 + condition_factor, 2),
            "rotational_speed": round(1500 + random.uniform(-200, 200) - condition_factor * 50, 1),
            "torque": round(40 + random.uniform(-8, 12) + condition_factor * 3, 2),
            "tool_wear": round(50 + random.uniform(0, 150) + condition_factor * 40, 1),
            "vibration": round(0.5 + random.uniform(-0.15, 0.25) + condition_factor * 0.15, 3),
            "humidity": round(60 + random.uniform(-10, 10), 1),
            "pressure": round(1.0 + random.uniform(-0.08, 0.12), 3)
        }
        
        return readings
    
    def _estimate_rul(self, sensor_readings: Dict[str, float]) -> float:
        """Estimate RUL based on sensor readings (simplified heuristic)."""
        tool_wear = sensor_readings['tool_wear']
        vibration = sensor_readings['vibration']
        temperature = sensor_readings['process_temperature']
        
        # Base RUL: 720 hours (30 days)
        base_rul = 720.0
        
        # Reduce based on wear factors
        wear_penalty = (tool_wear / 250) * 400
        vibration_penalty = max(0, (vibration - 0.5) / 1.0) * 250
        temp_penalty = max(0, (temperature - 310) / 10) * 180
        
        rul = base_rul - wear_penalty - vibration_penalty - temp_penalty
        rul = max(12, rul)  # Minimum 12 hours
        
        return rul
    
    def _determine_status(self, rul_hours: float, sensor_readings: Dict[str, float]) -> str:
        """Determine machine operational status."""
        tool_wear = sensor_readings['tool_wear']
        vibration = sensor_readings['vibration']
        temperature = sensor_readings['process_temperature']
        
        # Check if machine should be offline
        if random.random() < 0.05:  # 5% chance of offline
            return "OFFLINE"
        
        # Critical conditions
        if rul_hours < 48 or tool_wear > 220 or vibration > 1.0 or temperature > 315:
            return "CRITICAL"
        
        # Warning conditions
        if rul_hours < 120 or tool_wear > 180 or vibration > 0.8 or temperature > 312:
            return "WARNING"
        
        # Normal operation
        return "RUNNING"
    
    def get_sensor_history(self, machine_id: str, hours: int = 24) -> List[Dict]:
        """
        Get historical sensor readings for a machine.
        
        Args:
            machine_id: Machine identifier
            hours: Number of hours of history to retrieve
            
        Returns:
            List of historical sensor readings
        """
        if machine_id not in self.MACHINES:
            raise ValueError(f"Invalid machine_id: {machine_id}")
        
        history = []
        machine_index = self.MACHINES.index(machine_id)
        
        for i in range(hours):
            timestamp = datetime.now() - timedelta(hours=hours-i)
            random.seed(self.seed + machine_index + int(timestamp.timestamp() / 3600))
            
            readings = self._generate_sensor_readings(machine_index)
            readings['timestamp'] = timestamp.isoformat()
            
            history.append(readings)
        
        return history
