#!/usr/bin/env python3
"""
System Verification Script for AI-ERP Quality Module
Run this script to verify all modules are working correctly
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_module_imports():
    """Test that all modules can be imported"""
    print("\n1. Testing Module Imports...")
    
    try:
        from modules.quality.predictive_model import QualityPredictiveModel
        from modules.quality.spc_analysis import SPCAnalyzer
        print("   ✓ Quality modules")
    except Exception as e:
        print(f"   ✗ Quality modules: {e}")
        return False
    
    try:
        from modules.maintenance.rul_model import RULModel
        from modules.maintenance.sensor_monitor import SensorMonitor
        print("   ✓ Maintenance modules")
    except Exception as e:
        print(f"   ✗ Maintenance modules: {e}")
        return False
    
    try:
        from modules.supplier.supplier_score import SupplierScorer
        from modules.supplier.procurement_advisor import ProcurementAdvisor
        print("   ✓ Supplier modules")
    except Exception as e:
        print(f"   ✗ Supplier modules: {e}")
        return False
    
    try:
        from modules.vision.visual_inspection import VisualInspector
        from modules.vision.anomaly_detector import AnomalyDetector
        print("   ✓ Vision modules")
    except Exception as e:
        print(f"   ✗ Vision modules: {e}")
        return False
    
    try:
        from modules.reporting.kpi_engine import KPIEngine
        from modules.reporting.alert_system import AlertSystem
        print("   ✓ Reporting modules")
    except Exception as e:
        print(f"   ✗ Reporting modules: {e}")
        return False
    
    return True


def test_api():
    """Test that API can be initialized"""
    print("\n2. Testing API...")
    
    try:
        from api.main import app
        routes = [r.path for r in app.routes if hasattr(r, 'path') and r.path.startswith('/api')]
        print(f"   ✓ API initialized with {len(routes)} endpoints")
        return True
    except Exception as e:
        print(f"   ✗ API initialization failed: {e}")
        return False


def test_core_functionality():
    """Test core functionality of each module"""
    print("\n3. Testing Core Functionality...")
    
    sensor_data = {
        'air_temperature': 298.0,
        'process_temperature': 308.0,
        'rotational_speed': 1500.0,
        'torque': 40.0,
        'tool_wear': 100.0,
        'vibration': 0.5,
        'humidity': 60.0,
        'pressure': 1.0
    }
    
    try:
        from modules.maintenance.rul_model import RULModel
        rul = RULModel()
        result = rul.predict(sensor_data)
        print(f"   ✓ RUL Prediction: {result['rul_hours']:.1f}h")
    except Exception as e:
        print(f"   ✗ RUL Prediction: {e}")
        return False
    
    try:
        from modules.maintenance.sensor_monitor import SensorMonitor
        monitor = SensorMonitor()
        machines = monitor.get_all_machines()
        print(f"   ✓ Sensor Monitor: {len(machines)} machines")
    except Exception as e:
        print(f"   ✗ Sensor Monitor: {e}")
        return False
    
    try:
        from modules.supplier.supplier_score import SupplierScorer
        scorer = SupplierScorer()
        result = scorer.score({
            'supplier_id': 'TEST-001',
            'quality_score': 0.85,
            'on_time_delivery_rate': 0.90,
            'defect_rate': 0.03,
            'price_competitiveness': 0.75,
            'response_time_days': 2.0,
            'years_of_partnership': 3.0
        })
        print(f"   ✓ Supplier Scoring: {result['overall_score']:.1f}")
    except Exception as e:
        print(f"   ✗ Supplier Scoring: {e}")
        return False
    
    try:
        from modules.reporting.kpi_engine import KPIEngine
        kpi = KPIEngine()
        snapshot = kpi.get_snapshot()
        print(f"   ✓ KPI Engine: OEE={snapshot['oee']:.1f}%")
    except Exception as e:
        print(f"   ✗ KPI Engine: {e}")
        return False
    
    try:
        from modules.reporting.alert_system import AlertSystem
        alerts = AlertSystem()
        active = alerts.get_active_alerts()
        print(f"   ✓ Alert System: {len(active)} alerts")
    except Exception as e:
        print(f"   ✗ Alert System: {e}")
        return False
    
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("AI-ERP QUALITY MODULE - SYSTEM VERIFICATION")
    print("=" * 60)
    
    tests = [
        test_module_imports,
        test_api,
        test_core_functionality
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    if all(results):
        print("RESULT: ✓ ALL TESTS PASSED")
        print("=" * 60)
        return 0
    else:
        print("RESULT: ✗ SOME TESTS FAILED")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
