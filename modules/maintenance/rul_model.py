"""
Remaining Useful Life (RUL) Prediction Model
Random Forest-based predictive maintenance model for equipment lifecycle estimation

This module predicts the remaining useful life of machinery based on sensor readings
and provides maintenance urgency recommendations.
"""

import numpy as np
import pandas as pd
import joblib
import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime, timedelta

try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, r2_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not available. RUL model will use fallback mode.")

logger = logging.getLogger(__name__)


class RULModel:
    """
    Random Forest-based Remaining Useful Life prediction model.
    
    Predicts remaining operational hours before maintenance is required
    based on real-time sensor readings from manufacturing equipment.
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
        Initialize RUL Model.
        
        Args:
            model_path: Optional path to load pre-trained model
        """
        self.model = None
        self.feature_names = self.FEATURE_NAMES
        self.model_path = model_path or Path("models/rul_model.pkl")
        
        if self.model_path.exists():
            try:
                self.load_model(self.model_path)
            except Exception as e:
                logger.warning(f"Failed to load model from {self.model_path}: {e}")
                self._train_default_model()
        else:
            self._train_default_model()
    
    def train(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2) -> Dict[str, float]:
        """
        Train the Random Forest model on RUL data.
        
        Args:
            X: Feature matrix (sensor readings)
            y: Target variable (remaining useful life in hours)
            test_size: Proportion of data for testing
            
        Returns:
            Dictionary with training metrics
        """
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn not available. Cannot train model.")
            return {"error": "sklearn not available"}
        
        logger.info("Training RUL Model...")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        metrics = {
            'mae': float(mae),
            'r2_score': float(r2),
            'test_samples': len(y_test)
        }
        
        logger.info(f"✓ RUL Model trained - MAE: {mae:.2f} hours, R²: {r2:.3f}")
        
        return metrics
    
    def predict(self, sensor_data: Dict[str, float]) -> Dict:
        """
        Predict remaining useful life based on sensor readings.
        
        Args:
            sensor_data: Dictionary with sensor measurements
            
        Returns:
            Dictionary with RUL prediction, urgency level, and recommendations
        """
        features = self._prepare_features(sensor_data)
        X = pd.DataFrame([features], columns=self.feature_names)
        
        if self.model is None or not SKLEARN_AVAILABLE:
            # Fallback: rule-based RUL estimation
            rul_hours = self._fallback_rul_prediction(sensor_data)
        else:
            rul_hours = float(self.model.predict(X)[0])
        
        # Ensure RUL is positive
        rul_hours = max(0, rul_hours)
        
        # Calculate maintenance urgency
        urgency, days_to_maintenance = self._calculate_urgency(rul_hours)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(sensor_data, rul_hours, urgency)
        
        return {
            'rul_hours': round(rul_hours, 1),
            'rul_days': round(rul_hours / 24, 1),
            'maintenance_urgency': urgency,
            'days_to_maintenance': days_to_maintenance,
            'recommendations': recommendations,
            'sensor_health': self._assess_sensor_health(sensor_data)
        }
    
    def _prepare_features(self, sensor_data: Dict[str, float]) -> list:
        """Prepare feature vector from sensor data."""
        features = []
        for feature_name in self.feature_names:
            value = sensor_data.get(feature_name, 0.0)
            features.append(float(value))
        return features
    
    def _fallback_rul_prediction(self, sensor_data: Dict[str, float]) -> float:
        """
        Fallback RUL prediction using rule-based heuristics.
        Used when scikit-learn is not available.
        """
        # Base RUL starts at 500 hours
        rul = 500.0
        
        # Adjust based on sensor readings
        tool_wear = sensor_data.get('tool_wear', 0)
        vibration = sensor_data.get('vibration', 0.5)
        process_temp = sensor_data.get('process_temperature', 308)
        torque = sensor_data.get('torque', 40)
        
        # Tool wear impact (0-250 range)
        if tool_wear > 200:
            rul -= (tool_wear - 200) * 2
        elif tool_wear > 150:
            rul -= (tool_wear - 150) * 1
        
        # Vibration impact
        if vibration > 1.0:
            rul -= (vibration - 1.0) * 100
        elif vibration > 0.7:
            rul -= (vibration - 0.7) * 50
        
        # Temperature impact
        if process_temp > 315:
            rul -= (process_temp - 315) * 10
        elif process_temp > 310:
            rul -= (process_temp - 310) * 5
        
        # Torque impact
        if torque > 70:
            rul -= (torque - 70) * 5
        elif torque > 55:
            rul -= (torque - 55) * 2
        
        return max(24, rul)  # Minimum 24 hours RUL
    
    def _calculate_urgency(self, rul_hours: float) -> tuple:
        """Calculate maintenance urgency level."""
        days = rul_hours / 24
        
        if rul_hours < 48:  # Less than 2 days
            return "CRITICAL", int(days)
        elif rul_hours < 168:  # Less than 7 days
            return "WARNING", int(days)
        else:
            return "NORMAL", int(days)
    
    def _assess_sensor_health(self, sensor_data: Dict[str, float]) -> Dict[str, str]:
        """Assess health status of individual sensors."""
        health = {}
        
        # Temperature sensors
        air_temp = sensor_data.get('air_temperature', 298)
        health['air_temperature'] = 'GOOD' if 290 < air_temp < 305 else 'WARNING'
        
        process_temp = sensor_data.get('process_temperature', 308)
        health['process_temperature'] = 'GOOD' if 305 < process_temp < 312 else 'WARNING'
        
        # Mechanical sensors
        vibration = sensor_data.get('vibration', 0.5)
        health['vibration'] = 'GOOD' if vibration < 0.7 else 'WARNING' if vibration < 1.0 else 'CRITICAL'
        
        tool_wear = sensor_data.get('tool_wear', 100)
        health['tool_wear'] = 'GOOD' if tool_wear < 150 else 'WARNING' if tool_wear < 200 else 'CRITICAL'
        
        torque = sensor_data.get('torque', 40)
        health['torque'] = 'GOOD' if torque < 55 else 'WARNING' if torque < 70 else 'CRITICAL'
        
        return health
    
    def _generate_recommendations(
        self, 
        sensor_data: Dict[str, float], 
        rul_hours: float,
        urgency: str
    ) -> list:
        """Generate maintenance recommendations."""
        recommendations = []
        
        if urgency == "CRITICAL":
            recommendations.append("🚨 URGENT: Schedule immediate maintenance within 48 hours!")
        elif urgency == "WARNING":
            recommendations.append("⚠️ Plan maintenance within the next week")
        
        # Specific component recommendations
        tool_wear = sensor_data.get('tool_wear', 0)
        if tool_wear > 200:
            recommendations.append(f"🔧 Replace cutting tool immediately (wear: {tool_wear:.0f} min)")
        elif tool_wear > 150:
            recommendations.append(f"🔧 Schedule tool replacement soon (wear: {tool_wear:.0f} min)")
        
        vibration = sensor_data.get('vibration', 0)
        if vibration > 1.0:
            recommendations.append(f"⚠️ Excessive vibration detected ({vibration:.2f} mm/s) - Check alignment")
        
        process_temp = sensor_data.get('process_temperature', 308)
        if process_temp > 312:
            recommendations.append(f"🌡️ High process temperature ({process_temp:.1f}K) - Inspect cooling")
        
        torque = sensor_data.get('torque', 40)
        if torque > 70:
            recommendations.append(f"⚙️ High torque load ({torque:.1f} Nm) - Check for obstructions")
        
        if not recommendations:
            recommendations.append("✓ All systems operating normally")
        
        return recommendations
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from the trained model."""
        if self.model is None or not SKLEARN_AVAILABLE:
            return {}
        
        importance = self.model.feature_importances_
        return dict(zip(self.feature_names, importance))
    
    def save_model(self, path: Path) -> None:
        """Save trained model to disk."""
        if self.model is None:
            raise ValueError("No model to save")
        
        path.parent.mkdir(parents=True, exist_ok=True)
        
        model_data = {
            'model': self.model,
            'feature_names': self.feature_names
        }
        
        joblib.dump(model_data, path)
        logger.info(f"✓ RUL Model saved to {path}")
    
    def load_model(self, path: Path) -> None:
        """Load trained model from disk."""
        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")
        
        model_data = joblib.load(path)
        self.model = model_data['model']
        self.feature_names = model_data.get('feature_names', self.FEATURE_NAMES)
        
        logger.info(f"✓ RUL Model loaded from {path}")
    
    def _train_default_model(self) -> None:
        """Train a default model using synthetic data if sklearn is available."""
        if not SKLEARN_AVAILABLE:
            logger.info("sklearn not available, using fallback prediction mode")
            return
        
        logger.info("Training default RUL model with synthetic data...")
        
        # Generate synthetic training data
        np.random.seed(42)
        n_samples = 3000
        
        X_data = {
            'air_temperature': np.random.normal(298, 3, n_samples),
            'process_temperature': np.random.normal(308, 2, n_samples),
            'rotational_speed': np.random.normal(1500, 200, n_samples),
            'torque': np.random.normal(40, 12, n_samples),
            'tool_wear': np.random.uniform(0, 250, n_samples),
            'vibration': np.random.gamma(2, 0.25, n_samples),
            'humidity': np.random.normal(60, 10, n_samples),
            'pressure': np.random.normal(1.0, 0.1, n_samples),
        }
        
        X = pd.DataFrame(X_data)
        
        # Generate target RUL based on conditions
        rul = 500 - X['tool_wear'] * 1.5 - (X['vibration'] - 0.5) * 100
        rul -= np.maximum(0, X['process_temperature'] - 310) * 10
        rul -= np.maximum(0, X['torque'] - 55) * 3
        rul = np.maximum(24, rul)  # Minimum 24 hours
        rul += np.random.normal(0, 20, n_samples)  # Add noise
        
        y = pd.Series(rul)
        
        self.train(X, y)
        
        logger.info("✓ Default RUL model trained successfully")
