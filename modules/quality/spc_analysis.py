"""
Statistical Process Control (SPC) Analysis Module

Implements various SPC techniques for quality monitoring:
- Shewhart control charts (X-bar, R, p-charts)
- CUSUM (Cumulative Sum) analysis
- Western Electric rules for out-of-control detection
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ControlChartType(Enum):
    """Types of control charts"""
    XBAR = "X-bar"  # Mean chart
    R = "R"  # Range chart
    P = "p"  # Proportion chart
    CUSUM = "CUSUM"  # Cumulative sum chart


class ViolationType(Enum):
    """Western Electric rules violation types"""
    BEYOND_3SIGMA = "Point beyond 3σ"
    TWO_OF_THREE_BEYOND_2SIGMA = "2 out of 3 beyond 2σ"
    FOUR_OF_FIVE_BEYOND_1SIGMA = "4 out of 5 beyond 1σ"
    EIGHT_CONSECUTIVE_SAME_SIDE = "8 consecutive points on same side of center"
    SIX_CONSECUTIVE_TREND = "6 consecutive increasing or decreasing"
    FIFTEEN_CONSECUTIVE_NEAR_CENTER = "15 consecutive within 1σ"


@dataclass
class SPCResult:
    """Container for SPC analysis results"""
    chart_type: str
    center_line: float
    ucl: float  # Upper Control Limit
    lcl: float  # Lower Control Limit
    usl: Optional[float] = None  # Upper Specification Limit
    lsl: Optional[float] = None  # Lower Specification Limit
    out_of_control_points: List[int] = None
    violations: List[Tuple[int, str]] = None
    process_capability: Optional[Dict[str, float]] = None
    
    def __post_init__(self):
        if self.out_of_control_points is None:
            self.out_of_control_points = []
        if self.violations is None:
            self.violations = []


class SPCAnalyzer:
    """
    Statistical Process Control analyzer for quality monitoring.
    
    Provides various SPC techniques including control charts,
    Western Electric rules, and process capability analysis.
    """
    
    def __init__(self):
        """Initialize SPC Analyzer"""
        self.sigma_multiplier = 3  # Standard 3-sigma control limits
    
    def analyze_xbar(
        self,
        data: pd.Series,
        subgroup_size: int = 5,
        usl: Optional[float] = None,
        lsl: Optional[float] = None
    ) -> SPCResult:
        """
        Perform X-bar (mean) chart analysis.
        
        Args:
            data: Process measurements
            subgroup_size: Number of samples per subgroup
            usl: Upper Specification Limit
            lsl: Lower Specification Limit
            
        Returns:
            SPCResult with control limits and violations
        """
        # Calculate subgroup means
        n_subgroups = len(data) // subgroup_size
        subgroups = [data[i*subgroup_size:(i+1)*subgroup_size] for i in range(n_subgroups)]
        subgroup_means = [np.mean(sg) for sg in subgroups]
        
        # Calculate control limits
        grand_mean = np.mean(subgroup_means)
        
        # Estimate sigma from average range
        ranges = [np.max(sg) - np.min(sg) for sg in subgroups]
        avg_range = np.mean(ranges)
        
        # d2 constant for subgroup size
        d2_values = {2: 1.128, 3: 1.693, 4: 2.059, 5: 2.326, 6: 2.534, 7: 2.704, 8: 2.847, 9: 2.970, 10: 3.078}
        d2 = d2_values.get(subgroup_size, 2.326)
        
        sigma_estimate = avg_range / d2
        ucl = grand_mean + 3 * (sigma_estimate / np.sqrt(subgroup_size))
        lcl = grand_mean - 3 * (sigma_estimate / np.sqrt(subgroup_size))
        
        # Detect violations
        violations = self._apply_western_electric_rules(subgroup_means, grand_mean, ucl, lcl)
        out_of_control_points = [idx for idx, _ in violations]
        
        # Calculate process capability if spec limits provided
        process_capability = None
        if usl is not None and lsl is not None:
            process_capability = self._calculate_capability(data, usl, lsl)
        
        return SPCResult(
            chart_type=ControlChartType.XBAR.value,
            center_line=grand_mean,
            ucl=ucl,
            lcl=lcl,
            usl=usl,
            lsl=lsl,
            out_of_control_points=out_of_control_points,
            violations=violations,
            process_capability=process_capability
        )
    
    def analyze_r_chart(
        self,
        data: pd.Series,
        subgroup_size: int = 5
    ) -> SPCResult:
        """
        Perform R (range) chart analysis.
        
        Args:
            data: Process measurements
            subgroup_size: Number of samples per subgroup
            
        Returns:
            SPCResult with control limits
        """
        # Calculate subgroup ranges
        n_subgroups = len(data) // subgroup_size
        subgroups = [data[i*subgroup_size:(i+1)*subgroup_size] for i in range(n_subgroups)]
        ranges = [np.max(sg) - np.min(sg) for sg in subgroups]
        
        # Calculate control limits
        avg_range = np.mean(ranges)
        
        # D3 and D4 constants for subgroup size
        d3_values = {2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0.076, 8: 0.136, 9: 0.184, 10: 0.223}
        d4_values = {2: 3.267, 3: 2.574, 4: 2.282, 5: 2.114, 6: 2.004, 7: 1.924, 8: 1.864, 9: 1.816, 10: 1.777}
        
        d3 = d3_values.get(subgroup_size, 0)
        d4 = d4_values.get(subgroup_size, 2.114)
        
        ucl = d4 * avg_range
        lcl = d3 * avg_range
        
        # Detect out of control points
        out_of_control_points = [i for i, r in enumerate(ranges) if r > ucl or r < lcl]
        
        return SPCResult(
            chart_type=ControlChartType.R.value,
            center_line=avg_range,
            ucl=ucl,
            lcl=lcl,
            out_of_control_points=out_of_control_points
        )
    
    def analyze_p_chart(
        self,
        defects: pd.Series,
        sample_sizes: pd.Series
    ) -> SPCResult:
        """
        Perform p-chart (proportion defective) analysis.
        
        Args:
            defects: Number of defects in each sample
            sample_sizes: Size of each sample
            
        Returns:
            SPCResult with control limits
        """
        # Calculate proportions
        proportions = defects / sample_sizes
        p_bar = defects.sum() / sample_sizes.sum()
        
        # Average sample size
        n_bar = sample_sizes.mean()
        
        # Calculate control limits
        ucl = p_bar + 3 * np.sqrt(p_bar * (1 - p_bar) / n_bar)
        lcl = max(0, p_bar - 3 * np.sqrt(p_bar * (1 - p_bar) / n_bar))
        
        # Detect out of control points
        out_of_control_points = [i for i, p in enumerate(proportions) if p > ucl or p < lcl]
        
        return SPCResult(
            chart_type=ControlChartType.P.value,
            center_line=p_bar,
            ucl=ucl,
            lcl=lcl,
            out_of_control_points=out_of_control_points
        )
    
    def analyze_cusum(
        self,
        data: pd.Series,
        target: Optional[float] = None,
        k: float = 0.5,
        h: float = 5
    ) -> Dict:
        """
        Perform CUSUM (Cumulative Sum) analysis.
        
        Args:
            data: Process measurements
            target: Target value (uses mean if not provided)
            k: Reference value (typically 0.5 * sigma)
            h: Decision interval (typically 4-5 * sigma)
            
        Returns:
            Dictionary with CUSUM statistics
        """
        if target is None:
            target = data.mean()
        
        sigma = data.std()
        k = k * sigma
        h = h * sigma
        
        # Calculate CUSUM
        c_plus = [0]  # Upper CUSUM
        c_minus = [0]  # Lower CUSUM
        
        for value in data:
            c_plus.append(max(0, c_plus[-1] + (value - target) - k))
            c_minus.append(max(0, c_minus[-1] - (value - target) - k))
        
        c_plus = c_plus[1:]
        c_minus = c_minus[1:]
        
        # Detect out of control points
        out_of_control_points = [
            i for i, (cp, cm) in enumerate(zip(c_plus, c_minus))
            if cp > h or cm > h
        ]
        
        return {
            'c_plus': c_plus,
            'c_minus': c_minus,
            'h': h,
            'out_of_control_points': out_of_control_points
        }
    
    def _apply_western_electric_rules(
        self,
        data: List[float],
        center_line: float,
        ucl: float,
        lcl: float
    ) -> List[Tuple[int, str]]:
        """
        Apply Western Electric rules to detect special causes.
        
        Returns:
            List of (index, violation_type) tuples
        """
        violations = []
        sigma = (ucl - center_line) / 3
        
        # Rule 1: Point beyond 3σ
        for i, value in enumerate(data):
            if value > ucl or value < lcl:
                violations.append((i, ViolationType.BEYOND_3SIGMA.value))
        
        # Rule 2: 2 out of 3 consecutive points beyond 2σ
        for i in range(len(data) - 2):
            points = data[i:i+3]
            beyond_2sigma = sum(1 for p in points if abs(p - center_line) > 2 * sigma)
            if beyond_2sigma >= 2:
                violations.append((i+2, ViolationType.TWO_OF_THREE_BEYOND_2SIGMA.value))
        
        # Rule 3: 4 out of 5 consecutive points beyond 1σ
        for i in range(len(data) - 4):
            points = data[i:i+5]
            beyond_1sigma = sum(1 for p in points if abs(p - center_line) > sigma)
            if beyond_1sigma >= 4:
                violations.append((i+4, ViolationType.FOUR_OF_FIVE_BEYOND_1SIGMA.value))
        
        # Rule 4: 8 consecutive points on same side of center
        for i in range(len(data) - 7):
            points = data[i:i+8]
            all_above = all(p > center_line for p in points)
            all_below = all(p < center_line for p in points)
            if all_above or all_below:
                violations.append((i+7, ViolationType.EIGHT_CONSECUTIVE_SAME_SIDE.value))
        
        return violations
    
    def _calculate_capability(
        self,
        data: pd.Series,
        usl: float,
        lsl: float
    ) -> Dict[str, float]:
        """Calculate process capability indices."""
        mean = data.mean()
        sigma = data.std()
        
        # Cp: Potential capability
        cp = (usl - lsl) / (6 * sigma)
        
        # Cpk: Actual capability
        cpk = min((usl - mean) / (3 * sigma), (mean - lsl) / (3 * sigma))
        
        # Pp and Ppk (performance indices)
        pp = (usl - lsl) / (6 * sigma)
        ppk = min((usl - mean) / (3 * sigma), (mean - lsl) / (3 * sigma))
        
        return {
            'Cp': float(cp),
            'Cpk': float(cpk),
            'Pp': float(pp),
            'Ppk': float(ppk)
        }
