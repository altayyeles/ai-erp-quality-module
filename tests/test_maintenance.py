"""
Unit tests for Maintenance module (rul_model and sensor_monitor)
"""

import pytest
import pandas as pd
import numpy as np
from modules.maintenance.rul_model import RULModel, create_demo_rul_model
from modules.maintenance.sensor_monitor import SensorMonitor


class TestRULModel:
    """Test cases for RULModel"""
    
    def test_model_initialization(self):
        """Test RUL model can be initialized"""
        model = RULModel()
        assert model is not None
        assert model.model is not None  # Should auto-train
    
    def test_predict_rul(self):
        """Test RUL prediction"""
        model = RULModel()
        
        X = pd.DataFrame([{
            'air_temperature': 298.0,
            'process_temperature': 308.0,
            'rotational_speed': 1500.0,
            'torque': 40.0,
            'tool_wear': 100.0,
            'vibration': 0.5,
            'humidity': 60.0,
            'pressure': 1.0
        }])
        
        result = model.predict(X)
        
        assert 'rul_hours' in result
        assert 'maintenance_urgency' in result
        assert 'days_to_maintenance' in result
        assert result['rul_hours'] >= 0
        assert result['maintenance_urgency'] in ['NORMAL', 'WARNING', 'CRITICAL']
        assert result['days_to_maintenance'] >= 0
    
    def test_critical_urgency(self):
        """Test critical urgency with high wear"""
        model = RULModel()
        
        # High wear parameters that should predict low RUL
        X = pd.DataFrame([{
            'air_temperature': 300.0,
            'process_temperature': 315.0,
            'rotational_speed': 1300.0,
            'torque': 55.0,
            'tool_wear': 240.0,
            'vibration': 0.9,
            'humidity': 70.0,
            'pressure': 1.08
        }])
        
        result = model.predict(X)
        
        # Should predict low RUL with high wear
        assert result['rul_hours'] < 200
    
    def test_feature_importance(self):
        """Test feature importance calculation"""
        model = RULModel()
        importance = model.get_feature_importance()
        
        assert len(importance) == 8
        assert all(0 <= v <= 1 for v in importance.values())
    
    def test_training(self):
        """Test model training"""
        np.random.seed(42)
        n_samples = 100
        
        X = pd.DataFrame({
            'air_temperature': np.random.normal(298, 2, n_samples),
            'process_temperature': np.random.normal(308, 1.5, n_samples),
            'rotational_speed': np.random.normal(1500, 150, n_samples),
            'torque': np.random.normal(40, 8, n_samples),
            'tool_wear': np.random.uniform(0, 180, n_samples),
            'vibration': np.random.normal(0.5, 0.1, n_samples),
            'humidity': np.random.normal(60, 8, n_samples),
            'pressure': np.random.normal(1.0, 0.08, n_samples),
        })
        
        y = pd.Series(np.random.uniform(50, 400, n_samples))
        
        model = RULModel.__new__(RULModel)
        model.model = None
        model.feature_names = RULModel.FEATURE_NAMES
        
        metrics = model.train(X, y)
        
        assert 'mae' in metrics
        assert 'rmse' in metrics
        assert 'r2' in metrics
        assert metrics['mae'] > 0


class TestSensorMonitor:
    """Test cases for SensorMonitor"""
    
    def test_monitor_initialization(self):
        """Test sensor monitor can be initialized"""
        monitor = SensorMonitor()
        assert monitor is not None
    
    def test_get_all_machines(self):
        """Test getting all machines"""
        monitor = SensorMonitor()
        machines = monitor.get_all_machines()
        
        assert len(machines) == 8
        assert all(m['machine_id'] in ['M001', 'M002', 'M003', 'M004', 'M005', 'M006', 'M007', 'M008'] 
                  for m in machines)
    
    def test_get_machine_status(self):
        """Test getting specific machine status"""
        monitor = SensorMonitor()
        status = monitor.get_machine_status('M001')
        
        assert status['machine_id'] == 'M001'
        assert 'status' in status
        assert status['status'] in ['RUNNING', 'WARNING', 'CRITICAL', 'OFFLINE']
        assert 'rul_hours' in status
        assert 'sensor_readings' in status
        assert 'last_maintenance' in status
        assert 'next_maintenance' in status
    
    def test_invalid_machine_id(self):
        """Test error handling for invalid machine ID"""
        monitor = SensorMonitor()
        
        with pytest.raises(ValueError):
            monitor.get_machine_status('INVALID')
    
    def test_sensor_readings(self):
        """Test sensor readings contain all required fields"""
        monitor = SensorMonitor()
        status = monitor.get_machine_status('M001')
        
        sensor_data = status['sensor_readings']
        
        required_sensors = [
            'air_temperature', 'process_temperature', 'rotational_speed',
            'torque', 'tool_wear', 'vibration', 'humidity', 'pressure'
        ]
        
        for sensor in required_sensors:
            assert sensor in sensor_data
            assert isinstance(sensor_data[sensor], (int, float))
    
    def test_critical_machines(self):
        """Test getting critical machines"""
        monitor = SensorMonitor()
        critical = monitor.get_critical_machines()
        
        assert isinstance(critical, list)
        # All machines in critical list should be valid
        for machine_id in critical:
            assert machine_id in ['M001', 'M002', 'M003', 'M004', 'M005', 'M006', 'M007', 'M008']
    
    def test_maintenance_schedule(self):
        """Test maintenance schedule generation"""
        monitor = SensorMonitor()
        schedule = monitor.get_maintenance_schedule()
        
        assert len(schedule) == 8
        assert all('machine_id' in s for s in schedule)
        assert all('rul_hours' in s for s in schedule)
        assert all('urgency' in s for s in schedule)
        
        # Should be sorted by RUL (ascending)
        rul_values = [s['rul_hours'] for s in schedule]
        assert rul_values == sorted(rul_values)
