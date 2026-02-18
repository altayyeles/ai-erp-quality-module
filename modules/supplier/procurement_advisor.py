"""
Procurement Advisory System
Intelligent supplier-based procurement recommendations

This module provides AI-powered procurement advice based on supplier performance,
risk factors, and business opportunities.
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class ProcurementAdvisor:
    """
    Procurement advisory system for supplier-based purchasing decisions.
    
    Analyzes supplier data and provides actionable procurement recommendations
    with confidence scores and risk assessment.
    """
    
    def __init__(self):
        """Initialize the procurement advisor."""
        pass
    
    def advise(self, supplier_data: Dict) -> Dict:
        """
        Generate procurement advice for a supplier.
        
        Args:
            supplier_data: Dictionary containing supplier metrics:
                - supplier_id: Unique identifier
                - on_time_delivery_rate: 0.0-1.0
                - quality_score: 0.0-1.0
                - price_competitiveness: 0.0-1.0
                - defect_rate: 0.0-1.0
                - response_time_days: Response time in days
                - years_of_partnership: Years of relationship
        
        Returns:
            Dictionary with action, confidence, reasoning, risk factors, 
            opportunities, and suggested order volume
        """
        supplier_id = supplier_data.get('supplier_id', 'UNKNOWN')
        
        # Extract metrics
        quality = supplier_data.get('quality_score', 0.5)
        delivery = supplier_data.get('on_time_delivery_rate', 0.5)
        price = supplier_data.get('price_competitiveness', 0.5)
        defects = supplier_data.get('defect_rate', 0.1)
        response_time = supplier_data.get('response_time_days', 5.0)
        partnership_years = supplier_data.get('years_of_partnership', 0)
        
        # Analyze and determine action
        action, confidence, reasoning = self._determine_action(
            quality, delivery, price, defects, response_time, partnership_years
        )
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(
            quality, delivery, defects, response_time
        )
        
        # Identify opportunities
        opportunities = self._identify_opportunities(
            quality, delivery, price, partnership_years
        )
        
        # Suggest order volume
        order_volume = self._suggest_order_volume(
            action, quality, delivery, defects
        )
        
        return {
            'supplier_id': supplier_id,
            'action': action,
            'confidence': round(confidence, 2),
            'reasoning': reasoning,
            'risk_factors': risk_factors,
            'opportunities': opportunities,
            'suggested_order_volume': order_volume,
            'procurement_strategy': self._create_strategy(action, risk_factors, opportunities)
        }
    
    def _determine_action(
        self,
        quality: float,
        delivery: float,
        price: float,
        defects: float,
        response_time: float,
        partnership_years: float
    ) -> tuple:
        """Determine recommended action with confidence and reasoning."""
        # Calculate composite score
        composite_score = (
            quality * 0.35 +
            delivery * 0.30 +
            (1 - defects) * 0.25 +
            price * 0.10
        )
        
        # Critical disqualifiers
        if defects > 0.15 or quality < 0.5:
            return (
                "REJECT",
                0.95,
                "Critical quality issues detected. Defect rate or quality score below acceptable threshold."
            )
        
        # High performers
        if composite_score >= 0.85 and partnership_years >= 2:
            return (
                "RECOMMEND",
                0.92,
                "Excellent performance across all metrics. Strong track record with minimal risk."
            )
        elif composite_score >= 0.80:
            return (
                "RECOMMEND",
                0.85,
                "Strong performance in key areas. Suitable for standard procurement."
            )
        
        # Good performers
        elif composite_score >= 0.70:
            return (
                "RECOMMEND",
                0.75,
                "Good overall performance. Minor areas for improvement but reliable supplier."
            )
        
        # Moderate performers - needs monitoring
        elif composite_score >= 0.60:
            if partnership_years >= 3:
                return (
                    "MONITOR",
                    0.65,
                    "Established relationship but performance declining. Close monitoring recommended."
                )
            else:
                return (
                    "MONITOR",
                    0.70,
                    "Acceptable performance but not exceptional. Monitor for improvements."
                )
        
        # Marginal performers
        elif composite_score >= 0.50:
            return (
                "REVIEW",
                0.60,
                "Below-average performance. Comprehensive review and improvement plan required before proceeding."
            )
        
        # Poor performers
        else:
            return (
                "REJECT",
                0.85,
                "Consistently poor performance across multiple metrics. Seek alternative suppliers."
            )
    
    def _identify_risk_factors(
        self,
        quality: float,
        delivery: float,
        defects: float,
        response_time: float
    ) -> List[str]:
        """Identify specific risk factors."""
        risks = []
        
        if quality < 0.70:
            risks.append(f"Low quality score ({quality*100:.0f}%) - May impact product reliability")
        
        if delivery < 0.80:
            risks.append(f"Poor delivery performance ({delivery*100:.0f}%) - Risk of production delays")
        
        if defects > 0.10:
            risks.append(f"High defect rate ({defects*100:.1f}%) - Increased inspection and rework costs")
        
        if defects > 0.05 and quality < 0.75:
            risks.append("Combined quality and defect issues - High risk of customer complaints")
        
        if response_time > 7:
            risks.append(f"Slow response time ({response_time:.1f} days) - May delay issue resolution")
        
        if delivery < 0.85 and response_time > 5:
            risks.append("Communication and delivery issues combined - Coordination problems likely")
        
        if not risks:
            risks.append("No significant risk factors identified")
        
        return risks
    
    def _identify_opportunities(
        self,
        quality: float,
        delivery: float,
        price: float,
        partnership_years: float
    ) -> List[str]:
        """Identify business opportunities."""
        opportunities = []
        
        if quality >= 0.85 and delivery >= 0.90:
            opportunities.append("Excellent quality and delivery - Consider for critical components")
        
        if price >= 0.80:
            opportunities.append(f"Competitive pricing - Potential cost savings opportunity")
        
        if partnership_years >= 5 and quality >= 0.75:
            opportunities.append("Long-term reliable partnership - Candidate for strategic supplier status")
        
        if quality >= 0.80 and delivery >= 0.85 and price >= 0.70:
            opportunities.append("Well-balanced performance - Good candidate for volume increase")
        
        if partnership_years >= 3 and quality >= 0.75 and delivery >= 0.80:
            opportunities.append("Established relationship with good performance - Potential for joint development")
        
        if price >= 0.85 and quality >= 0.70:
            opportunities.append("Strong value proposition - Consider expanding product range")
        
        if not opportunities:
            opportunities.append("Limited opportunities - Focus on performance improvement first")
        
        return opportunities
    
    def _suggest_order_volume(
        self,
        action: str,
        quality: float,
        delivery: float,
        defects: float
    ) -> str:
        """Suggest appropriate order volume."""
        if action == "REJECT":
            return "NONE"
        
        if action == "REVIEW":
            return "MINIMAL"
        
        if action == "MONITOR":
            if quality >= 0.70 and delivery >= 0.75:
                return "MEDIUM"
            else:
                return "LOW"
        
        if action == "RECOMMEND":
            # High confidence recommends
            if quality >= 0.85 and delivery >= 0.90 and defects < 0.03:
                return "HIGH"
            elif quality >= 0.75 and delivery >= 0.80:
                return "MEDIUM"
            else:
                return "LOW"
        
        return "MEDIUM"
    
    def _create_strategy(
        self,
        action: str,
        risk_factors: List[str],
        opportunities: List[str]
    ) -> str:
        """Create a procurement strategy summary."""
        strategies = {
            "RECOMMEND": (
                "✅ APPROVED PROCUREMENT: Proceed with standard procurement processes. "
                "Maintain regular performance reviews."
            ),
            "MONITOR": (
                "⚠️ CONDITIONAL PROCUREMENT: Proceed with caution. Implement enhanced monitoring "
                "and periodic performance reviews. Consider backup suppliers."
            ),
            "REVIEW": (
                "🔍 PROCUREMENT UNDER REVIEW: Hold major orders pending improvement. "
                "Schedule supplier audit and require corrective action plan before proceeding."
            ),
            "REJECT": (
                "🚫 PROCUREMENT NOT RECOMMENDED: Suspend new orders. Seek alternative suppliers "
                "immediately. Wind down existing commitments safely."
            )
        }
        
        base_strategy = strategies.get(action, "Unknown action")
        
        # Add risk context if significant risks exist
        if len(risk_factors) > 2 and action in ["RECOMMEND", "MONITOR"]:
            base_strategy += " Note: Multiple risk factors require attention."
        
        return base_strategy
    
    def batch_advise(self, suppliers_data: List[Dict]) -> List[Dict]:
        """
        Generate procurement advice for multiple suppliers.
        
        Args:
            suppliers_data: List of supplier data dictionaries
            
        Returns:
            List of advisory results, sorted by confidence (descending)
        """
        results = [self.advise(supplier) for supplier in suppliers_data]
        
        # Sort by action priority and confidence
        action_priority = {"RECOMMEND": 0, "MONITOR": 1, "REVIEW": 2, "REJECT": 3}
        results.sort(key=lambda x: (action_priority.get(x['action'], 4), -x['confidence']))
        
        return results
    
    def compare_suppliers(self, supplier_a: Dict, supplier_b: Dict) -> Dict:
        """
        Compare two suppliers and recommend the better option.
        
        Args:
            supplier_a: First supplier data
            supplier_b: Second supplier data
            
        Returns:
            Comparison analysis with recommendation
        """
        advice_a = self.advise(supplier_a)
        advice_b = self.advise(supplier_b)
        
        # Determine winner
        if advice_a['confidence'] > advice_b['confidence'] + 0.1:
            recommended = supplier_a.get('supplier_id', 'Supplier A')
            reasoning = f"Supplier A has significantly higher confidence ({advice_a['confidence']:.2f} vs {advice_b['confidence']:.2f})"
        elif advice_b['confidence'] > advice_a['confidence'] + 0.1:
            recommended = supplier_b.get('supplier_id', 'Supplier B')
            reasoning = f"Supplier B has significantly higher confidence ({advice_b['confidence']:.2f} vs {advice_a['confidence']:.2f})"
        else:
            # Close call - use other factors
            if advice_a['action'] == "RECOMMEND" and advice_b['action'] != "RECOMMEND":
                recommended = supplier_a.get('supplier_id', 'Supplier A')
                reasoning = "Supplier A has a clearer recommendation despite similar confidence"
            elif advice_b['action'] == "RECOMMEND" and advice_a['action'] != "RECOMMEND":
                recommended = supplier_b.get('supplier_id', 'Supplier B')
                reasoning = "Supplier B has a clearer recommendation despite similar confidence"
            else:
                recommended = "NEUTRAL"
                reasoning = "Both suppliers have similar performance profiles. Consider other factors like capacity and location."
        
        return {
            'recommended_supplier': recommended,
            'reasoning': reasoning,
            'supplier_a_analysis': advice_a,
            'supplier_b_analysis': advice_b,
            'key_differentiators': self._identify_differentiators(supplier_a, supplier_b)
        }
    
    def _identify_differentiators(self, supplier_a: Dict, supplier_b: Dict) -> List[str]:
        """Identify key differences between two suppliers."""
        diffs = []
        
        quality_diff = abs(
            supplier_a.get('quality_score', 0.5) - supplier_b.get('quality_score', 0.5)
        )
        if quality_diff > 0.1:
            diffs.append(f"Significant quality difference ({quality_diff*100:.0f}% points)")
        
        delivery_diff = abs(
            supplier_a.get('on_time_delivery_rate', 0.5) - supplier_b.get('on_time_delivery_rate', 0.5)
        )
        if delivery_diff > 0.1:
            diffs.append(f"Notable delivery performance gap ({delivery_diff*100:.0f}% points)")
        
        price_diff = abs(
            supplier_a.get('price_competitiveness', 0.5) - supplier_b.get('price_competitiveness', 0.5)
        )
        if price_diff > 0.15:
            diffs.append(f"Substantial price difference ({price_diff*100:.0f}% points)")
        
        if not diffs:
            diffs.append("Suppliers have similar performance profiles")
        
        return diffs
