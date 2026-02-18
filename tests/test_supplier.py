"""
Unit tests for Supplier module (supplier_score and procurement_advisor)
"""

import pytest
from modules.supplier.supplier_score import SupplierScorer
from modules.supplier.procurement_advisor import ProcurementAdvisor


class TestSupplierScorer:
    """Test cases for SupplierScorer"""
    
    def test_scorer_initialization(self):
        """Test supplier scorer can be initialized"""
        scorer = SupplierScorer()
        assert scorer is not None
    
    def test_score_calculation(self):
        """Test supplier score calculation"""
        scorer = SupplierScorer()
        
        supplier_data = {
            'supplier_id': 'SUP-001',
            'on_time_delivery_rate': 0.90,
            'quality_score': 0.85,
            'price_competitiveness': 0.75,
            'defect_rate': 0.03,
            'response_time_days': 2.0,
            'years_of_partnership': 3.0
        }
        
        result = scorer.score(supplier_data)
        
        assert 'overall_score' in result
        assert 'risk_level' in result
        assert 'category' in result
        assert 'breakdown' in result
        assert 'recommendations' in result
        
        assert 0 <= result['overall_score'] <= 100
        assert result['risk_level'] in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        assert result['category'] in ['PREFERRED', 'APPROVED', 'CONDITIONAL', 'DISQUALIFIED']
    
    def test_high_performance_supplier(self):
        """Test scoring for high-performance supplier"""
        scorer = SupplierScorer()
        
        supplier_data = {
            'supplier_id': 'SUP-EXCELLENT',
            'on_time_delivery_rate': 0.98,
            'quality_score': 0.95,
            'price_competitiveness': 0.90,
            'defect_rate': 0.01,
            'response_time_days': 1.0,
            'years_of_partnership': 5.0
        }
        
        result = scorer.score(supplier_data)
        
        assert result['overall_score'] >= 80
        assert result['risk_level'] in ['LOW', 'MEDIUM']
        assert result['category'] in ['PREFERRED', 'APPROVED']
    
    def test_poor_performance_supplier(self):
        """Test scoring for poor-performance supplier"""
        scorer = SupplierScorer()
        
        supplier_data = {
            'supplier_id': 'SUP-POOR',
            'on_time_delivery_rate': 0.60,
            'quality_score': 0.50,
            'price_competitiveness': 0.40,
            'defect_rate': 0.12,
            'response_time_days': 8.0,
            'years_of_partnership': 1.0
        }
        
        result = scorer.score(supplier_data)
        
        assert result['overall_score'] < 60
        assert result['risk_level'] in ['HIGH', 'CRITICAL']
        assert result['category'] in ['CONDITIONAL', 'DISQUALIFIED']
    
    def test_breakdown_components(self):
        """Test score breakdown contains all components"""
        scorer = SupplierScorer()
        
        supplier_data = {
            'supplier_id': 'SUP-001',
            'on_time_delivery_rate': 0.90,
            'quality_score': 0.85,
            'price_competitiveness': 0.75,
            'defect_rate': 0.03,
            'response_time_days': 2.0,
            'years_of_partnership': 3.0
        }
        
        result = scorer.score(supplier_data)
        breakdown = result['breakdown']
        
        assert 'quality_score' in breakdown
        assert 'on_time_delivery_rate' in breakdown
        assert 'defect_rate' in breakdown
        assert 'price_competitiveness' in breakdown
        assert 'response_time_days' in breakdown
        
        # All components should be in 0-100 range
        for score in breakdown.values():
            assert 0 <= score <= 100
    
    def test_recommendations_generated(self):
        """Test that recommendations are generated"""
        scorer = SupplierScorer()
        
        supplier_data = {
            'supplier_id': 'SUP-001',
            'on_time_delivery_rate': 0.90,
            'quality_score': 0.85,
            'price_competitiveness': 0.75,
            'defect_rate': 0.03,
            'response_time_days': 2.0,
            'years_of_partnership': 3.0
        }
        
        result = scorer.score(supplier_data)
        
        assert isinstance(result['recommendations'], list)
        assert len(result['recommendations']) > 0


class TestProcurementAdvisor:
    """Test cases for ProcurementAdvisor"""
    
    def test_advisor_initialization(self):
        """Test procurement advisor can be initialized"""
        advisor = ProcurementAdvisor()
        assert advisor is not None
    
    def test_advise(self):
        """Test procurement advice generation"""
        advisor = ProcurementAdvisor()
        
        supplier_data = {
            'supplier_id': 'SUP-001',
            'on_time_delivery_rate': 0.90,
            'quality_score': 0.85,
            'price_competitiveness': 0.75,
            'defect_rate': 0.03,
            'response_time_days': 2.0,
            'years_of_partnership': 3.0
        }
        
        result = advisor.advise(supplier_data)
        
        assert 'action' in result
        assert 'confidence' in result
        assert 'reasoning' in result
        assert 'risk_factors' in result
        assert 'opportunities' in result
        assert 'suggested_order_volume' in result
        
        assert result['action'] in ['RECOMMEND', 'MONITOR', 'REVIEW', 'REJECT']
        assert 0.0 <= result['confidence'] <= 1.0
        assert result['suggested_order_volume'] in ['NONE', 'LOW', 'MEDIUM', 'HIGH']
    
    def test_recommend_action(self):
        """Test RECOMMEND action for good supplier"""
        advisor = ProcurementAdvisor()
        
        supplier_data = {
            'supplier_id': 'SUP-GOOD',
            'on_time_delivery_rate': 0.95,
            'quality_score': 0.90,
            'price_competitiveness': 0.85,
            'defect_rate': 0.01,
            'response_time_days': 1.5,
            'years_of_partnership': 5.0
        }
        
        result = advisor.advise(supplier_data)
        
        assert result['action'] in ['RECOMMEND', 'MONITOR']
        assert result['confidence'] >= 0.6
    
    def test_reject_action(self):
        """Test REJECT action for poor supplier"""
        advisor = ProcurementAdvisor()
        
        supplier_data = {
            'supplier_id': 'SUP-BAD',
            'on_time_delivery_rate': 0.60,
            'quality_score': 0.40,
            'price_competitiveness': 0.50,
            'defect_rate': 0.15,
            'response_time_days': 10.0,
            'years_of_partnership': 0.5
        }
        
        result = advisor.advise(supplier_data)
        
        assert result['action'] in ['REJECT', 'REVIEW']
        assert len(result['risk_factors']) > 0
    
    def test_risk_factors_identification(self):
        """Test risk factors are properly identified"""
        advisor = ProcurementAdvisor()
        
        supplier_data = {
            'supplier_id': 'SUP-RISKY',
            'on_time_delivery_rate': 0.70,
            'quality_score': 0.65,
            'price_competitiveness': 0.60,
            'defect_rate': 0.08,
            'response_time_days': 7.0,
            'years_of_partnership': 0.5
        }
        
        result = advisor.advise(supplier_data)
        
        assert isinstance(result['risk_factors'], list)
        # Should identify multiple risks
        assert len(result['risk_factors']) > 0
    
    def test_opportunities_identification(self):
        """Test opportunities are properly identified"""
        advisor = ProcurementAdvisor()
        
        supplier_data = {
            'supplier_id': 'SUP-OPPORTUNITY',
            'on_time_delivery_rate': 0.97,
            'quality_score': 0.92,
            'price_competitiveness': 0.85,
            'defect_rate': 0.005,
            'response_time_days': 1.0,
            'years_of_partnership': 6.0
        }
        
        result = advisor.advise(supplier_data)
        
        assert isinstance(result['opportunities'], list)
        # Should identify multiple opportunities
        assert len(result['opportunities']) > 0
