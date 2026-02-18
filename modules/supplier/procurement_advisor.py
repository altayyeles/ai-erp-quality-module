"""
Procurement Advisory System
Provides intelligent procurement recommendations based on supplier analysis
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class ProcurementAdvisor:
    """
    Intelligent procurement advisory system.
    
    Analyzes supplier data and provides actionable procurement recommendations
    including action type, confidence level, reasoning, and suggested order volumes.
    """
    
    def __init__(self):
        """Initialize procurement advisor."""
        pass
    
    def advise(self, supplier_data: Dict) -> Dict:
        """
        Generate procurement advice for a supplier.
        
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
            Dictionary with procurement advice
        """
        # Extract metrics
        quality_score = float(supplier_data.get('quality_score', 0.85))
        on_time_delivery = float(supplier_data.get('on_time_delivery_rate', 0.90))
        price_comp = float(supplier_data.get('price_competitiveness', 0.75))
        defect_rate = float(supplier_data.get('defect_rate', 0.03))
        response_time = float(supplier_data.get('response_time_days', 2.0))
        years_partnership = float(supplier_data.get('years_of_partnership', 3.0))
        
        # Calculate composite score for decision making
        composite_score = (
            quality_score * 0.35 +
            on_time_delivery * 0.30 +
            (1.0 - defect_rate) * 0.20 +
            price_comp * 0.15
        )
        
        # Determine action
        action = self._determine_action(
            composite_score, defect_rate, on_time_delivery, quality_score
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            composite_score, years_partnership, supplier_data
        )
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            action, supplier_data, composite_score
        )
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(supplier_data)
        
        # Identify opportunities
        opportunities = self._identify_opportunities(supplier_data)
        
        # Suggest order volume
        order_volume = self._suggest_order_volume(action, composite_score, risk_factors)
        
        return {
            'supplier_id': supplier_data.get('supplier_id', 'UNKNOWN'),
            'action': action,
            'confidence': round(confidence, 2),
            'reasoning': reasoning,
            'risk_factors': risk_factors,
            'opportunities': opportunities,
            'suggested_order_volume': order_volume,
            'composite_score': round(composite_score * 100, 1)
        }
    
    def _determine_action(
        self,
        composite_score: float,
        defect_rate: float,
        on_time_delivery: float,
        quality_score: float
    ) -> str:
        """Determine procurement action."""
        # Critical issues -> REJECT
        if defect_rate > 0.12 or on_time_delivery < 0.65 or quality_score < 0.55:
            return "REJECT"
        
        # High-risk issues -> REVIEW
        if defect_rate > 0.08 or on_time_delivery < 0.75 or quality_score < 0.65:
            return "REVIEW"
        
        # Good performance -> RECOMMEND
        if composite_score >= 0.85:
            return "RECOMMEND"
        
        # Moderate performance -> MONITOR
        if composite_score >= 0.70:
            return "MONITOR"
        
        # Below threshold -> REVIEW
        return "REVIEW"
    
    def _calculate_confidence(
        self,
        composite_score: float,
        years_partnership: float,
        supplier_data: Dict
    ) -> float:
        """Calculate confidence level for the recommendation."""
        # Base confidence from composite score
        confidence = composite_score
        
        # Adjust for partnership history (more data = higher confidence)
        if years_partnership >= 5:
            confidence += 0.10
        elif years_partnership >= 2:
            confidence += 0.05
        
        # Reduce confidence for inconsistent metrics
        quality_score = supplier_data.get('quality_score', 0.85)
        on_time_delivery = supplier_data.get('on_time_delivery_rate', 0.90)
        defect_rate = supplier_data.get('defect_rate', 0.03)
        
        # Check for inconsistencies (e.g., high quality but high defects)
        if (quality_score > 0.85 and defect_rate > 0.08) or \
           (on_time_delivery > 0.90 and defect_rate > 0.10):
            confidence -= 0.10
        
        # Ensure confidence is between 0 and 1
        confidence = max(0.0, min(1.0, confidence))
        
        return confidence
    
    def _generate_reasoning(
        self,
        action: str,
        supplier_data: Dict,
        composite_score: float
    ) -> str:
        """Generate human-readable reasoning for the recommendation."""
        quality_score = supplier_data.get('quality_score', 0.85)
        on_time_delivery = supplier_data.get('on_time_delivery_rate', 0.90)
        defect_rate = supplier_data.get('defect_rate', 0.03)
        years_partnership = supplier_data.get('years_of_partnership', 3.0)
        
        if action == "RECOMMEND":
            return (
                f"Strong supplier performance with composite score of {composite_score*100:.1f}%. "
                f"Quality score of {quality_score:.0%}, on-time delivery of {on_time_delivery:.0%}, "
                f"and low defect rate of {defect_rate:.1%} indicate reliable partnership. "
                f"Safe to increase order volumes."
            )
        
        elif action == "MONITOR":
            return (
                f"Acceptable supplier performance with composite score of {composite_score*100:.1f}%. "
                f"Continue current order levels while monitoring key metrics. "
                f"Quality score: {quality_score:.0%}, Delivery: {on_time_delivery:.0%}, "
                f"Defects: {defect_rate:.1%}. Watch for improvement or deterioration."
            )
        
        elif action == "REVIEW":
            concerns = []
            if defect_rate > 0.05:
                concerns.append(f"elevated defect rate ({defect_rate:.1%})")
            if on_time_delivery < 0.85:
                concerns.append(f"delivery performance ({on_time_delivery:.0%})")
            if quality_score < 0.75:
                concerns.append(f"quality score ({quality_score:.0%})")
            
            concerns_str = ", ".join(concerns) if concerns else "performance inconsistencies"
            
            return (
                f"Supplier requires review due to {concerns_str}. "
                f"Composite score of {composite_score*100:.1f}% indicates moderate risk. "
                f"Recommend detailed audit and corrective action plan before placing large orders."
            )
        
        else:  # REJECT
            critical = []
            if defect_rate > 0.10:
                critical.append(f"critical defect rate ({defect_rate:.1%})")
            if on_time_delivery < 0.70:
                critical.append(f"poor delivery performance ({on_time_delivery:.0%})")
            if quality_score < 0.60:
                critical.append(f"unacceptable quality ({quality_score:.0%})")
            
            critical_str = ", ".join(critical) if critical else "severe performance issues"
            
            return (
                f"DO NOT PLACE ORDERS. Supplier shows {critical_str}. "
                f"Composite score of {composite_score*100:.1f}% is below acceptable threshold. "
                f"Immediate suspension recommended. Seek alternative suppliers."
            )
    
    def _identify_risk_factors(self, supplier_data: Dict) -> List[str]:
        """Identify supplier risk factors."""
        risk_factors = []
        
        defect_rate = supplier_data.get('defect_rate', 0.03)
        on_time_delivery = supplier_data.get('on_time_delivery_rate', 0.90)
        quality_score = supplier_data.get('quality_score', 0.85)
        response_time = supplier_data.get('response_time_days', 2.0)
        years_partnership = supplier_data.get('years_of_partnership', 3.0)
        
        if defect_rate > 0.08:
            risk_factors.append(f"High defect rate: {defect_rate:.1%} (threshold: 5%)")
        
        if on_time_delivery < 0.85:
            risk_factors.append(f"Low on-time delivery: {on_time_delivery:.0%} (target: >90%)")
        
        if quality_score < 0.75:
            risk_factors.append(f"Low quality score: {quality_score:.0%} (target: >80%)")
        
        if response_time > 4:
            risk_factors.append(f"Slow response time: {response_time:.1f} days (target: <3 days)")
        
        if years_partnership < 1:
            risk_factors.append("New supplier with limited track record")
        
        return risk_factors
    
    def _identify_opportunities(self, supplier_data: Dict) -> List[str]:
        """Identify opportunities with the supplier."""
        opportunities = []
        
        quality_score = supplier_data.get('quality_score', 0.85)
        on_time_delivery = supplier_data.get('on_time_delivery_rate', 0.90)
        price_comp = supplier_data.get('price_competitiveness', 0.75)
        defect_rate = supplier_data.get('defect_rate', 0.03)
        years_partnership = supplier_data.get('years_of_partnership', 3.0)
        
        if quality_score > 0.90 and defect_rate < 0.02:
            opportunities.append("Excellent quality - consider strategic partnership")
        
        if on_time_delivery > 0.95:
            opportunities.append("Outstanding delivery - potential for JIT arrangements")
        
        if price_comp > 0.85:
            opportunities.append("Competitive pricing - negotiate volume discounts")
        
        if years_partnership > 5 and quality_score > 0.85:
            opportunities.append("Long-term reliable partner - consider sole sourcing for select items")
        
        if defect_rate < 0.02 and quality_score > 0.90 and on_time_delivery > 0.92:
            opportunities.append("Tier-1 supplier - expand product portfolio")
        
        return opportunities
    
    def _suggest_order_volume(
        self,
        action: str,
        composite_score: float,
        risk_factors: List[str]
    ) -> str:
        """Suggest order volume level."""
        if action == "REJECT":
            return "NONE"
        
        if action == "REVIEW":
            return "LOW"
        
        if action == "MONITOR":
            if len(risk_factors) > 2:
                return "LOW"
            return "MEDIUM"
        
        # RECOMMEND
        if composite_score >= 0.90:
            return "HIGH"
        elif composite_score >= 0.85:
            return "MEDIUM"
        else:
            return "MEDIUM"
