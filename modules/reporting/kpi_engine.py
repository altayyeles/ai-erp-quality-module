"""
KPI Engine Module

This module calculates key performance indicators (KPIs) for manufacturing
quality management.

Key Features:
- OEE (Overall Equipment Effectiveness)
- FPY (First Pass Yield)
- DPMO (Defects Per Million Opportunities)
- Cpk (Process Capability Index)
- Target comparison and status tracking
- Trend analysis
"""

import logging
import numpy as np
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)


class KPIEngine:
    """
    KPI calculation engine for manufacturing quality metrics.
    
    Calculates and tracks key performance indicators with targets,
    status assessment, and trend analysis.
    """
    
    def __init__(self):
        """Initialize the KPI engine."""
        logger.info("KPIEngine initialized")
        
        # KPI targets (industry standards)
        self.targets = {
            'oee': 85.0,      # 85% is world-class
            'fpy': 95.0,      # 95% first pass yield
            'dpmo': 35000,    # Defects per million opportunities
            'cpk': 1.33       # Process capability index
        }
    
    def get_snapshot(self) -> Dict:
        """
        Get current KPI snapshot.
        
        Returns:
            Dictionary containing all KPIs with values, targets, status, and trends
        """
        logger.info("Calculating KPI snapshot...")
        
        # Calculate current KPIs (simulated values with some randomness)
        # In production, these would come from real data sources
        current_kpis = self._calculate_current_kpis()
        
        # Build comprehensive snapshot
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'kpis': {
                'oee': self._build_kpi_detail(
                    'OEE',
                    'Overall Equipment Effectiveness',
                    current_kpis['oee'],
                    self.targets['oee'],
                    '%',
                    higher_is_better=True
                ),
                'fpy': self._build_kpi_detail(
                    'FPY',
                    'First Pass Yield',
                    current_kpis['fpy'],
                    self.targets['fpy'],
                    '%',
                    higher_is_better=True
                ),
                'dpmo': self._build_kpi_detail(
                    'DPMO',
                    'Defects Per Million Opportunities',
                    current_kpis['dpmo'],
                    self.targets['dpmo'],
                    'defects',
                    higher_is_better=False
                ),
                'cpk': self._build_kpi_detail(
                    'Cpk',
                    'Process Capability Index',
                    current_kpis['cpk'],
                    self.targets['cpk'],
                    '',
                    higher_is_better=True
                )
            },
            'summary': self._generate_summary(current_kpis)
        }
        
        logger.info("✓ KPI snapshot generated")
        
        return snapshot
    
    def _calculate_current_kpis(self) -> Dict[str, float]:
        """
        Calculate current KPI values.
        
        In production, this would query real databases and calculate from actual data.
        For demo purposes, we generate realistic simulated values.
        
        Returns:
            Dictionary with current KPI values
        """
        # Use current time for variation
        np.random.seed(int(datetime.now().timestamp()) % 1000)
        
        # Simulate OEE (typically 75-95%)
        # OEE = Availability × Performance × Quality
        availability = np.random.normal(0.92, 0.03)
        performance = np.random.normal(0.95, 0.02)
        quality = np.random.normal(0.98, 0.01)
        oee = availability * performance * quality * 100
        oee = np.clip(oee, 70, 99)
        
        # Simulate FPY (typically 90-99%)
        fpy = np.random.normal(96.5, 1.5)
        fpy = np.clip(fpy, 85, 99.5)
        
        # Simulate DPMO (typically 20,000-50,000 for good processes)
        dpmo = np.random.normal(32000, 5000)
        dpmo = np.clip(dpmo, 15000, 60000)
        
        # Simulate Cpk (typically 1.0-2.0 for capable processes)
        cpk = np.random.normal(1.45, 0.15)
        cpk = np.clip(cpk, 0.8, 2.0)
        
        return {
            'oee': round(float(oee), 2),
            'fpy': round(float(fpy), 2),
            'dpmo': round(float(dpmo), 0),
            'cpk': round(float(cpk), 2)
        }
    
    def _build_kpi_detail(
        self,
        name: str,
        description: str,
        value: float,
        target: float,
        unit: str,
        higher_is_better: bool = True
    ) -> Dict:
        """
        Build detailed KPI information.
        
        Args:
            name: KPI short name
            description: Full description
            value: Current value
            target: Target value
            unit: Unit of measurement
            higher_is_better: Whether higher values are better
            
        Returns:
            Dictionary with complete KPI details
        """
        # Calculate performance vs target
        if higher_is_better:
            performance_ratio = value / target
            deviation = value - target
        else:
            performance_ratio = target / value
            deviation = target - value
        
        # Determine status
        if performance_ratio >= 1.0:
            status = "GOOD"
        elif performance_ratio >= 0.95:
            status = "WARNING"
        else:
            status = "CRITICAL"
        
        # Simulate trend (for demo)
        # In production, this would be calculated from historical data
        trend_value = np.random.uniform(-3, 5)
        if abs(trend_value) < 1:
            trend = "STABLE"
        elif trend_value > 0:
            trend = "IMPROVING"
        else:
            trend = "DECLINING"
        
        return {
            'name': name,
            'description': description,
            'value': value,
            'target': target,
            'unit': unit,
            'status': status,
            'performance_ratio': round(performance_ratio, 3),
            'deviation': round(deviation, 2),
            'trend': trend,
            'trend_value': round(trend_value, 2)
        }
    
    def _generate_summary(self, kpis: Dict[str, float]) -> Dict:
        """
        Generate overall summary of KPI performance.
        
        Args:
            kpis: Dictionary of current KPI values
            
        Returns:
            Summary dictionary
        """
        # Count how many KPIs meet targets
        targets_met = 0
        total_kpis = 4
        
        if kpis['oee'] >= self.targets['oee']:
            targets_met += 1
        if kpis['fpy'] >= self.targets['fpy']:
            targets_met += 1
        if kpis['dpmo'] <= self.targets['dpmo']:
            targets_met += 1
        if kpis['cpk'] >= self.targets['cpk']:
            targets_met += 1
        
        # Overall performance
        performance_percentage = (targets_met / total_kpis) * 100
        
        if targets_met == total_kpis:
            overall_status = "EXCELLENT"
            message = "All KPIs meeting or exceeding targets. Outstanding performance!"
        elif targets_met >= 3:
            overall_status = "GOOD"
            message = "Most KPIs on target. Minor improvements needed."
        elif targets_met >= 2:
            overall_status = "FAIR"
            message = "Some KPIs below target. Action required."
        else:
            overall_status = "POOR"
            message = "Multiple KPIs below target. Immediate attention needed."
        
        return {
            'overall_status': overall_status,
            'targets_met': targets_met,
            'total_kpis': total_kpis,
            'performance_percentage': round(performance_percentage, 1),
            'message': message
        }
    
    def calculate_oee(
        self,
        availability: float,
        performance: float,
        quality: float
    ) -> float:
        """
        Calculate Overall Equipment Effectiveness.
        
        Args:
            availability: Equipment availability (0-1)
            performance: Performance rate (0-1)
            quality: Quality rate (0-1)
            
        Returns:
            OEE as percentage (0-100)
        """
        oee = availability * performance * quality * 100
        return round(oee, 2)
    
    def calculate_fpy(self, passed_units: int, total_units: int) -> float:
        """
        Calculate First Pass Yield.
        
        Args:
            passed_units: Number of units that passed first time
            total_units: Total number of units produced
            
        Returns:
            FPY as percentage (0-100)
        """
        if total_units == 0:
            return 0.0
        fpy = (passed_units / total_units) * 100
        return round(fpy, 2)
    
    def calculate_dpmo(self, defects: int, units: int, opportunities: int) -> float:
        """
        Calculate Defects Per Million Opportunities.
        
        Args:
            defects: Number of defects found
            units: Number of units inspected
            opportunities: Number of defect opportunities per unit
            
        Returns:
            DPMO value
        """
        if units == 0 or opportunities == 0:
            return 0.0
        dpmo = (defects / (units * opportunities)) * 1_000_000
        return round(dpmo, 0)
    
    def calculate_cpk(self, mean: float, std: float, usl: float, lsl: float) -> float:
        """
        Calculate Process Capability Index.
        
        Args:
            mean: Process mean
            std: Process standard deviation
            usl: Upper specification limit
            lsl: Lower specification limit
            
        Returns:
            Cpk value
        """
        if std == 0:
            return 0.0
        
        cpu = (usl - mean) / (3 * std)
        cpl = (mean - lsl) / (3 * std)
        cpk = min(cpu, cpl)
        
        return round(cpk, 2)


def create_demo_kpi_engine() -> KPIEngine:
    """
    Create a demo KPI engine.
    
    Returns:
        Initialized KPIEngine
    """
    return KPIEngine()
