"""
Alert Management System
SQLite-based alert queue and notification system

This module manages alerts for quality issues, maintenance needs,
and other critical events in the manufacturing process.
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
    
    Manages creation, retrieval, and dismissal of alerts for
    quality issues, maintenance needs, and process anomalies.
    """
    
    SEVERITY_LEVELS = ['INFO', 'WARNING', 'ERROR', 'CRITICAL']
    
    def __init__(self, db_path: str = None):
        """
        Initialize Alert System.
        
        Args:
            db_path: Path to SQLite database (optional)
        """
        self.db_path = db_path or "data/alerts.db"
        self._ensure_data_directory()
        self._initialize_database()
    
    def _ensure_data_directory(self):
        """Ensure the data directory exists."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _initialize_database(self):
        """Initialize SQLite database with alerts table."""
        try:
            conn = sqlite3.connect(self.db_path)
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
                    dismissed_at TEXT,
                    machine_id TEXT,
                    metric_value REAL
                )
            ''')
            
            # Create indices for faster queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_severity 
                ON alerts(severity)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_dismissed 
                ON alerts(is_dismissed)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_created_at 
                ON alerts(created_at)
            ''')
            
            conn.commit()
            conn.close()
            
            # Create sample alerts if database is empty
            self._create_sample_alerts_if_empty()
            
            logger.info(f"✓ Alert system initialized at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Error initializing alert database: {e}")
    
    def _create_sample_alerts_if_empty(self):
        """Create sample alerts if the database is empty."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM alerts WHERE is_dismissed = 0")
        count = cursor.fetchone()[0]
        
        if count == 0:
            logger.info("Creating sample alerts...")
            
            sample_alerts = [
                {
                    'title': 'High Defect Rate Detected',
                    'message': 'Machine M003 showing defect rate of 8.5%, exceeding threshold of 5%',
                    'severity': 'WARNING',
                    'source': 'Quality Control',
                    'machine_id': 'M003',
                    'metric_value': 8.5
                },
                {
                    'title': 'Predictive Maintenance Alert',
                    'message': 'Machine M005 RUL below 48 hours. Schedule immediate maintenance.',
                    'severity': 'CRITICAL',
                    'source': 'Predictive Maintenance',
                    'machine_id': 'M005',
                    'metric_value': 36.0
                },
                {
                    'title': 'Supplier Quality Issue',
                    'message': 'Supplier SUP-008 quality score dropped to 62%. Review recommended.',
                    'severity': 'WARNING',
                    'source': 'Supplier Management',
                    'machine_id': None,
                    'metric_value': 62.0
                },
                {
                    'title': 'OEE Below Target',
                    'message': 'Overall Equipment Effectiveness at 78.3%, below target of 85%',
                    'severity': 'INFO',
                    'source': 'KPI Monitoring',
                    'machine_id': None,
                    'metric_value': 78.3
                },
                {
                    'title': 'Visual Inspection Failure',
                    'message': 'Multiple defects detected in batch B-2024-0215. Quality score: 45/100',
                    'severity': 'ERROR',
                    'source': 'Vision System',
                    'machine_id': None,
                    'metric_value': 45.0
                }
            ]
            
            for alert_data in sample_alerts:
                self.create_alert(
                    title=alert_data['title'],
                    message=alert_data['message'],
                    severity=alert_data['severity'],
                    source=alert_data['source'],
                    machine_id=alert_data.get('machine_id'),
                    metric_value=alert_data.get('metric_value')
                )
            
            logger.info(f"✓ Created {len(sample_alerts)} sample alerts")
        
        conn.close()
    
    def create_alert(
        self,
        title: str,
        message: str,
        severity: str,
        source: str,
        machine_id: Optional[str] = None,
        metric_value: Optional[float] = None
    ) -> int:
        """
        Create a new alert.
        
        Args:
            title: Alert title
            message: Detailed alert message
            severity: Alert severity (INFO, WARNING, ERROR, CRITICAL)
            source: Source system/module that generated the alert
            machine_id: Optional machine identifier
            metric_value: Optional metric value that triggered alert
            
        Returns:
            Alert ID
        """
        if severity not in self.SEVERITY_LEVELS:
            logger.warning(f"Invalid severity '{severity}', defaulting to 'INFO'")
            severity = 'INFO'
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            created_at = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO alerts 
                (title, message, severity, source, created_at, machine_id, metric_value)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (title, message, severity, source, created_at, machine_id, metric_value))
            
            alert_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"✓ Alert created: {title} (ID: {alert_id}, Severity: {severity})")
            
            return alert_id
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            return -1
    
    def get_active_alerts(self, severity: Optional[str] = None) -> List[Dict]:
        """
        Get all active (non-dismissed) alerts.
        
        Args:
            severity: Optional filter by severity level
            
        Returns:
            List of alert dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if severity and severity in self.SEVERITY_LEVELS:
                cursor.execute('''
                    SELECT id, title, message, severity, source, created_at, 
                           machine_id, metric_value
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
                ''', (severity,))
            else:
                cursor.execute('''
                    SELECT id, title, message, severity, source, created_at, 
                           machine_id, metric_value
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
                ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            alerts = []
            for row in rows:
                alerts.append({
                    'id': row[0],
                    'title': row[1],
                    'message': row[2],
                    'severity': row[3],
                    'source': row[4],
                    'created_at': row[5],
                    'machine_id': row[6],
                    'metric_value': row[7]
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting active alerts: {e}")
            return []
    
    def get_alert(self, alert_id: int) -> Optional[Dict]:
        """
        Get a specific alert by ID.
        
        Args:
            alert_id: Alert ID
            
        Returns:
            Alert dictionary or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, title, message, severity, source, created_at, 
                       is_dismissed, dismissed_at, machine_id, metric_value
                FROM alerts
                WHERE id = ?
            ''', (alert_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'title': row[1],
                    'message': row[2],
                    'severity': row[3],
                    'source': row[4],
                    'created_at': row[5],
                    'is_dismissed': bool(row[6]),
                    'dismissed_at': row[7],
                    'machine_id': row[8],
                    'metric_value': row[9]
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting alert {alert_id}: {e}")
            return None
    
    def dismiss_alert(self, alert_id: int) -> bool:
        """
        Dismiss an alert.
        
        Args:
            alert_id: Alert ID to dismiss
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            dismissed_at = datetime.now().isoformat()
            
            cursor.execute('''
                UPDATE alerts
                SET is_dismissed = 1, dismissed_at = ?
                WHERE id = ?
            ''', (dismissed_at, alert_id))
            
            rows_affected = cursor.rowcount
            conn.commit()
            conn.close()
            
            if rows_affected > 0:
                logger.info(f"✓ Alert {alert_id} dismissed")
                return True
            else:
                logger.warning(f"Alert {alert_id} not found")
                return False
                
        except Exception as e:
            logger.error(f"Error dismissing alert {alert_id}: {e}")
            return False
    
    def get_alert_statistics(self) -> Dict:
        """
        Get alert statistics.
        
        Returns:
            Dictionary with alert counts by severity
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT severity, COUNT(*) as count
                FROM alerts
                WHERE is_dismissed = 0
                GROUP BY severity
            ''')
            
            rows = cursor.fetchall()
            
            # Get total alerts (including dismissed)
            cursor.execute('SELECT COUNT(*) FROM alerts')
            total_all = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM alerts WHERE is_dismissed = 0')
            total_active = cursor.fetchone()[0]
            
            conn.close()
            
            stats = {
                'total_active': total_active,
                'total_all_time': total_all,
                'by_severity': {}
            }
            
            for row in rows:
                stats['by_severity'][row[0]] = row[1]
            
            # Ensure all severity levels are present
            for severity in self.SEVERITY_LEVELS:
                if severity not in stats['by_severity']:
                    stats['by_severity'][severity] = 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting alert statistics: {e}")
            return {
                'total_active': 0,
                'total_all_time': 0,
                'by_severity': {s: 0 for s in self.SEVERITY_LEVELS}
            }
    
    def clear_old_alerts(self, days: int = 30) -> int:
        """
        Clear dismissed alerts older than specified days.
        
        Args:
            days: Number of days to retain dismissed alerts
            
        Returns:
            Number of alerts cleared
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM alerts
                WHERE is_dismissed = 1 
                AND dismissed_at < datetime('now', '-' || ? || ' days')
            ''', (days,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"✓ Cleared {deleted_count} old dismissed alerts")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error clearing old alerts: {e}")
            return 0
