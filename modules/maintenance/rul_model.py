"""
RUL (Remaining Useful Life) Model using Random Forest
Predicts maintenance requirements based on sensor readings
"""

import numpy as np
import pandas as pd
import joblib
import logging
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime, timedelta

try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)


class RULModel:
    """
    Random Forest-based Remaining Useful Life (RUL) prediction model.
    
    Predicts how many hours/days of operation remain before maintenance is required.
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
            model_path: Path to pre-trained model (optional)
        """
        self.model = None
        self.feature_names = self.FEATURE_NAMES
        self.model_path = model_path or Path("models/rul_model.pkl")
        
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn not available. Using fallback predictions.")
            return
        
        # Try to load existing model, or train if not exists
        if self.model_path.exists():
            try:
                self.load_model(self.model_path)
            except Exception as e:
                logger.warning(f"Failed to load model: {e}. Training new model...")
                self._train_with_synthetic_data()
        else:
            self._train_with_synthetic_data()
    
    def train(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """
        Train the Random Forest model on RUL data.
        
        Args:
            X: Feature matrix (sensor readings)
            y: Target variable (RUL in hours)
            
        Returns:
            Dictionary containing training metrics
        """
        if not SKLEARN_AVAILABLE:
            logger.error("scikit-learn not available")
            return {"error": "scikit-learn not installed"}
        
        logger.info("Training RUL Model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train Random Forest
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
        
        logger.info(f"✓ RUL Model trained - MAE: {metrics['mae']:.1f}h, RMSE: {metrics['rmse']:.1f}h, R²: {metrics['r2']:.3f}")
        
        return metrics
    
    def predict(self, sensor_data: Dict[str, float]) -> Dict:
        """
        Predict RUL and maintenance urgency.
        
        Args:
            sensor_data: Dictionary with sensor measurements
            
        Returns:
            Dictionary with RUL prediction, urgency level, and recommendations
        """
        # Prepare features
        features = self._prepare_features(sensor_data)
        
        if self.model is None or not SKLEARN_AVAILABLE:
            # Fallback to rule-based estimation
            return self._fallback_predict(sensor_data)
        
        X = pd.DataFrame([features], columns=self.feature_names)
        rul_hours = float(self.model.predict(X)[0])
        
        # Ensure RUL is non-negative
        rul_hours = max(0, rul_hours)
        
        # Calculate days to maintenance
        days_to_maintenance = rul_hours / 24.0
        
        # Determine urgency level
        if days_to_maintenance < 3:
            urgency = "CRITICAL"
        elif days_to_maintenance < 7:
            urgency = "WARNING"
        else:
            urgency = "NORMAL"
        
        # Generate recommendations
        recommendations = self._generate_recommendations(sensor_data, days_to_maintenance, urgency)
        
        return {
            "rul_hours": round(rul_hours, 1),
            "days_to_maintenance": round(days_to_maintenance, 1),
            "maintenance_urgency": urgency,
            "recommendations": recommendations,
            "predicted_maintenance_date": (datetime.now() + timedelta(hours=rul_hours)).isoformat()
        }
    
    def _fallback_predict(self, sensor_data: Dict[str, float]) -> Dict:
        """Fallback prediction when model is not available."""
        # Rule-based RUL estimation
        tool_wear = sensor_data.get('tool_wear', 100)
        vibration = sensor_data.get('vibration', 0.5)
        temperature = sensor_data.get('process_temperature', 308)
        
        # Simple heuristic
        base_rul = 720  # Base 30 days in hours
        
        # Reduce RUL based on wear factors
        wear_penalty = (tool_wear / 250) * 300  # Up to 300 hours penalty
        vibration_penalty = max(0, (vibration - 0.5) / 1.0) * 200  # Up to 200 hours
        temp_penalty = max(0, (temperature - 310) / 10) * 150  # Up to 150 hours
        
        rul_hours = max(24, base_rul - wear_penalty - vibration_penalty - temp_penalty)
        days_to_maintenance = rul_hours / 24.0
        
        if days_to_maintenance < 3:
            urgency = "CRITICAL"
        elif days_to_maintenance < 7:
            urgency = "WARNING"
        else:
            urgency = "NORMAL"
        
        recommendations = self._generate_recommendations(sensor_data, days_to_maintenance, urgency)
        
        return {
            "rul_hours": round(rul_hours, 1),
            "days_to_maintenance": round(days_to_maintenance, 1),
            "maintenance_urgency": urgency,
            "recommendations": recommendations,
            "predicted_maintenance_date": (datetime.now() + timedelta(hours=rul_hours)).isoformat(),
            "note": "Using fallback estimation (model not available)"
        }
    
    def _generate_recommendations(
        self,
        sensor_data: Dict[str, float],
        days_to_maintenance: float,
        urgency: str
    ) -> List[str]:
        """Generate maintenance recommendations."""
        recommendations = []
        
        tool_wear = sensor_data.get('tool_wear', 100)
        vibration = sensor_data.get('vibration', 0.5)
        temperature = sensor_data.get('process_temperature', 308)
        torque = sensor_data.get('torque', 40)
        
        if urgency == "CRITICAL":
            recommendations.append("🚨 CRITICAL: Schedule immediate maintenance within 48 hours!")
        elif urgency == "WARNING":
            recommendations.append("⚠️ WARNING: Schedule maintenance within the next week.")
        
        if tool_wear > 200:
            recommendations.append(f"🔧 Tool wear is high ({tool_wear:.0f} min). Replace cutting tools soon.")
        
        if vibration > 0.8:
            recommendations.append(f"⚡ Excessive vibration ({vibration:.2f} mm/s). Check machine balance and bearings.")
        
        if temperature > 312:
            recommendations.append(f"🌡️ Process temperature elevated ({temperature:.1f}K). Inspect cooling system.")
        
        if torque > 55:
            recommendations.append(f"⚙️ High torque detected ({torque:.1f} Nm). Check for mechanical resistance.")
        
        if not recommendations or urgency == "NORMAL":
            recommendations.append("✓ Machine operating normally. Continue routine monitoring.")
        
        return recommendations
    
    def _prepare_features(self, sensor_data: Dict[str, float]) -> List[float]:
        """Prepare feature vector from sensor readings."""
        features = []
        for feature_name in self.feature_names:
            value = sensor_data.get(feature_name, 0.0)
            features.append(float(value))
        return features
    
    def _train_with_synthetic_data(self):
        """Train model with synthetic data if no training data available."""
        if not SKLEARN_AVAILABLE:
            return
        
        logger.info("Training RUL model with synthetic data...")
        
        np.random.seed(42)
        n_samples = 3000
        
        # Generate synthetic data
        # Normal operation -> longer RUL
        tool_wear = np.random.uniform(0, 250, n_samples)
        vibration = np.random.normal(0.5, 0.2, n_samples)
        process_temp = np.random.normal(308, 3, n_samples)
        air_temp = np.random.normal(298, 2, n_samples)
        rot_speed = np.random.normal(1500, 150, n_samples)
        torque = np.random.normal(40, 10, n_samples)
        humidity = np.random.normal(60, 10, n_samples)
        pressure = np.random.normal(1.0, 0.1, n_samples)
        
        # RUL calculation (heuristic for training)
        rul = 720 - (tool_wear / 250 * 400) - np.maximum(0, (vibration - 0.5) * 300) - np.maximum(0, (process_temp - 310) * 20)
        rul = np.maximum(24, rul)  # Minimum 24 hours
        rul += np.random.normal(0, 50, n_samples)  # Add noise
        
        X = pd.DataFrame({
            'air_temperature': air_temp,
            'process_temperature': process_temp,
            'rotational_speed': rot_speed,
            'torque': torque,
            'tool_wear': tool_wear,
            'vibration': vibration,
            'humidity': humidity,
            'pressure': pressure
        })
        
        y = pd.Series(rul)
        
        # Train
        self.train(X, y)
        
        # Save model
        try:
            self.save_model(self.model_path)
        except Exception as e:
            logger.warning(f"Failed to save model: {e}")
    
    def save_model(self, path: Path) -> None:
        """Save the trained model to disk."""
        if self.model is None:
            raise ValueError("No model to save.")
        
        path.parent.mkdir(parents=True, exist_ok=True)
        
        model_data = {
            'model': self.model,
            'feature_names': self.feature_names
        }
        
        joblib.dump(model_data, path)
        logger.info(f"✓ RUL Model saved to {path}")
    
    def load_model(self, path: Path) -> None:
        """Load a trained model from disk."""
        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")
        
        model_data = joblib.load(path)
        self.model = model_data['model']
        self.feature_names = model_data.get('feature_names', self.FEATURE_NAMES)
        
        logger.info(f"✓ RUL Model loaded from {path}")
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores from the model."""
        if self.model is None:
            raise ValueError("Model not trained or loaded.")
        
        if not SKLEARN_AVAILABLE:
            return {}
        
        importance = self.model.feature_importances_
        return dict(zip(self.feature_names, [float(x) for x in importance]))
