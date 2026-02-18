"""
Procurement Advisory System

This module provides intelligent procurement recommendations based on
supplier performance analysis and risk assessment.

Key Features:
- Automated procurement decisions (RECOMMEND/MONITOR/REVIEW/REJECT)
- Confidence scoring for recommendations
- Risk factor identification
- Opportunity identification
- Order volume suggestions (LOW/MEDIUM/HIGH)
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class ProcurementAdvisor:
    """
    Intelligent procurement advisory system.
    
    Analyzes supplier data to provide actionable procurement recommendations
    with confidence levels and detailed reasoning.
    """
    
    def __init__(self):
        """Initialize the procurement advisor."""
        logger.info("ProcurementAdvisor initialized")
    
    def advise(self, supplier_data: Dict) -> Dict:
        """
        Generate procurement advice for a supplier.
        
        Args:
            supplier_data: Dictionary containing supplier metrics:
                - supplier_id: Supplier identifier
                - on_time_delivery_rate: 0.0-1.0
                - quality_score: 0.0-1.0
                - price_competitiveness: 0.0-1.0
                - defect_rate: 0.0-1.0
                - response_time_days: Average response time
                - years_of_partnership: Years working together
        
        Returns:
            Dictionary with action, confidence, reasoning, risk_factors,
            opportunities, and suggested_order_volume
        """
        supplier_id = supplier_data.get('supplier_id', 'UNKNOWN')
        logger.info(f"Generating procurement advice for: {supplier_id}")
        
        # Analyze supplier performance
        quality = supplier_data.get('quality_score', 0.5)
        delivery = supplier_data.get('on_time_delivery_rate', 0.5)
        defect_rate = supplier_data.get('defect_rate', 0.05)
        price = supplier_data.get('price_competitiveness', 0.5)
        response_time = supplier_data.get('response_time_days', 5.0)
        years = supplier_data.get('years_of_partnership', 0.0)
        
        # Calculate aggregate performance score
        performance_score = (
            quality * 0.35 +
            delivery * 0.25 +
            (1 - min(defect_rate * 10, 1)) * 0.20 +
            price * 0.15 +
            (1 - min(response_time / 10, 1)) * 0.05
        )
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(supplier_data)
        
        # Identify opportunities
        opportunities = self._identify_opportunities(supplier_data)
        
        # Determine action based on performance and risks
        action = self._determine_action(performance_score, risk_factors)
        
        # Calculate confidence level
        confidence = self._calculate_confidence(supplier_data, action, risk_factors)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            action, performance_score, quality, delivery, defect_rate, years
        )
        
        # Suggest order volume
        order_volume = self._suggest_order_volume(action, performance_score, risk_factors)
        
        result = {
            'supplier_id': supplier_id,
            'action': action,
            'confidence': round(confidence, 3),
            'reasoning': reasoning,
            'risk_factors': risk_factors,
            'opportunities': opportunities,
            'suggested_order_volume': order_volume
        }
        
        logger.info(f"✓ Advice for {supplier_id}: {action} (confidence: {confidence:.2f})")
        
        return result
    
    def _identify_risk_factors(self, data: Dict) -> List[str]:
        """
        Identify risk factors based on supplier metrics.
        
        Args:
            data: Supplier data dictionary
            
        Returns:
            List of identified risk factors
        """
        risks = []
        
        quality = data.get('quality_score', 0.5)
        delivery = data.get('on_time_delivery_rate', 0.5)
        defect_rate = data.get('defect_rate', 0.05)
        response_time = data.get('response_time_days', 5.0)
        years = data.get('years_of_partnership', 0.0)
        
        if quality < 0.7:
            risks.append(f"Low quality score: {quality*100:.1f}%")
        
        if delivery < 0.85:
            risks.append(f"Poor delivery performance: {delivery*100:.1f}% on-time")
        
        if defect_rate > 0.05:
            risks.append(f"High defect rate: {defect_rate*100:.1f}%")
        
        if response_time > 5:
            risks.append(f"Slow response time: {response_time:.1f} days")
        
        if years < 1:
            risks.append("New supplier - limited track record")
        
        return risks
    
    def _identify_opportunities(self, data: Dict) -> List[str]:
        """
        Identify opportunities based on supplier strengths.
        
        Args:
            data: Supplier data dictionary
            
        Returns:
            List of identified opportunities
        """
        opportunities = []
        
        quality = data.get('quality_score', 0.5)
        delivery = data.get('on_time_delivery_rate', 0.5)
        defect_rate = data.get('defect_rate', 0.05)
        price = data.get('price_competitiveness', 0.5)
        years = data.get('years_of_partnership', 0.0)
        
        if quality >= 0.90:
            opportunities.append("Excellent quality - consider for critical components")
        
        if delivery >= 0.95:
            opportunities.append("Highly reliable delivery - suitable for JIT manufacturing")
        
        if defect_rate < 0.01:
            opportunities.append("Very low defect rate - potential for reduced inspection")
        
        if price >= 0.80:
            opportunities.append("Competitive pricing - cost optimization potential")
        
        if years >= 5:
            opportunities.append("Long-term relationship - negotiate strategic partnership")
        
        if quality >= 0.85 and delivery >= 0.90 and defect_rate < 0.02:
            opportunities.append("Strong overall performance - candidate for increased volume")
        
        return opportunities
    
    def _determine_action(self, performance_score: float, risk_factors: List[str]) -> str:
        """
        Determine procurement action based on performance and risks.
        
        Args:
            performance_score: Aggregate performance (0-1)
            risk_factors: List of identified risks
            
        Returns:
            Action: RECOMMEND, MONITOR, REVIEW, or REJECT
        """
        critical_risks = len([r for r in risk_factors if 'High defect' in r or 'Low quality' in r])
        
        if critical_risks > 0:
            return "REJECT"
        elif performance_score >= 0.80 and len(risk_factors) <= 1:
            return "RECOMMEND"
        elif performance_score >= 0.65:
            return "MONITOR"
        else:
            return "REVIEW"
    
    def _calculate_confidence(
        self,
        data: Dict,
        action: str,
        risk_factors: List[str]
    ) -> float:
        """
        Calculate confidence level for the recommendation.
        
        Args:
            data: Supplier data
            action: Recommended action
            risk_factors: Identified risks
            
        Returns:
            Confidence score (0.0-1.0)
        """
        years = data.get('years_of_partnership', 0.0)
        
        # Base confidence on data history
        base_confidence = min(0.5 + (years / 10), 0.85)
        
        # Adjust based on action and risks
        if action == "RECOMMEND":
            confidence = base_confidence + 0.15
        elif action == "REJECT":
            confidence = base_confidence + 0.10
        elif action == "MONITOR":
            confidence = base_confidence
        else:  # REVIEW
            confidence = base_confidence - 0.10
        
        # Penalize for many risk factors
        confidence -= len(risk_factors) * 0.05
        
        return max(0.5, min(1.0, confidence))
    
    def _generate_reasoning(
        self,
        action: str,
        performance_score: float,
        quality: float,
        delivery: float,
        defect_rate: float,
        years: float
    ) -> str:
        """
        Generate human-readable reasoning for the recommendation.
        
        Args:
            action: Recommended action
            performance_score: Aggregate performance score
            quality: Quality score
            delivery: Delivery rate
            defect_rate: Defect rate
            years: Partnership duration
            
        Returns:
            Reasoning string
        """
        if action == "RECOMMEND":
            return (
                f"Supplier demonstrates strong performance (score: {performance_score:.2f}). "
                f"Quality at {quality*100:.1f}%, delivery at {delivery*100:.1f}%, "
                f"and defect rate of {defect_rate*100:.2f}% indicate reliability. "
                "Safe for increased procurement volume."
            )
        elif action == "MONITOR":
            return (
                f"Supplier shows acceptable performance (score: {performance_score:.2f}) "
                "but requires monitoring. Continue current procurement levels while "
                "tracking quality and delivery metrics closely."
            )
        elif action == "REVIEW":
            return (
                f"Supplier performance is below expectations (score: {performance_score:.2f}). "
                f"Quality ({quality*100:.1f}%), delivery ({delivery*100:.1f}%), "
                f"or defect rate ({defect_rate*100:.2f}%) need improvement. "
                "Schedule review meeting before placing new orders."
            )
        else:  # REJECT
            return (
                f"Supplier performance is unacceptable (score: {performance_score:.2f}). "
                f"Critical issues detected: quality {quality*100:.1f}%, "
                f"defect rate {defect_rate*100:.2f}%. "
                "Recommend finding alternative suppliers immediately."
            )
    
    def _suggest_order_volume(
        self,
        action: str,
        performance_score: float,
        risk_factors: List[str]
    ) -> str:
        """
        Suggest order volume based on action and performance.
        
        Args:
            action: Recommended action
            performance_score: Aggregate performance score
            risk_factors: Identified risks
            
        Returns:
            Order volume suggestion: LOW, MEDIUM, or HIGH
        """
        if action == "REJECT":
            return "NONE"
        elif action == "RECOMMEND" and performance_score >= 0.85:
            return "HIGH"
        elif action == "RECOMMEND":
            return "MEDIUM"
        elif action == "MONITOR":
            return "MEDIUM" if len(risk_factors) <= 2 else "LOW"
        else:  # REVIEW
            return "LOW"


def create_demo_advisor() -> ProcurementAdvisor:
    """
    Create a demo procurement advisor.
    
    Returns:
        Initialized ProcurementAdvisor
    """
    return ProcurementAdvisor()
