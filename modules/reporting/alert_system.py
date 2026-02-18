"""
Alert System with SQLite Backend
Manages quality and maintenance alerts with severity levels
"""

import logging
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AlertSystem:
    """
    Alert management system with SQLite backend.
    
    Manages alerts with different severity levels:
    - INFO: Informational messages
    - WARNING: Potential issues requiring attention
    - ERROR: Problems that need resolution
    - CRITICAL: Urgent issues requiring immediate action
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize Alert System.
        
        Args:
            db_path: Path to SQLite database for alerts
        """
        self.db_path = db_path or Path("data/alerts.db")
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Create database and tables if they don't exist."""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Create alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    source TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    is_dismissed INTEGER DEFAULT 0,
                    dismissed_at TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            # Create some demo alerts if empty
            self._create_demo_alerts()
            
            logger.info(f"✓ Alert system initialized at {self.db_path}")
        
        except Exception as e:
            logger.error(f"Failed to initialize alert system: {e}")
    
    def _create_demo_alerts(self):
        """Create demo alerts if database is empty."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Check if alerts exist
            cursor.execute("SELECT COUNT(*) FROM alerts WHERE is_dismissed = 0")
            count = cursor.fetchone()[0]
            
            if count == 0:
                logger.info("Creating demo alerts...")
                
                demo_alerts = [
                    {
                        'title': 'High Defect Rate Detected',
                        'message': 'Machine M005 showing defect rate of 8.2% (threshold: 5%). Immediate inspection recommended.',
                        'severity': 'CRITICAL',
                        'source': 'Quality Module'
                    },
                    {
                        'title': 'Maintenance Due for M007',
                        'message': 'Machine M007 has reached 95% of predicted RUL. Schedule maintenance within 48 hours.',
                        'severity': 'WARNING',
                        'source': 'Maintenance Module'
                    },
                    {
                        'title': 'Supplier Performance Issue',
                        'message': 'Supplier SUP-023 on-time delivery rate dropped to 78% (target: 90%). Review required.',
                        'severity': 'WARNING',
                        'source': 'Supplier Module'
                    },
                    {
                        'title': 'Vision System Alert',
                        'message': 'Multiple defects detected in batch #4521. Manual inspection recommended for confirmation.',
                        'severity': 'ERROR',
                        'source': 'Vision Module'
                    },
                    {
                        'title': 'OEE Below Target',
                        'message': 'Overall Equipment Effectiveness dropped to 82.3% (target: 85%). Investigate availability issues.',
                        'severity': 'WARNING',
                        'source': 'KPI Engine'
                    },
                    {
                        'title': 'Tool Wear Threshold Exceeded',
                        'message': 'Machine M002 tool wear at 235 minutes (threshold: 220). Replace cutting tools immediately.',
                        'severity': 'CRITICAL',
                        'source': 'Maintenance Module'
                    },
                    {
                        'title': 'System Health Check',
                        'message': 'All systems operational. Last backup completed successfully at 02:00 AM.',
                        'severity': 'INFO',
                        'source': 'System'
                    },
                    {
                        'title': 'Temperature Anomaly',
                        'message': 'Machine M004 process temperature elevated at 314.5K (normal: 308K). Check cooling system.',
                        'severity': 'WARNING',
                        'source': 'Quality Module'
                    }
                ]
                
                for alert in demo_alerts:
                    self.create_alert(
                        title=alert['title'],
                        message=alert['message'],
                        severity=alert['severity'],
                        source=alert['source']
                    )
                
                logger.info("✓ Demo alerts created successfully")
            
            conn.close()
        
        except Exception as e:
            logger.error(f"Failed to create demo alerts: {e}")
    
    def get_active_alerts(self, severity: Optional[str] = None) -> List[Dict]:
        """
        Get all active (non-dismissed) alerts.
        
        Args:
            severity: Optional severity filter (INFO, WARNING, ERROR, CRITICAL)
            
        Returns:
            List of active alert dictionaries
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            if severity:
                query = '''
                    SELECT id, title, message, severity, source, created_at
                    FROM alerts
                    WHERE is_dismissed = 0 AND severity = ?
                    ORDER BY 
                        CASE severity
                            WHEN 'CRITICAL' THEN 1
                            WHEN 'ERROR' THEN 2
                            WHEN 'WARNING' THEN 3
                            WHEN 'INFO' THEN 4
                        END,
                        created_at DESC
                '''
                cursor.execute(query, (severity.upper(),))
            else:
                query = '''
                    SELECT id, title, message, severity, source, created_at
                    FROM alerts
                    WHERE is_dismissed = 0
                    ORDER BY 
                        CASE severity
                            WHEN 'CRITICAL' THEN 1
                            WHEN 'ERROR' THEN 2
                            WHEN 'WARNING' THEN 3
                            WHEN 'INFO' THEN 4
                        END,
                        created_at DESC
                '''
                cursor.execute(query)
            
            rows = cursor.fetchall()
            conn.close()
            
            alerts = []
            for row in rows:
                alert_id, title, message, severity, source, created_at = row
                alerts.append({
                    'id': alert_id,
                    'title': title,
                    'message': message,
                    'severity': severity,
                    'source': source,
                    'created_at': created_at
                })
            
            return alerts
        
        except Exception as e:
            logger.error(f"Failed to get active alerts: {e}")
            return []
    
    def get_all_alerts(self, include_dismissed: bool = False) -> List[Dict]:
        """
        Get all alerts.
        
        Args:
            include_dismissed: Whether to include dismissed alerts
            
        Returns:
            List of all alert dictionaries
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            if include_dismissed:
                query = '''
                    SELECT id, title, message, severity, source, created_at, is_dismissed, dismissed_at
                    FROM alerts
                    ORDER BY created_at DESC
                '''
            else:
                query = '''
                    SELECT id, title, message, severity, source, created_at, is_dismissed, dismissed_at
                    FROM alerts
                    WHERE is_dismissed = 0
                    ORDER BY created_at DESC
                '''
            
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()
            
            alerts = []
            for row in rows:
                alert_id, title, message, severity, source, created_at, is_dismissed, dismissed_at = row
                alerts.append({
                    'id': alert_id,
                    'title': title,
                    'message': message,
                    'severity': severity,
                    'source': source,
                    'created_at': created_at,
                    'is_dismissed': bool(is_dismissed),
                    'dismissed_at': dismissed_at
                })
            
            return alerts
        
        except Exception as e:
            logger.error(f"Failed to get all alerts: {e}")
            return []
    
    def create_alert(
        self,
        title: str,
        message: str,
        severity: str,
        source: str
    ) -> int:
        """
        Create a new alert.
        
        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity (INFO, WARNING, ERROR, CRITICAL)
            source: Alert source (e.g., 'Quality Module', 'Maintenance Module')
            
        Returns:
            Alert ID
        """
        try:
            # Validate severity
            valid_severities = ['INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if severity.upper() not in valid_severities:
                raise ValueError(f"Invalid severity. Must be one of {valid_severities}")
            
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            created_at = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO alerts (title, message, severity, source, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, message, severity.upper(), source, created_at))
            
            alert_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            logger.info(f"✓ Alert created: [{severity}] {title}")
            
            return alert_id
        
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
            raise
    
    def dismiss_alert(self, alert_id: int) -> None:
        """
        Dismiss an alert by ID.
        
        Args:
            alert_id: Alert ID to dismiss
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            dismissed_at = datetime.now().isoformat()
            
            cursor.execute('''
                UPDATE alerts
                SET is_dismissed = 1, dismissed_at = ?
                WHERE id = ?
            ''', (dismissed_at, alert_id))
            
            if cursor.rowcount == 0:
                conn.close()
                raise ValueError(f"Alert {alert_id} not found")
            
            conn.commit()
            conn.close()
            
            logger.info(f"✓ Alert {alert_id} dismissed")
        
        except Exception as e:
            logger.error(f"Failed to dismiss alert: {e}")
            raise
    
    def get_alert_count_by_severity(self) -> Dict[str, int]:
        """
        Get count of active alerts by severity.
        
        Returns:
            Dictionary with severity counts
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT severity, COUNT(*) as count
                FROM alerts
                WHERE is_dismissed = 0
                GROUP BY severity
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            counts = {
                'CRITICAL': 0,
                'ERROR': 0,
                'WARNING': 0,
                'INFO': 0
            }
            
            for severity, count in rows:
                counts[severity] = count
            
            return counts
        
        except Exception as e:
            logger.error(f"Failed to get alert counts: {e}")
            return {'CRITICAL': 0, 'ERROR': 0, 'WARNING': 0, 'INFO': 0}
