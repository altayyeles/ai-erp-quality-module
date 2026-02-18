"""
Alert System Module

This module implements an in-memory alert management system for
quality and maintenance notifications.

Key Features:
- Alert creation with severity levels (INFO/WARNING/CRITICAL)
- Active alert tracking
- Alert dismissal
- Source tracking (quality, maintenance, supplier, vision)
- Timestamp tracking
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from threading import Lock

logger = logging.getLogger(__name__)


@dataclass
class Alert:
    """Alert data structure."""
    id: int
    title: str
    message: str
    severity: str  # INFO, WARNING, CRITICAL
    source: str    # quality, maintenance, supplier, vision, system
    timestamp: str
    is_active: bool = True


class AlertSystem:
    """
    In-memory alert management system.
    
    Manages alerts for quality, maintenance, and operational issues
    with severity levels and source tracking.
    """
    
    SEVERITY_LEVELS = ['INFO', 'WARNING', 'CRITICAL']
    VALID_SOURCES = ['quality', 'maintenance', 'supplier', 'vision', 'dashboard', 'system']
    
    def __init__(self):
        """Initialize the alert system with in-memory storage."""
        self.alerts: List[Alert] = []
        self.next_id = 1
        self.lock = Lock()
        
        logger.info("AlertSystem initialized with in-memory storage")
        
        # Create some demo alerts for demonstration
        self._create_demo_alerts()
    
    def get_active_alerts(self) -> List[Dict]:
        """
        Get all active alerts.
        
        Returns:
            List of active alert dictionaries, sorted by severity and timestamp
        """
        with self.lock:
            active = [alert for alert in self.alerts if alert.is_active]
            
            # Sort by severity (CRITICAL > WARNING > INFO) and then by timestamp
            severity_order = {'CRITICAL': 0, 'WARNING': 1, 'INFO': 2}
            active.sort(key=lambda a: (severity_order.get(a.severity, 3), a.timestamp))
            
            result = [asdict(alert) for alert in active]
            
            logger.info(f"Retrieved {len(result)} active alerts")
            return result
    
    def get_all_alerts(self) -> List[Dict]:
        """
        Get all alerts (active and dismissed).
        
        Returns:
            List of all alert dictionaries
        """
        with self.lock:
            result = [asdict(alert) for alert in self.alerts]
            logger.info(f"Retrieved {len(result)} total alerts")
            return result
    
    def create_alert(
        self,
        title: str,
        message: str,
        severity: str,
        source: str
    ) -> Dict:
        """
        Create a new alert.
        
        Args:
            title: Alert title
            message: Alert message/description
            severity: Severity level (INFO/WARNING/CRITICAL)
            source: Source module (quality/maintenance/supplier/vision/system)
            
        Returns:
            Created alert as dictionary
            
        Raises:
            ValueError: If severity or source is invalid
        """
        # Validate inputs
        severity = severity.upper()
        if severity not in self.SEVERITY_LEVELS:
            raise ValueError(f"Invalid severity: {severity}. Must be one of {self.SEVERITY_LEVELS}")
        
        source = source.lower()
        if source not in self.VALID_SOURCES:
            raise ValueError(f"Invalid source: {source}. Must be one of {self.VALID_SOURCES}")
        
        with self.lock:
            alert = Alert(
                id=self.next_id,
                title=title,
                message=message,
                severity=severity,
                source=source,
                timestamp=datetime.now().isoformat(),
                is_active=True
            )
            
            self.alerts.append(alert)
            self.next_id += 1
            
            logger.info(f"✓ Created {severity} alert #{alert.id} from {source}: {title}")
            
            return asdict(alert)
    
    def dismiss_alert(self, alert_id: int) -> None:
        """
        Dismiss an active alert.
        
        Args:
            alert_id: ID of the alert to dismiss
            
        Raises:
            ValueError: If alert not found
        """
        with self.lock:
            alert = self._find_alert(alert_id)
            
            if alert is None:
                raise ValueError(f"Alert {alert_id} not found")
            
            if not alert.is_active:
                logger.warning(f"Alert {alert_id} already dismissed")
                return
            
            alert.is_active = False
            logger.info(f"✓ Alert {alert_id} dismissed")
    
    def get_alert(self, alert_id: int) -> Optional[Dict]:
        """
        Get a specific alert by ID.
        
        Args:
            alert_id: Alert ID
            
        Returns:
            Alert dictionary or None if not found
        """
        with self.lock:
            alert = self._find_alert(alert_id)
            return asdict(alert) if alert else None
    
    def get_alerts_by_severity(self, severity: str) -> List[Dict]:
        """
        Get all active alerts of a specific severity.
        
        Args:
            severity: Severity level (INFO/WARNING/CRITICAL)
            
        Returns:
            List of matching alert dictionaries
        """
        severity = severity.upper()
        with self.lock:
            filtered = [
                alert for alert in self.alerts
                if alert.is_active and alert.severity == severity
            ]
            return [asdict(alert) for alert in filtered]
    
    def get_alerts_by_source(self, source: str) -> List[Dict]:
        """
        Get all active alerts from a specific source.
        
        Args:
            source: Source module
            
        Returns:
            List of matching alert dictionaries
        """
        source = source.lower()
        with self.lock:
            filtered = [
                alert for alert in self.alerts
                if alert.is_active and alert.source == source
            ]
            return [asdict(alert) for alert in filtered]
    
    def clear_all_alerts(self) -> int:
        """
        Dismiss all active alerts.
        
        Returns:
            Number of alerts dismissed
        """
        with self.lock:
            count = 0
            for alert in self.alerts:
                if alert.is_active:
                    alert.is_active = False
                    count += 1
            
            logger.info(f"✓ Dismissed {count} alerts")
            return count
    
    def get_alert_stats(self) -> Dict:
        """
        Get statistics about alerts.
        
        Returns:
            Dictionary with alert statistics
        """
        with self.lock:
            total = len(self.alerts)
            active = len([a for a in self.alerts if a.is_active])
            dismissed = total - active
            
            active_by_severity = {
                'CRITICAL': len([a for a in self.alerts if a.is_active and a.severity == 'CRITICAL']),
                'WARNING': len([a for a in self.alerts if a.is_active and a.severity == 'WARNING']),
                'INFO': len([a for a in self.alerts if a.is_active and a.severity == 'INFO'])
            }
            
            active_by_source = {}
            for source in self.VALID_SOURCES:
                count = len([a for a in self.alerts if a.is_active and a.source == source])
                if count > 0:
                    active_by_source[source] = count
            
            return {
                'total_alerts': total,
                'active_alerts': active,
                'dismissed_alerts': dismissed,
                'active_by_severity': active_by_severity,
                'active_by_source': active_by_source
            }
    
    def _find_alert(self, alert_id: int) -> Optional[Alert]:
        """Find an alert by ID (not thread-safe, use within lock)."""
        for alert in self.alerts:
            if alert.id == alert_id:
                return alert
        return None
    
    def _create_demo_alerts(self) -> None:
        """Create demo alerts for demonstration purposes."""
        demo_alerts = [
            {
                'title': 'High Defect Rate Detected',
                'message': 'Machine M005 showing defect rate above 5% threshold',
                'severity': 'WARNING',
                'source': 'quality'
            },
            {
                'title': 'Machine M003 Requires Maintenance',
                'message': 'RUL prediction indicates maintenance needed within 24 hours',
                'severity': 'CRITICAL',
                'source': 'maintenance'
            },
            {
                'title': 'Supplier Quality Issue',
                'message': 'Supplier SUP-005 quality score dropped below 70%',
                'severity': 'WARNING',
                'source': 'supplier'
            },
            {
                'title': 'Visual Inspection Alert',
                'message': 'Multiple defects detected in recent batch inspection',
                'severity': 'INFO',
                'source': 'vision'
            },
            {
                'title': 'OEE Below Target',
                'message': 'Overall Equipment Effectiveness at 78%, below target of 85%',
                'severity': 'WARNING',
                'source': 'dashboard'
            }
        ]
        
        for alert_data in demo_alerts:
            try:
                self.create_alert(**alert_data)
            except Exception as e:
                logger.error(f"Error creating demo alert: {e}")


def create_demo_alert_system() -> AlertSystem:
    """
    Create a demo alert system with sample alerts.
    
    Returns:
        Initialized AlertSystem
    """
    return AlertSystem()
