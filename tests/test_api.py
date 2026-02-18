"""
Unit tests for FastAPI endpoints
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestRootEndpoints:
    """Test root and health endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'message' in data
        assert 'version' in data
        assert 'docs' in data
        assert 'status' in data
        assert 'timestamp' in data
        
        assert data['status'] == 'running'
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'status' in data
        assert 'timestamp' in data
        assert 'modules' in data
        
        assert data['status'] == 'healthy'
        
        modules = data['modules']
        assert 'quality' in modules
        assert 'maintenance' in modules
        assert 'supplier' in modules
        assert 'vision' in modules
        assert 'dashboard' in modules


class TestQualityEndpoints:
    """Test quality prediction endpoints"""
    
    def test_predict_quality(self):
        """Test quality prediction endpoint"""
        payload = {
            'air_temperature': 298.0,
            'process_temperature': 308.0,
            'rotational_speed': 1500.0,
            'torque': 40.0,
            'tool_wear': 100.0,
            'vibration': 0.5,
            'humidity': 60.0,
            'pressure': 1.0
        }
        
        response = client.post("/api/v1/quality/predict", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['status'] == 'success'
        assert 'data' in data
        
        result = data['data']
        assert 'defect_probability' in result
        assert 'risk_level' in result
        assert 'is_defect_predicted' in result


class TestMaintenanceEndpoints:
    """Test maintenance endpoints"""
    
    def test_predict_rul(self):
        """Test RUL prediction endpoint"""
        payload = {
            'air_temperature': 298.0,
            'process_temperature': 308.0,
            'rotational_speed': 1500.0,
            'torque': 40.0,
            'tool_wear': 100.0,
            'vibration': 0.5,
            'humidity': 60.0,
            'pressure': 1.0
        }
        
        response = client.post("/api/v1/maintenance/predict-rul", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['status'] == 'success'
        assert 'data' in data
        
        result = data['data']
        assert 'rul_hours' in result
        assert 'maintenance_urgency' in result
    
    def test_get_all_machines(self):
        """Test get all machines endpoint"""
        response = client.get("/api/v1/maintenance/machines")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['status'] == 'success'
        assert 'data' in data
        
        machines = data['data']
        assert isinstance(machines, list)
        assert len(machines) == 8
    
    def test_get_machine_status(self):
        """Test get specific machine status"""
        response = client.get("/api/v1/maintenance/machines/M001")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['status'] == 'success'
        assert 'data' in data
        
        machine = data['data']
        assert machine['machine_id'] == 'M001'
        assert 'status' in machine
        assert 'rul_hours' in machine
    
    def test_get_invalid_machine(self):
        """Test getting invalid machine"""
        response = client.get("/api/v1/maintenance/machines/INVALID")
        
        assert response.status_code == 404


class TestSupplierEndpoints:
    """Test supplier endpoints"""
    
    def test_score_supplier(self):
        """Test supplier scoring endpoint"""
        payload = {
            'supplier_id': 'SUP-001',
            'on_time_delivery_rate': 0.90,
            'quality_score': 0.85,
            'price_competitiveness': 0.75,
            'defect_rate': 0.03,
            'response_time_days': 2.0,
            'years_of_partnership': 3.0
        }
        
        response = client.post("/api/v1/suppliers/score", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['status'] == 'success'
        assert 'data' in data
        
        result = data['data']
        assert 'overall_score' in result
        assert 'risk_level' in result
        assert 'category' in result
    
    def test_procurement_advice(self):
        """Test procurement advisory endpoint"""
        payload = {
            'supplier_id': 'SUP-001',
            'on_time_delivery_rate': 0.90,
            'quality_score': 0.85,
            'price_competitiveness': 0.75,
            'defect_rate': 0.03,
            'response_time_days': 2.0,
            'years_of_partnership': 3.0
        }
        
        response = client.post("/api/v1/suppliers/advise", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['status'] == 'success'
        assert 'data' in data
        
        result = data['data']
        assert 'action' in result
        assert 'confidence' in result
        assert 'reasoning' in result


class TestDashboardEndpoints:
    """Test dashboard endpoints"""
    
    def test_get_kpis(self):
        """Test get KPIs endpoint"""
        response = client.get("/api/v1/dashboard/kpis")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['status'] == 'success'
        assert 'data' in data
        
        result = data['data']
        assert 'timestamp' in result
        assert 'kpis' in result
        assert 'summary' in result
    
    def test_get_alerts(self):
        """Test get alerts endpoint"""
        response = client.get("/api/v1/dashboard/alerts")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['status'] == 'success'
        assert 'data' in data
        
        alerts = data['data']
        assert isinstance(alerts, list)
    
    def test_dismiss_alert(self):
        """Test dismiss alert endpoint"""
        # First, get active alerts
        response = client.get("/api/v1/dashboard/alerts")
        alerts = response.json()['data']
        
        if len(alerts) > 0:
            alert_id = alerts[0]['id']
            
            # Dismiss the alert
            response = client.delete(f"/api/v1/dashboard/alerts/{alert_id}")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data['status'] == 'success'
    
    def test_dismiss_invalid_alert(self):
        """Test dismissing non-existent alert"""
        response = client.delete("/api/v1/dashboard/alerts/99999")
        
        assert response.status_code == 404


class TestVisionEndpoints:
    """Test vision inspection endpoints - basic structure tests"""
    
    def test_inspect_endpoint_exists(self):
        """Test that inspect endpoint exists (without valid image)"""
        # This will fail without a valid image file, but tests the endpoint exists
        response = client.post("/api/v1/vision/inspect")
        
        # Will return 422 (validation error) because file is required
        assert response.status_code == 422
    
    def test_detect_anomaly_endpoint_exists(self):
        """Test that detect-anomaly endpoint exists (without valid image)"""
        # This will fail without a valid image file, but tests the endpoint exists
        response = client.post("/api/v1/vision/detect-anomaly")
        
        # Will return 422 (validation error) because file is required
        assert response.status_code == 422
