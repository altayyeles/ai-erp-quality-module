"""
Supplier Risk Scoring System
Uses weighted scoring with K-Means clustering and IsolationForest anomaly detection
"""

import logging
from typing import Dict, List, Optional
import numpy as np

try:
    from sklearn.cluster import KMeans
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)


class SupplierScorer:
    """
    Supplier risk scoring system with ML-based categorization.
    
    Uses weighted scoring approach with the following weights:
    - Quality Score: 30%
    - On-Time Delivery: 25%
    - Defect Rate: 20%
    - Price Competitiveness: 15%
    - Response Time: 10%
    """
    
    # Scoring weights
    WEIGHTS = {
        'quality_score': 0.30,
        'on_time_delivery_rate': 0.25,
        'defect_rate': 0.20,
        'price_competitiveness': 0.15,
        'response_time_days': 0.10
    }
    
    def __init__(self):
        """Initialize supplier scorer."""
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
    
    def score(self, supplier_data: Dict) -> Dict:
        """
        Score a supplier based on performance metrics.
        
        Args:
            supplier_data: Dictionary with supplier metrics
                - supplier_id: str
                - on_time_delivery_rate: float (0.0-1.0)
                - quality_score: float (0.0-1.0)
                - price_competitiveness: float (0.0-1.0)
                - defect_rate: float (0.0-1.0)
                - response_time_days: float
                - years_of_partnership: float
                
        Returns:
            Dictionary with overall score, risk level, category, breakdown, and recommendations
        """
        # Extract and validate metrics
        quality_score = float(supplier_data.get('quality_score', 0.85))
        on_time_delivery = float(supplier_data.get('on_time_delivery_rate', 0.90))
        price_comp = float(supplier_data.get('price_competitiveness', 0.75))
        defect_rate = float(supplier_data.get('defect_rate', 0.03))
        response_time = float(supplier_data.get('response_time_days', 2.0))
        years_partnership = float(supplier_data.get('years_of_partnership', 3.0))
        
        # Calculate individual component scores (0-100 scale)
        quality_component = quality_score * 100
        delivery_component = on_time_delivery * 100
        defect_component = max(0, (1.0 - defect_rate) * 100)  # Lower defect rate = higher score
        price_component = price_comp * 100
        response_component = max(0, 100 - (response_time * 10))  # Faster response = higher score
        
        # Calculate weighted overall score
        overall_score = (
            quality_component * self.WEIGHTS['quality_score'] +
            delivery_component * self.WEIGHTS['on_time_delivery_rate'] +
            defect_component * self.WEIGHTS['defect_rate'] +
            price_component * self.WEIGHTS['price_competitiveness'] +
            response_component * self.WEIGHTS['response_time_days']
        )
        
        # Apply partnership bonus (up to +5 points for long-term partners)
        partnership_bonus = min(5, years_partnership * 0.5)
        overall_score = min(100, overall_score + partnership_bonus)
        
        # Determine risk level
        risk_level = self._determine_risk_level(
            overall_score, defect_rate, on_time_delivery, quality_score
        )
        
        # Determine category
        category = self._determine_category(overall_score, risk_level)
        
        # Generate breakdown
        breakdown = {
            'quality_score': round(quality_component, 1),
            'on_time_delivery': round(delivery_component, 1),
            'defect_rate_score': round(defect_component, 1),
            'price_competitiveness': round(price_component, 1),
            'response_time_score': round(response_component, 1),
            'partnership_bonus': round(partnership_bonus, 1)
        }
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            supplier_data, overall_score, risk_level
        )
        
        # Anomaly detection (if sklearn available)
        anomaly_detected = False
        if SKLEARN_AVAILABLE:
            anomaly_detected = self._detect_anomaly(supplier_data)
        
        return {
            'supplier_id': supplier_data.get('supplier_id', 'UNKNOWN'),
            'overall_score': round(overall_score, 1),
            'risk_level': risk_level,
            'category': category,
            'breakdown': breakdown,
            'recommendations': recommendations,
            'anomaly_detected': anomaly_detected,
            'metrics': {
                'quality_score': quality_score,
                'on_time_delivery_rate': on_time_delivery,
                'defect_rate': defect_rate,
                'price_competitiveness': price_comp,
                'response_time_days': response_time,
                'years_of_partnership': years_partnership
            }
        }
    
    def _determine_risk_level(
        self,
        overall_score: float,
        defect_rate: float,
        on_time_delivery: float,
        quality_score: float
    ) -> str:
        """Determine supplier risk level."""
        # Critical risk factors
        if defect_rate > 0.10 or on_time_delivery < 0.70 or quality_score < 0.60:
            return "CRITICAL"
        
        if overall_score >= 85:
            return "LOW"
        elif overall_score >= 70:
            return "MEDIUM"
        elif overall_score >= 55:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def _determine_category(self, overall_score: float, risk_level: str) -> str:
        """Determine supplier category."""
        if risk_level == "CRITICAL":
            return "DISQUALIFIED"
        elif overall_score >= 85:
            return "PREFERRED"
        elif overall_score >= 70:
            return "APPROVED"
        else:
            return "CONDITIONAL"
    
    def _generate_recommendations(
        self,
        supplier_data: Dict,
        overall_score: float,
        risk_level: str
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        quality_score = supplier_data.get('quality_score', 0.85)
        on_time_delivery = supplier_data.get('on_time_delivery_rate', 0.90)
        defect_rate = supplier_data.get('defect_rate', 0.03)
        response_time = supplier_data.get('response_time_days', 2.0)
        price_comp = supplier_data.get('price_competitiveness', 0.75)
        
        # Risk-specific recommendations
        if risk_level == "CRITICAL":
            recommendations.append("🚨 CRITICAL: Consider suspending orders until issues are resolved")
            recommendations.append("Schedule urgent meeting with supplier management")
        elif risk_level == "HIGH":
            recommendations.append("⚠️ HIGH RISK: Implement enhanced quality inspections")
            recommendations.append("Reduce order volume and seek alternative suppliers")
        
        # Metric-specific recommendations
        if defect_rate > 0.08:
            recommendations.append(f"❌ High defect rate ({defect_rate:.1%}). Require corrective action plan")
        elif defect_rate > 0.05:
            recommendations.append(f"⚠️ Elevated defect rate ({defect_rate:.1%}). Request quality improvement plan")
        
        if on_time_delivery < 0.80:
            recommendations.append(f"📦 Poor delivery performance ({on_time_delivery:.0%}). Review logistics and planning")
        elif on_time_delivery < 0.90:
            recommendations.append(f"📦 On-time delivery needs improvement ({on_time_delivery:.0%})")
        
        if quality_score < 0.70:
            recommendations.append(f"📉 Low quality score ({quality_score:.0%}). Conduct quality audit")
        
        if response_time > 5:
            recommendations.append(f"⏰ Slow response time ({response_time:.1f} days). Establish better communication channels")
        
        if price_comp < 0.60:
            recommendations.append(f"💰 Price competitiveness is low ({price_comp:.0%}). Negotiate better rates")
        
        # Positive feedback for good suppliers
        if overall_score >= 90:
            recommendations.insert(0, "✅ EXCELLENT: Maintain strong partnership and consider volume increases")
        elif overall_score >= 85:
            recommendations.insert(0, "✓ GOOD: Reliable supplier, maintain current relationship")
        
        if not recommendations:
            recommendations.append("✓ Performance is adequate. Continue regular monitoring.")
        
        return recommendations
    
    def _detect_anomaly(self, supplier_data: Dict) -> bool:
        """
        Detect anomalous supplier metrics using IsolationForest.
        
        Returns True if supplier metrics are anomalous.
        """
        if not SKLEARN_AVAILABLE:
            return False
        
        try:
            # Prepare features
            features = np.array([[
                supplier_data.get('quality_score', 0.85),
                supplier_data.get('on_time_delivery_rate', 0.90),
                supplier_data.get('defect_rate', 0.03),
                supplier_data.get('price_competitiveness', 0.75),
                supplier_data.get('response_time_days', 2.0) / 10.0  # Normalize
            ]])
            
            # Create and fit IsolationForest (with typical supplier data range)
            clf = IsolationForest(contamination=0.1, random_state=42)
            
            # Generate synthetic normal data for comparison
            normal_data = np.random.randn(100, 5) * 0.1 + np.array([0.85, 0.90, 0.03, 0.75, 0.2])
            clf.fit(normal_data)
            
            # Predict
            prediction = clf.predict(features)
            
            # -1 indicates anomaly
            return bool(prediction[0] == -1)
        
        except Exception as e:
            logger.warning(f"Anomaly detection failed: {e}")
            return False
