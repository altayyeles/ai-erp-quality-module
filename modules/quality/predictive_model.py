"""
Predictive Quality Model using XGBoost and SHAP

This module implements an AI-powered quality prediction system that forecasts
defect probability based on sensor readings and process parameters.

Key Features:
- XGBoost classifier for defect prediction
- SHAP (SHapley Additive exPlanations) for model interpretability
- Model training, saving, and loading capabilities
- Real-time prediction with feature importance
"""

import numpy as np
import pandas as pd
import joblib
import logging
from pathlib import Path
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass

try:
    import xgboost as xgb
    import shap
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
    HAS_ML_LIBS = True
except ImportError as e:
    xgb = None
    shap = None
    train_test_split = None
    classification_report = None
    roc_auc_score = None
    confusion_matrix = None
    HAS_ML_LIBS = False
    import warnings
    warnings.warn(f"ML libraries not available: {e}. Quality prediction will be limited.")

logger = logging.getLogger(__name__)


@dataclass
class PredictionResult:
    """Container for prediction results"""
    defect_probability: float
    is_defect_predicted: bool
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    feature_contributions: Dict[str, float]
    recommendations: List[str]


class QualityPredictiveModel:
    """
    XGBoost-based quality prediction model with SHAP explainability.
    
    This model predicts the probability of defects based on sensor readings
    and provides interpretable explanations for its predictions.
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
        Initialize the Quality Predictive Model.
        
        Args:
            model_path: Path to load a pre-trained model from
        """
        self.model = None
        self.explainer = None
        self.feature_names = self.FEATURE_NAMES
        self.model_path = model_path
        
        if model_path and model_path.exists():
            self.load_model(model_path)
    
    def train(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Dict[str, float]:
        """
        Train the XGBoost model on quality data.
        
        Args:
            X: Feature matrix (sensor readings)
            y: Target variable (0: no defect, 1: defect)
            test_size: Proportion of data for testing
            random_state: Random seed for reproducibility
            
        Returns:
            Dictionary containing training metrics
        """
        if not HAS_ML_LIBS or xgb is None or shap is None:
            raise ImportError(
                "Required ML libraries (xgboost, shap, scikit-learn) not available. "
                "Install them with: pip install xgboost shap scikit-learn"
            )
        
        logger.info("Training Quality Predictive Model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # Train XGBoost classifier
        self.model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            objective='binary:logistic',
            random_state=random_state,
            eval_metric='auc'
        )
        
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )
        
        # Create SHAP explainer (with fallback for version incompatibility)
        try:
            self.explainer = shap.TreeExplainer(self.model)
        except (ValueError, TypeError) as e:
            logger.warning(
                f"Failed to create SHAP explainer due to version incompatibility: {e}. "
                "Predictions will work but without feature contribution explanations."
            )
            self.explainer = None
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        metrics = {
            'accuracy': float((y_pred == y_test).mean()),
            'roc_auc': float(roc_auc_score(y_test, y_pred_proba)),
            'test_samples': len(y_test),
            'defect_rate': float(y_test.mean())
        }
        
        logger.info(f"✓ Model trained - Accuracy: {metrics['accuracy']:.3f}, ROC-AUC: {metrics['roc_auc']:.3f}")
        
        return metrics
    
    def predict_defect_probability(
        self,
        sensor_readings: Dict[str, float]
    ) -> PredictionResult:
        """
        Predict defect probability for given sensor readings.
        
        Args:
            sensor_readings: Dictionary with sensor measurements
                Expected keys: air_temperature, process_temperature, rotational_speed,
                             torque, tool_wear, vibration, humidity, pressure
        
        Returns:
            PredictionResult with probability, risk level, and explanations
        """
        if self.model is None:
            raise ValueError("Model not trained or loaded. Call train() or load_model() first.")
        
        # Prepare features
        features = self._prepare_features(sensor_readings)
        X = pd.DataFrame([features], columns=self.feature_names)
        
        # Predict probability
        probability = float(self.model.predict_proba(X)[0, 1])
        is_defect = probability > 0.5
        
        # Calculate SHAP values for explanation (if explainer is available)
        if self.explainer is not None:
            shap_values = self.explainer.shap_values(X)
            feature_contributions = dict(zip(
                self.feature_names,
                shap_values[0]
            ))
        else:
            # Fallback: use zero contributions if SHAP is not available
            feature_contributions = {feature: 0.0 for feature in self.feature_names}
        
        # Determine risk level
        risk_level = self._calculate_risk_level(probability)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            sensor_readings, feature_contributions, probability
        )
        
        return PredictionResult(
            defect_probability=probability,
            is_defect_predicted=is_defect,
            risk_level=risk_level,
            feature_contributions=feature_contributions,
            recommendations=recommendations
        )
    
    def _prepare_features(self, sensor_readings: Dict[str, float]) -> List[float]:
        """Prepare feature vector from sensor readings."""
        features = []
        for feature_name in self.feature_names:
            value = sensor_readings.get(feature_name, 0.0)
            features.append(float(value))
        return features
    
    def _calculate_risk_level(self, probability: float) -> str:
        """Calculate risk level based on defect probability."""
        if probability < 0.25:
            return "LOW"
        elif probability < 0.50:
            return "MEDIUM"
        elif probability < 0.75:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def _generate_recommendations(
        self,
        sensor_readings: Dict[str, float],
        feature_contributions: Dict[str, float],
        probability: float
    ) -> List[str]:
        """Generate actionable recommendations based on predictions."""
        recommendations = []
        
        # Get top contributing features (absolute SHAP values)
        sorted_contributions = sorted(
            feature_contributions.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        # Generate specific recommendations based on top contributors
        for feature, contribution in sorted_contributions[:3]:
            if abs(contribution) > 0.1:  # Significant contribution
                value = sensor_readings.get(feature, 0)
                
                if feature == 'tool_wear' and value > 200:
                    recommendations.append(
                        f"⚠️ Tool wear is high ({value:.0f} min). Schedule tool replacement."
                    )
                elif feature == 'process_temperature' and value > 310:
                    recommendations.append(
                        f"⚠️ Process temperature is elevated ({value:.1f}K). Check cooling system."
                    )
                elif feature == 'vibration' and value > 0.8:
                    recommendations.append(
                        f"⚠️ Excessive vibration detected ({value:.2f} mm/s). Inspect machine alignment."
                    )
                elif feature == 'torque' and value > 60:
                    recommendations.append(
                        f"⚠️ High torque detected ({value:.1f} Nm). Check for mechanical resistance."
                    )
                elif feature == 'rotational_speed' and value < 1200:
                    recommendations.append(
                        f"⚠️ Low rotational speed ({value:.0f} rpm). Verify power supply."
                    )
        
        # General recommendations based on risk level
        if probability > 0.75:
            recommendations.insert(0, "🚨 CRITICAL: Stop production and inspect machine immediately!")
        elif probability > 0.50:
            recommendations.insert(0, "⚠️ HIGH RISK: Schedule immediate inspection after current batch.")
        elif probability > 0.25:
            recommendations.insert(0, "⚠️ MEDIUM RISK: Monitor closely and schedule preventive maintenance.")
        
        if not recommendations:
            recommendations.append("✓ All parameters within normal range. Continue monitoring.")
        
        return recommendations
    
    def save_model(self, path: Path) -> None:
        """Save the trained model to disk."""
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
        """Load a trained model from disk."""
        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")
        
        model_data = joblib.load(path)
        self.model = model_data['model']
        self.feature_names = model_data['feature_names']
        
        # Recreate SHAP explainer (with fallback for version incompatibility)
        if self.model is not None:
            try:
                self.explainer = shap.TreeExplainer(self.model)
            except (ValueError, TypeError) as e:
                logger.warning(
                    f"Failed to create SHAP explainer due to version incompatibility: {e}. "
                    "Predictions will work but without feature contribution explanations."
                )
                self.explainer = None
        
        logger.info(f"✓ Model loaded from {path}")
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores from the model."""
        if self.model is None:
            raise ValueError("Model not trained or loaded.")
        
        importance = self.model.feature_importances_
        return dict(zip(self.feature_names, importance))


def create_demo_model() -> QualityPredictiveModel:
    """
    Create and train a demo model using synthetic data.
    
    Returns:
        Trained QualityPredictiveModel
    """
    if not HAS_ML_LIBS or xgb is None or shap is None:
        raise ImportError(
            "Required ML libraries (xgboost, shap, scikit-learn) not available. "
            "Install them with: pip install xgboost shap scikit-learn"
        )
    
    logger.info("Creating demo quality model with synthetic data...")
    
    # Generate synthetic training data
    np.random.seed(42)
    n_samples = 5000
    
    # Normal operation data
    normal_data = {
        'air_temperature': np.random.normal(298, 2, n_samples // 2),
        'process_temperature': np.random.normal(308, 1.5, n_samples // 2),
        'rotational_speed': np.random.normal(1500, 150, n_samples // 2),
        'torque': np.random.normal(40, 8, n_samples // 2),
        'tool_wear': np.random.uniform(0, 180, n_samples // 2),
        'vibration': np.random.normal(0.5, 0.1, n_samples // 2),
        'humidity': np.random.normal(60, 8, n_samples // 2),
        'pressure': np.random.normal(1.0, 0.08, n_samples // 2),
    }
    
    # Defective operation data (with anomalies)
    defect_data = {
        'air_temperature': np.random.normal(298, 3, n_samples // 2),
        'process_temperature': np.random.normal(312, 2, n_samples // 2),
        'rotational_speed': np.random.normal(1300, 200, n_samples // 2),
        'torque': np.random.normal(52, 12, n_samples // 2),
        'tool_wear': np.random.uniform(180, 250, n_samples // 2),
        'vibration': np.random.normal(0.75, 0.2, n_samples // 2),
        'humidity': np.random.normal(65, 12, n_samples // 2),
        'pressure': np.random.normal(1.05, 0.12, n_samples // 2),
    }
    
    # Combine data
    X_normal = pd.DataFrame(normal_data)
    X_defect = pd.DataFrame(defect_data)
    X = pd.concat([X_normal, X_defect], ignore_index=True)
    
    y_normal = pd.Series([0] * (n_samples // 2))
    y_defect = pd.Series([1] * (n_samples // 2))
    y = pd.concat([y_normal, y_defect], ignore_index=True)
    
    # Shuffle
    shuffle_idx = np.random.permutation(len(X))
    X = X.iloc[shuffle_idx].reset_index(drop=True)
    y = y.iloc[shuffle_idx].reset_index(drop=True)
    
    # Train model
    model = QualityPredictiveModel()
    model.train(X, y)
    
    logger.info("✓ Demo model created successfully")
    return model
