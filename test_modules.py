"""
Simple test script to verify all modules can be imported
"""

import sys

def test_imports():
    """Test that all modules can be imported"""
    print("Testing module imports...")
    
    tests = []
    
    # Test API routes
    try:
        from api.routes import quality, maintenance, supplier, vision, dashboard
        tests.append(("API Routes", True, ""))
    except Exception as e:
        tests.append(("API Routes", False, str(e)))
    
    # Test Quality module
    try:
        from modules.quality.predictive_model import QualityPredictiveModel
        from modules.quality.spc_analysis import SPCAnalyzer
        tests.append(("Quality Module", True, ""))
    except Exception as e:
        tests.append(("Quality Module", False, str(e)))
    
    # Test Maintenance module
    try:
        from modules.maintenance.rul_model import RULModel
        from modules.maintenance.sensor_monitor import SensorMonitor
        tests.append(("Maintenance Module", True, ""))
    except Exception as e:
        tests.append(("Maintenance Module", False, str(e)))
    
    # Test Supplier module
    try:
        from modules.supplier.supplier_score import SupplierScorer
        from modules.supplier.procurement_advisor import ProcurementAdvisor
        tests.append(("Supplier Module", True, ""))
    except Exception as e:
        tests.append(("Supplier Module", False, str(e)))
    
    # Test Vision module
    try:
        from modules.vision.visual_inspection import VisualInspector
        from modules.vision.anomaly_detector import AnomalyDetector
        tests.append(("Vision Module", True, ""))
    except Exception as e:
        tests.append(("Vision Module", False, str(e)))
    
    # Test Reporting module
    try:
        from modules.reporting.kpi_engine import KPIEngine
        from modules.reporting.alert_system import AlertSystem
        tests.append(("Reporting Module", True, ""))
    except Exception as e:
        tests.append(("Reporting Module", False, str(e)))
    
    # Print results
    print("\n" + "="*60)
    print("MODULE IMPORT TEST RESULTS")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for module, success, error in tests:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status:8} | {module:25}")
        if not success:
            print(f"         | Error: {error}")
            failed += 1
        else:
            passed += 1
    
    print("="*60)
    print(f"Total: {len(tests)} | Passed: {passed} | Failed: {failed}")
    print("="*60)
    
    return failed == 0

def test_basic_functionality():
    """Test basic functionality of key modules"""
    print("\n\nTesting basic functionality...")
    
    try:
        # Test SensorMonitor
        from modules.maintenance.sensor_monitor import SensorMonitor
        monitor = SensorMonitor()
        machines = monitor.get_all_machines()
        print(f"✓ SensorMonitor: Retrieved {len(machines)} machines")
        
        # Test AlertSystem
        from modules.reporting.alert_system import AlertSystem
        alert_system = AlertSystem()
        alerts = alert_system.get_active_alerts()
        print(f"✓ AlertSystem: Retrieved {len(alerts)} active alerts")
        
        # Test SupplierScorer
        from modules.supplier.supplier_score import SupplierScorer
        scorer = SupplierScorer()
        test_supplier = {
            'supplier_id': 'TEST-001',
            'on_time_delivery_rate': 0.9,
            'quality_score': 0.85,
            'price_competitiveness': 0.75,
            'defect_rate': 0.03,
            'response_time_days': 2.0,
            'years_of_partnership': 3.0
        }
        result = scorer.score(test_supplier)
        print(f"✓ SupplierScorer: Scored supplier with {result['overall_score']:.1f}/100")
        
        print("\n✓ All basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Functionality test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("AI-ERP Quality Module - Module Test Suite")
    print("="*60)
    
    import_success = test_imports()
    functionality_success = test_basic_functionality()
    
    if import_success and functionality_success:
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED")
        print("="*60)
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("✗ SOME TESTS FAILED")
        print("="*60)
        sys.exit(1)
