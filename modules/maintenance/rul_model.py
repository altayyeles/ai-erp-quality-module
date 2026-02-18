"""
Remaining Useful Life (RUL) Prediction Model

This module implements a Random Forest-based RUL prediction system for
predictive maintenance, estimating equipment remaining useful life.

Key Features:
- Random Forest regression for RUL estimation
- Feature importance analysis
- Maintenance urgency classification (NORMAL/WARNING/CRITICAL)
- Model persistence with joblib
- Automatic synthetic training if no model exists
"""

import numpy as np
import pandas as pd
import joblib
import logging
from pathlib import Path
from typing import Dict, Optional, List
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

logger = logging.getLogger(__name__)


class RULModel:
    """
    Random Forest-based Remaining Useful Life prediction model.
    
    Predicts the remaining operational hours before maintenance is required
    based on sensor readings and operational parameters.
    """
    
    FEATURE_NAMES = [
        'air_temperature',
        'process_temperature',
        'rotational_speed',
        'torque',
        'tool_wear',
        'vibration',
        'humidity',
        'pressure'
    ]
    
    def __init__(self, model_path: Optional[Path] = None):
        """
        Initialize the RUL Model.
        
        Args:
            model_path: Path to load a pre-trained model from
        """
        self.model = None
        self.feature_names = self.FEATURE_NAMES
        self.model_path = model_path
        
        if model_path and model_path.exists():
            self.load_model(model_path)
        else:
            # Auto-train with synthetic data if no model exists
            logger.info("No pre-trained model found. Training with synthetic data...")
            self._train_synthetic_model()
    
    def train(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """
        Train the Random Forest model on RUL data.
        
        Args:
            X: Feature matrix (sensor readings)
            y: Target variable (RUL in hours)
            
        Returns:
            Dictionary containing training metrics
        """
        logger.info("Training RUL Model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train Random Forest regressor
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        
        metrics = {
            'mae': float(mean_absolute_error(y_test, y_pred)),
            'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred))),
            'r2': float(r2_score(y_test, y_pred)),
            'test_samples': len(y_test)
        }
        
        logger.info(f"✓ Model trained - MAE: {metrics['mae']:.2f}h, RMSE: {metrics['rmse']:.2f}h, R²: {metrics['r2']:.3f}")
        
        return metrics
    
    def predict(self, X: pd.DataFrame) -> Dict:
        """
        Predict Remaining Useful Life for given sensor readings.
        
        Args:
            X: DataFrame with sensor readings
            
        Returns:
            Dictionary with RUL prediction, urgency level, and maintenance schedule
        """
        if self.model is None:
            raise ValueError("Model not trained or loaded.")
        
        # Make prediction
        rul_hours = float(self.model.predict(X)[0])
        
        # Ensure non-negative RUL
        rul_hours = max(0, rul_hours)
        
        # Calculate maintenance urgency
        if rul_hours < 24:
            maintenance_urgency = "CRITICAL"
            days_to_maintenance = 0
        elif rul_hours < 72:
            maintenance_urgency = "WARNING"
            days_to_maintenance = int(rul_hours / 24)
        else:
            maintenance_urgency = "NORMAL"
            days_to_maintenance = int(rul_hours / 24)
        
        return {
            'rul_hours': round(rul_hours, 2),
            'maintenance_urgency': maintenance_urgency,
            'days_to_maintenance': days_to_maintenance,
            'estimated_failure_date': f"{days_to_maintenance} days from now"
        }
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance scores from the trained model.
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        if self.model is None:
            raise ValueError("Model not trained or loaded.")
        
        importance = self.model.feature_importances_
        return dict(zip(self.feature_names, [float(imp) for imp in importance]))
    
    def save_model(self, path: Path) -> None:
        """
        Save the trained model to disk.
        
        Args:
            path: Path where to save the model
        """
        if self.model is None:
            raise ValueError("No model to save. Train the model first.")
        
        path.parent.mkdir(parents=True, exist_ok=True)
        
        model_data = {
            'model': self.model,
            'feature_names': self.feature_names
        }
        
        joblib.dump(model_data, path)
        logger.info(f"✓ Model saved to {path}")
    
    def load_model(self, path: Path) -> None:
        """
        Load a trained model from disk.
        
        Args:
            path: Path to the saved model
        """
        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")
        
        model_data = joblib.load(path)
        self.model = model_data['model']
        self.feature_names = model_data['feature_names']
        
        logger.info(f"✓ Model loaded from {path}")
    
    def _train_synthetic_model(self) -> None:
        """Train model with synthetic data for demonstration purposes."""
        logger.info("Generating synthetic training data for RUL model...")
        
        np.random.seed(42)
        n_samples = 3000
        
        # Generate synthetic sensor data
        data = {
            'air_temperature': np.random.normal(298, 3, n_samples),
            'process_temperature': np.random.normal(308, 2, n_samples),
            'rotational_speed': np.random.normal(1500, 200, n_samples),
            'torque': np.random.normal(40, 10, n_samples),
            'tool_wear': np.random.uniform(0, 250, n_samples),
            'vibration': np.random.normal(0.5, 0.15, n_samples),
            'humidity': np.random.normal(60, 10, n_samples),
            'pressure': np.random.normal(1.0, 0.1, n_samples),
        }
        
        X = pd.DataFrame(data)
        
        # Generate synthetic RUL based on features (inverse relationship)
        # Higher tool wear, vibration, temperature -> lower RUL
        rul = (
            500  # Base RUL
            - (X['tool_wear'] * 1.5)  # Tool wear reduces RUL
            - (X['vibration'] - 0.5) * 200  # Vibration impact
            - (X['process_temperature'] - 308) * 10  # Temperature impact
            + np.random.normal(0, 20, n_samples)  # Random noise
        )
        
        # Clip RUL to reasonable range (0-500 hours)
        y = pd.Series(np.clip(rul, 0, 500))
        
        # Train the model
        self.train(X, y)
        
        logger.info("✓ Synthetic model training completed")


def create_demo_rul_model() -> RULModel:
    """
    Create and train a demo RUL model using synthetic data.
    
    Returns:
        Trained RULModel
    """
    model = RULModel()
    return model
