"""
Unit tests for Quality module (predictive_model and spc_analysis)
"""

import pytest
import pandas as pd
import numpy as np
from modules.quality.predictive_model import QualityPredictiveModel, create_demo_model


class TestQualityPredictiveModel:
    """Test cases for QualityPredictiveModel"""
    
    def test_model_initialization(self):
        """Test model can be initialized"""
        model = create_demo_model()
        assert model is not None
        assert model.model is not None
    
    def test_predict_defect_probability(self):
        """Test defect probability prediction"""
        model = create_demo_model()
        
        sensor_readings = {
            'air_temperature': 298.0,
            'process_temperature': 308.0,
            'rotational_speed': 1500.0,
            'torque': 40.0,
            'tool_wear': 100.0,
            'vibration': 0.5,
            'humidity': 60.0,
            'pressure': 1.0
        }
        
        result = model.predict_defect_probability(sensor_readings)
        
        assert result.defect_probability >= 0.0
        assert result.defect_probability <= 1.0
        assert result.risk_level in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        assert isinstance(result.is_defect_predicted, bool)
        assert isinstance(result.recommendations, list)
        assert len(result.recommendations) > 0
    
    def test_feature_contributions(self):
        """Test SHAP feature contributions"""
        model = create_demo_model()
        
        sensor_readings = {
            'air_temperature': 298.0,
            'process_temperature': 308.0,
            'rotational_speed': 1500.0,
            'torque': 40.0,
            'tool_wear': 100.0,
            'vibration': 0.5,
            'humidity': 60.0,
            'pressure': 1.0
        }
        
        result = model.predict_defect_probability(sensor_readings)
        
        assert len(result.feature_contributions) == 8
        for feature in model.feature_names:
            assert feature in result.feature_contributions
    
    def test_high_risk_prediction(self):
        """Test prediction with high-risk parameters"""
        model = create_demo_model()
        
        # High-risk parameters
        sensor_readings = {
            'air_temperature': 305.0,
            'process_temperature': 315.0,
            'rotational_speed': 1200.0,
            'torque': 65.0,
            'tool_wear': 230.0,
            'vibration': 0.9,
            'humidity': 75.0,
            'pressure': 1.1
        }
        
        result = model.predict_defect_probability(sensor_readings)
        
        # High-risk should have elevated probability
        assert result.risk_level in ['MEDIUM', 'HIGH', 'CRITICAL']
    
    def test_feature_importance(self):
        """Test feature importance calculation"""
        model = create_demo_model()
        importance = model.get_feature_importance()
        
        assert len(importance) == 8
        assert all(0 <= v <= 1 for v in importance.values())
        
        # Sum of importances should be approximately 1
        assert 0.95 <= sum(importance.values()) <= 1.05
    
    def test_training_with_synthetic_data(self):
        """Test model training with synthetic data"""
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
        
        y = pd.Series([0 if i < 50 else 1 for i in range(n_samples)])
        
        model = QualityPredictiveModel()
        metrics = model.train(X, y)
        
        assert 'accuracy' in metrics
        assert 'roc_auc' in metrics
        assert metrics['accuracy'] > 0
        assert metrics['roc_auc'] > 0
