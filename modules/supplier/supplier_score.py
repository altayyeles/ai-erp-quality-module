"""
Supplier Scoring System

This module implements a weighted scoring system for supplier evaluation
based on multiple performance metrics.

Key Features:
- Multi-criteria weighted scoring
- Risk level classification (LOW/MEDIUM/HIGH/CRITICAL)
- Supplier category assignment (PREFERRED/APPROVED/CONDITIONAL/DISQUALIFIED)
- Detailed score breakdown by metric
- Actionable recommendations
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class SupplierScorer:
    """
    Weighted scoring system for supplier risk assessment.
    
    Evaluates suppliers based on quality, delivery, price, defects,
    response time, and partnership duration.
    """
    
    # Scoring weights (must sum to 1.0)
    WEIGHTS = {
        'quality_score': 0.30,          # 30%
        'on_time_delivery_rate': 0.25,  # 25%
        'defect_rate': 0.20,             # 20%
        'price_competitiveness': 0.15,   # 15%
        'response_time_days': 0.10       # 10%
    }
    
    def __init__(self):
        """Initialize the supplier scorer."""
        logger.info("SupplierScorer initialized")
    
    def score(self, supplier_data: Dict) -> Dict:
        """
        Calculate comprehensive supplier score.
        
        Args:
            supplier_data: Dictionary containing supplier metrics:
                - supplier_id: Supplier identifier
                - on_time_delivery_rate: 0.0-1.0 (e.g., 0.95 = 95%)
                - quality_score: 0.0-1.0 (e.g., 0.85 = 85%)
                - price_competitiveness: 0.0-1.0 (higher = better)
                - defect_rate: 0.0-1.0 (e.g., 0.03 = 3%, lower = better)
                - response_time_days: Average response time in days
                - years_of_partnership: Years working together
        
        Returns:
            Dictionary with overall_score, risk_level, category, breakdown, and recommendations
        """
        supplier_id = supplier_data.get('supplier_id', 'UNKNOWN')
        logger.info(f"Scoring supplier: {supplier_id}")
        
        # Calculate individual metric scores (0-100 scale)
        breakdown = self._calculate_breakdown(supplier_data)
        
        # Calculate weighted overall score
        overall_score = sum(
            breakdown[metric] * self.WEIGHTS[metric]
            for metric in self.WEIGHTS.keys()
        )
        
        # Determine risk level
        risk_level = self._calculate_risk_level(overall_score, supplier_data)
        
        # Determine supplier category
        category = self._determine_category(overall_score, risk_level)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(supplier_data, breakdown)
        
        result = {
            'supplier_id': supplier_id,
            'overall_score': round(overall_score, 2),
            'risk_level': risk_level,
            'category': category,
            'breakdown': breakdown,
            'recommendations': recommendations
        }
        
        logger.info(f"✓ Supplier {supplier_id} scored: {overall_score:.2f} - {risk_level} risk, {category}")
        
        return result
    
    def _calculate_breakdown(self, data: Dict) -> Dict[str, float]:
        """
        Calculate individual metric scores on 0-100 scale.
        
        Args:
            data: Supplier data dictionary
            
        Returns:
            Dictionary with scores for each metric
        """
        # Quality score (already 0-1, convert to 0-100)
        quality = data.get('quality_score', 0.5) * 100
        
        # On-time delivery (already 0-1, convert to 0-100)
        delivery = data.get('on_time_delivery_rate', 0.5) * 100
        
        # Defect rate (invert: lower is better)
        defect_rate = data.get('defect_rate', 0.05)
        defects = max(0, 100 - (defect_rate * 1000))  # 5% defect = 50 score
        
        # Price competitiveness (already 0-1, convert to 0-100)
        price = data.get('price_competitiveness', 0.5) * 100
        
        # Response time (invert: lower days is better)
        response_days = data.get('response_time_days', 5.0)
        response = max(0, 100 - (response_days * 10))  # 5 days = 50 score
        
        return {
            'quality_score': round(quality, 2),
            'on_time_delivery_rate': round(delivery, 2),
            'defect_rate': round(defects, 2),
            'price_competitiveness': round(price, 2),
            'response_time_days': round(response, 2)
        }
    
    def _calculate_risk_level(self, overall_score: float, data: Dict) -> str:
        """
        Determine risk level based on overall score and critical metrics.
        
        Args:
            overall_score: Weighted overall score (0-100)
            data: Supplier data for critical checks
            
        Returns:
            Risk level: LOW, MEDIUM, HIGH, or CRITICAL
        """
        defect_rate = data.get('defect_rate', 0.0)
        quality = data.get('quality_score', 0.0)
        delivery = data.get('on_time_delivery_rate', 0.0)
        
        # Critical conditions
        if defect_rate > 0.10 or quality < 0.5 or delivery < 0.6:
            return "CRITICAL"
        
        # Score-based classification
        if overall_score >= 80:
            return "LOW"
        elif overall_score >= 65:
            return "MEDIUM"
        elif overall_score >= 50:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def _determine_category(self, overall_score: float, risk_level: str) -> str:
        """
        Assign supplier category based on score and risk.
        
        Args:
            overall_score: Weighted overall score (0-100)
            risk_level: Risk classification
            
        Returns:
            Category: PREFERRED, APPROVED, CONDITIONAL, or DISQUALIFIED
        """
        if risk_level == "CRITICAL":
            return "DISQUALIFIED"
        elif overall_score >= 85:
            return "PREFERRED"
        elif overall_score >= 70:
            return "APPROVED"
        else:
            return "CONDITIONAL"
    
    def _generate_recommendations(self, data: Dict, breakdown: Dict[str, float]) -> List[str]:
        """
        Generate actionable recommendations based on supplier performance.
        
        Args:
            data: Original supplier data
            breakdown: Calculated metric scores
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Check quality score
        if breakdown['quality_score'] < 70:
            recommendations.append("⚠️ Quality score below threshold. Request quality improvement plan.")
        elif breakdown['quality_score'] >= 90:
            recommendations.append("✓ Excellent quality performance. Consider for preferred status.")
        
        # Check delivery performance
        if breakdown['on_time_delivery_rate'] < 80:
            recommendations.append("⚠️ On-time delivery needs improvement. Discuss logistics optimization.")
        elif breakdown['on_time_delivery_rate'] >= 95:
            recommendations.append("✓ Outstanding delivery reliability.")
        
        # Check defect rate
        defect_rate = data.get('defect_rate', 0.0)
        if defect_rate > 0.05:
            recommendations.append(f"🚨 High defect rate ({defect_rate*100:.1f}%). Conduct quality audit immediately.")
        elif defect_rate < 0.01:
            recommendations.append("✓ Excellent defect rate. Maintain current quality standards.")
        
        # Check price competitiveness
        if breakdown['price_competitiveness'] < 60:
            recommendations.append("💰 Price competitiveness low. Negotiate better terms or explore alternatives.")
        
        # Check response time
        response_days = data.get('response_time_days', 0.0)
        if response_days > 5:
            recommendations.append(f"⏱️ Slow response time ({response_days:.1f} days). Request faster communication.")
        
        # Partnership duration
        years = data.get('years_of_partnership', 0.0)
        if years > 5:
            recommendations.append(f"🤝 Long-term partner ({years:.0f} years). Consider strategic partnership benefits.")
        
        # Overall assessment
        if not recommendations:
            recommendations.append("✓ Supplier performance is satisfactory across all metrics.")
        
        return recommendations


def create_demo_scorer() -> SupplierScorer:
    """
    Create a demo supplier scorer.
    
    Returns:
        Initialized SupplierScorer
    """
    return SupplierScorer()
