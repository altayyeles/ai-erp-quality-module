"""
Supplier Scoring System
K-Means clustering and IsolationForest-based supplier risk assessment

This module evaluates supplier performance using multiple metrics and provides
risk-based scoring with category classification.
"""

import logging
from typing import Dict, List
import numpy as np

try:
    from sklearn.cluster import KMeans
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not available. Supplier scoring will use fallback mode.")

logger = logging.getLogger(__name__)


class SupplierScorer:
    """
    Supplier performance scoring system with risk assessment.
    
    Uses weighted metrics and anomaly detection to classify suppliers
    into risk categories and provide actionable recommendations.
    """
    
    # Metric weights (must sum to 1.0)
    WEIGHTS = {
        'quality_score': 0.30,
        'on_time_delivery_rate': 0.25,
        'defect_rate': 0.20,
        'price_competitiveness': 0.15,
        'response_time_days': 0.10
    }
    
    def __init__(self):
        """Initialize the supplier scorer."""
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
    
    def score(self, supplier_data: Dict) -> Dict:
        """
        Score a supplier based on performance metrics.
        
        Args:
            supplier_data: Dictionary containing:
                - supplier_id: Unique supplier identifier
                - on_time_delivery_rate: 0.0-1.0 (e.g., 0.95 = 95%)
                - quality_score: 0.0-1.0
                - price_competitiveness: 0.0-1.0 (higher = better)
                - defect_rate: 0.0-1.0 (lower = better)
                - response_time_days: Average response time in days
                - years_of_partnership: Years working together (optional)
        
        Returns:
            Dictionary with overall score, risk level, category, breakdown, and recommendations
        """
        supplier_id = supplier_data.get('supplier_id', 'UNKNOWN')
        
        # Extract metrics with defaults
        metrics = {
            'quality_score': supplier_data.get('quality_score', 0.5),
            'on_time_delivery_rate': supplier_data.get('on_time_delivery_rate', 0.5),
            'price_competitiveness': supplier_data.get('price_competitiveness', 0.5),
            'defect_rate': supplier_data.get('defect_rate', 0.1),
            'response_time_days': supplier_data.get('response_time_days', 5.0),
            'years_of_partnership': supplier_data.get('years_of_partnership', 0)
        }
        
        # Calculate component scores (0-100 scale)
        component_scores = self._calculate_component_scores(metrics)
        
        # Calculate weighted overall score
        overall_score = self._calculate_overall_score(component_scores)
        
        # Determine risk level
        risk_level = self._determine_risk_level(overall_score, metrics)
        
        # Classify supplier category
        category = self._classify_category(overall_score, risk_level, metrics)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            metrics, component_scores, overall_score, risk_level
        )
        
        return {
            'supplier_id': supplier_id,
            'overall_score': round(overall_score, 1),
            'risk_level': risk_level,
            'category': category,
            'breakdown': component_scores,
            'recommendations': recommendations,
            'metrics_summary': {
                'quality_score': round(metrics['quality_score'] * 100, 1),
                'on_time_delivery': round(metrics['on_time_delivery_rate'] * 100, 1),
                'defect_rate': round(metrics['defect_rate'] * 100, 2),
                'price_competitiveness': round(metrics['price_competitiveness'] * 100, 1)
            }
        }
    
    def _calculate_component_scores(self, metrics: Dict) -> Dict[str, float]:
        """Calculate individual component scores (0-100 scale)."""
        scores = {}
        
        # Quality score (higher is better)
        scores['quality'] = metrics['quality_score'] * 100
        
        # On-time delivery (higher is better)
        scores['delivery'] = metrics['on_time_delivery_rate'] * 100
        
        # Defect rate (lower is better, so invert)
        scores['defects'] = (1 - metrics['defect_rate']) * 100
        
        # Price competitiveness (higher is better)
        scores['price'] = metrics['price_competitiveness'] * 100
        
        # Response time (lower is better, normalize to 0-100)
        # Assume 1 day = excellent (100), 10 days = poor (0)
        response_time = metrics['response_time_days']
        scores['responsiveness'] = max(0, 100 - (response_time - 1) * 11.1)
        
        return {k: round(v, 1) for k, v in scores.items()}
    
    def _calculate_overall_score(self, component_scores: Dict[str, float]) -> float:
        """Calculate weighted overall score."""
        overall = 0.0
        
        overall += component_scores['quality'] * self.WEIGHTS['quality_score']
        overall += component_scores['delivery'] * self.WEIGHTS['on_time_delivery_rate']
        overall += component_scores['defects'] * self.WEIGHTS['defect_rate']
        overall += component_scores['price'] * self.WEIGHTS['price_competitiveness']
        overall += component_scores['responsiveness'] * self.WEIGHTS['response_time_days']
        
        return overall
    
    def _determine_risk_level(self, overall_score: float, metrics: Dict) -> str:
        """Determine risk level based on score and critical metrics."""
        # Check for critical red flags
        if metrics['defect_rate'] > 0.15 or metrics['quality_score'] < 0.5:
            return "CRITICAL"
        
        if overall_score >= 80:
            return "LOW"
        elif overall_score >= 65:
            return "MEDIUM"
        elif overall_score >= 50:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def _classify_category(self, overall_score: float, risk_level: str, metrics: Dict) -> str:
        """Classify supplier into operational category."""
        # DISQUALIFIED: Critical issues
        if risk_level == "CRITICAL":
            return "DISQUALIFIED"
        
        # PREFERRED: High performers
        if overall_score >= 85 and metrics['years_of_partnership'] >= 2:
            return "PREFERRED"
        
        # APPROVED: Good performers
        if overall_score >= 70:
            return "APPROVED"
        
        # CONDITIONAL: Marginal performers
        if overall_score >= 50:
            return "CONDITIONAL"
        
        return "DISQUALIFIED"
    
    def _generate_recommendations(
        self,
        metrics: Dict,
        component_scores: Dict,
        overall_score: float,
        risk_level: str
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Risk-based overall recommendations
        if risk_level == "CRITICAL":
            recommendations.append("🚨 CRITICAL: Immediate review required. Consider alternative suppliers.")
        elif risk_level == "HIGH":
            recommendations.append("⚠️ HIGH RISK: Schedule supplier audit and improvement plan.")
        elif risk_level == "LOW":
            recommendations.append("✅ LOW RISK: Maintain current partnership and monitor performance.")
        
        # Component-specific recommendations
        if component_scores['quality'] < 70:
            recommendations.append(
                f"📉 Quality score is low ({component_scores['quality']:.0f}/100). "
                "Request quality improvement plan."
            )
        
        if component_scores['delivery'] < 80:
            recommendations.append(
                f"🚚 On-time delivery needs improvement ({component_scores['delivery']:.0f}/100). "
                "Discuss logistics optimization."
            )
        
        if component_scores['defects'] < 85:
            defect_rate = metrics['defect_rate'] * 100
            recommendations.append(
                f"⚠️ Defect rate is concerning ({defect_rate:.1f}%). "
                "Implement stricter quality controls."
            )
        
        if component_scores['price'] < 60:
            recommendations.append(
                f"💰 Pricing not competitive ({component_scores['price']:.0f}/100). "
                "Negotiate better terms or seek alternatives."
            )
        
        if component_scores['responsiveness'] < 70:
            recommendations.append(
                f"⏱️ Response time is slow ({metrics['response_time_days']:.1f} days). "
                "Request improved communication protocols."
            )
        
        # Partnership recommendations
        if metrics['years_of_partnership'] < 1:
            recommendations.append(
                "🆕 New supplier: Monitor closely during probationary period."
            )
        elif metrics['years_of_partnership'] >= 5 and overall_score >= 85:
            recommendations.append(
                "⭐ Long-term high performer: Consider preferred supplier status."
            )
        
        return recommendations
    
    def score_multiple(self, suppliers_data: List[Dict]) -> List[Dict]:
        """
        Score multiple suppliers and rank them.
        
        Args:
            suppliers_data: List of supplier data dictionaries
            
        Returns:
            List of scored suppliers, sorted by overall score (descending)
        """
        scores = [self.score(supplier) for supplier in suppliers_data]
        
        # Sort by overall score
        scores.sort(key=lambda x: x['overall_score'], reverse=True)
        
        # Add rank
        for i, score in enumerate(scores, 1):
            score['rank'] = i
        
        return scores
    
    def detect_anomalies(self, suppliers_data: List[Dict]) -> List[str]:
        """
        Detect anomalous supplier performance using IsolationForest.
        
        Args:
            suppliers_data: List of supplier data dictionaries
            
        Returns:
            List of supplier IDs flagged as anomalous
        """
        if not SKLEARN_AVAILABLE or len(suppliers_data) < 3:
            logger.warning("Cannot perform anomaly detection: sklearn unavailable or insufficient data")
            return []
        
        # Extract features
        features = []
        supplier_ids = []
        
        for supplier in suppliers_data:
            features.append([
                supplier.get('quality_score', 0.5),
                supplier.get('on_time_delivery_rate', 0.5),
                supplier.get('defect_rate', 0.1),
                supplier.get('price_competitiveness', 0.5),
                supplier.get('response_time_days', 5.0)
            ])
            supplier_ids.append(supplier.get('supplier_id', 'UNKNOWN'))
        
        features = np.array(features)
        
        # Fit IsolationForest
        iso_forest = IsolationForest(contamination=0.1, random_state=42)
        predictions = iso_forest.fit_predict(features)
        
        # Return anomalous suppliers (prediction = -1)
        anomalies = [
            supplier_ids[i] for i, pred in enumerate(predictions) if pred == -1
        ]
        
        return anomalies
