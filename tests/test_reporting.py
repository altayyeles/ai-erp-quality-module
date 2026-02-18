"""
Unit tests for Reporting module (kpi_engine and alert_system)
"""

import pytest
from modules.reporting.kpi_engine import KPIEngine
from modules.reporting.alert_system import AlertSystem


class TestKPIEngine:
    """Test cases for KPIEngine"""
    
    def test_engine_initialization(self):
        """Test KPI engine can be initialized"""
        engine = KPIEngine()
        assert engine is not None
        assert engine.targets is not None
    
    def test_get_snapshot(self):
        """Test KPI snapshot generation"""
        engine = KPIEngine()
        snapshot = engine.get_snapshot()
        
        assert 'timestamp' in snapshot
        assert 'kpis' in snapshot
        assert 'summary' in snapshot
        
        # Check KPIs
        kpis = snapshot['kpis']
        assert 'oee' in kpis
        assert 'fpy' in kpis
        assert 'dpmo' in kpis
        assert 'cpk' in kpis
    
    def test_kpi_structure(self):
        """Test KPI data structure"""
        engine = KPIEngine()
        snapshot = engine.get_snapshot()
        
        for kpi_name, kpi_data in snapshot['kpis'].items():
            assert 'name' in kpi_data
            assert 'description' in kpi_data
            assert 'value' in kpi_data
            assert 'target' in kpi_data
            assert 'unit' in kpi_data
            assert 'status' in kpi_data
            assert 'performance_ratio' in kpi_data
            assert 'deviation' in kpi_data
            assert 'trend' in kpi_data
            
            assert kpi_data['status'] in ['GOOD', 'WARNING', 'CRITICAL']
            assert kpi_data['trend'] in ['STABLE', 'IMPROVING', 'DECLINING']
    
    def test_summary_structure(self):
        """Test summary structure"""
        engine = KPIEngine()
        snapshot = engine.get_snapshot()
        summary = snapshot['summary']
        
        assert 'overall_status' in summary
        assert 'targets_met' in summary
        assert 'total_kpis' in summary
        assert 'performance_percentage' in summary
        assert 'message' in summary
        
        assert summary['overall_status'] in ['EXCELLENT', 'GOOD', 'FAIR', 'POOR']
        assert 0 <= summary['targets_met'] <= summary['total_kpis']
        assert 0 <= summary['performance_percentage'] <= 100
    
    def test_calculate_oee(self):
        """Test OEE calculation"""
        engine = KPIEngine()
        
        oee = engine.calculate_oee(0.92, 0.95, 0.98)
        
        assert 0 <= oee <= 100
        assert abs(oee - 85.596) < 0.1  # 0.92 * 0.95 * 0.98 * 100 (allow small rounding differences)
    
    def test_calculate_fpy(self):
        """Test FPY calculation"""
        engine = KPIEngine()
        
        fpy = engine.calculate_fpy(950, 1000)
        
        assert fpy == 95.0
    
    def test_calculate_fpy_zero_units(self):
        """Test FPY with zero units"""
        engine = KPIEngine()
        
        fpy = engine.calculate_fpy(0, 0)
        
        assert fpy == 0.0
    
    def test_calculate_dpmo(self):
        """Test DPMO calculation"""
        engine = KPIEngine()
        
        dpmo = engine.calculate_dpmo(35, 1000, 10)
        
        assert dpmo == 3500.0
    
    def test_calculate_dpmo_zero_units(self):
        """Test DPMO with zero units"""
        engine = KPIEngine()
        
        dpmo = engine.calculate_dpmo(0, 0, 10)
        
        assert dpmo == 0.0
    
    def test_calculate_cpk(self):
        """Test Cpk calculation"""
        engine = KPIEngine()
        
        cpk = engine.calculate_cpk(100, 5, 115, 85)
        
        assert cpk > 0
        assert cpk == 1.0  # min((115-100)/(3*5), (100-85)/(3*5))
    
    def test_calculate_cpk_zero_std(self):
        """Test Cpk with zero standard deviation"""
        engine = KPIEngine()
        
        cpk = engine.calculate_cpk(100, 0, 115, 85)
        
        assert cpk == 0.0


class TestAlertSystem:
    """Test cases for AlertSystem"""
    
    def test_system_initialization(self):
        """Test alert system can be initialized"""
        system = AlertSystem()
        assert system is not None
    
    def test_get_active_alerts(self):
        """Test getting active alerts"""
        system = AlertSystem()
        alerts = system.get_active_alerts()
        
        assert isinstance(alerts, list)
        # Demo alerts should be created
        assert len(alerts) > 0
    
    def test_create_alert(self):
        """Test creating a new alert"""
        system = AlertSystem()
        
        alert = system.create_alert(
            title="Test Alert",
            message="This is a test alert",
            severity="WARNING",
            source="quality"
        )
        
        assert alert['title'] == "Test Alert"
        assert alert['message'] == "This is a test alert"
        assert alert['severity'] == "WARNING"
        assert alert['source'] == "quality"
        assert alert['is_active'] is True
        assert 'id' in alert
        assert 'timestamp' in alert
    
    def test_dismiss_alert(self):
        """Test dismissing an alert"""
        system = AlertSystem()
        
        # Create an alert
        alert = system.create_alert(
            title="Test Alert",
            message="Test",
            severity="INFO",
            source="system"
        )
        
        alert_id = alert['id']
        
        # Dismiss it
        system.dismiss_alert(alert_id)
        
        # Verify it's dismissed
        dismissed_alert = system.get_alert(alert_id)
        assert dismissed_alert['is_active'] is False
    
    def test_dismiss_nonexistent_alert(self):
        """Test dismissing non-existent alert"""
        system = AlertSystem()
        
        with pytest.raises(ValueError):
            system.dismiss_alert(99999)
    
    def test_get_alert_by_id(self):
        """Test getting specific alert by ID"""
        system = AlertSystem()
        
        alert = system.create_alert(
            title="Test",
            message="Test message",
            severity="INFO",
            source="system"
        )
        
        retrieved = system.get_alert(alert['id'])
        
        assert retrieved is not None
        assert retrieved['id'] == alert['id']
        assert retrieved['title'] == "Test"
    
    def test_get_alerts_by_severity(self):
        """Test filtering alerts by severity"""
        system = AlertSystem()
        
        # Create alerts with different severities
        system.create_alert("Critical 1", "Test", "CRITICAL", "system")
        system.create_alert("Warning 1", "Test", "WARNING", "system")
        system.create_alert("Info 1", "Test", "INFO", "system")
        
        critical_alerts = system.get_alerts_by_severity("CRITICAL")
        
        assert len(critical_alerts) > 0
        assert all(a['severity'] == 'CRITICAL' for a in critical_alerts)
    
    def test_get_alerts_by_source(self):
        """Test filtering alerts by source"""
        system = AlertSystem()
        
        system.create_alert("Test", "Test", "INFO", "quality")
        system.create_alert("Test", "Test", "INFO", "maintenance")
        
        quality_alerts = system.get_alerts_by_source("quality")
        
        assert len(quality_alerts) > 0
        assert all(a['source'] == 'quality' for a in quality_alerts)
    
    def test_clear_all_alerts(self):
        """Test clearing all alerts"""
        system = AlertSystem()
        
        # Create some alerts
        system.create_alert("Test 1", "Test", "INFO", "system")
        system.create_alert("Test 2", "Test", "WARNING", "system")
        
        # Clear all
        count = system.clear_all_alerts()
        
        assert count > 0
        
        # Verify all are dismissed
        active_alerts = system.get_active_alerts()
        new_active = [a for a in active_alerts if a['title'] in ['Test 1', 'Test 2']]
        assert len(new_active) == 0
    
    def test_get_alert_stats(self):
        """Test getting alert statistics"""
        system = AlertSystem()
        
        stats = system.get_alert_stats()
        
        assert 'total_alerts' in stats
        assert 'active_alerts' in stats
        assert 'dismissed_alerts' in stats
        assert 'active_by_severity' in stats
        assert 'active_by_source' in stats
        
        assert stats['total_alerts'] >= stats['active_alerts']
    
    def test_invalid_severity(self):
        """Test error handling for invalid severity"""
        system = AlertSystem()
        
        with pytest.raises(ValueError):
            system.create_alert("Test", "Test", "INVALID", "system")
    
    def test_invalid_source(self):
        """Test error handling for invalid source"""
        system = AlertSystem()
        
        with pytest.raises(ValueError):
            system.create_alert("Test", "Test", "INFO", "invalid_source")
    
    def test_alert_sorting(self):
        """Test that alerts are sorted by severity"""
        system = AlertSystem()
        
        # Create alerts in mixed order
        system.create_alert("Info", "Test", "INFO", "system")
        system.create_alert("Critical", "Test", "CRITICAL", "system")
        system.create_alert("Warning", "Test", "WARNING", "system")
        
        active = system.get_active_alerts()
        
        # Should be sorted: CRITICAL, WARNING, INFO
        severities = [a['severity'] for a in active if a['title'] in ['Info', 'Critical', 'Warning']]
        expected_order = ['CRITICAL', 'WARNING', 'INFO']
        
        # Check that critical comes before warning, warning before info
        if 'CRITICAL' in severities and 'WARNING' in severities:
            assert severities.index('CRITICAL') < severities.index('WARNING')
        if 'WARNING' in severities and 'INFO' in severities:
            assert severities.index('WARNING') < severities.index('INFO')
