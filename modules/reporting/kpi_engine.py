"""
KPI Engine for Quality Manufacturing Metrics
Calculates OEE, FPY, DPMO, Cpk and other key performance indicators
"""

import logging
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)


class KPIEngine:
    """
    KPI calculation and reporting engine.
    
    Calculates and tracks key manufacturing quality metrics:
    - OEE (Overall Equipment Effectiveness)
    - FPY (First Pass Yield)
    - DPMO (Defects Per Million Opportunities)
    - Cpk (Process Capability Index)
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize KPI Engine.
        
        Args:
            db_path: Path to SQLite database for metrics storage
        """
        self.db_path = db_path or Path("data/kpi_metrics.db")
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Create database and tables if they don't exist."""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Create metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS kpi_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    machine_id TEXT,
                    oee REAL,
                    availability REAL,
                    performance REAL,
                    quality REAL,
                    fpy REAL,
                    dpmo REAL,
                    cpk REAL,
                    total_units INTEGER,
                    defective_units INTEGER,
                    produced_units INTEGER,
                    planned_production_time REAL,
                    actual_production_time REAL,
                    downtime REAL
                )
            ''')
            
            conn.commit()
            conn.close()
            
            # Populate with initial demo data if empty
            self._populate_demo_data()
            
            logger.info(f"✓ KPI database initialized at {self.db_path}")
        
        except Exception as e:
            logger.error(f"Failed to initialize KPI database: {e}")
    
    def _populate_demo_data(self):
        """Populate database with demo data if it's empty."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Check if data exists
            cursor.execute("SELECT COUNT(*) FROM kpi_metrics")
            count = cursor.fetchone()[0]
            
            if count == 0:
                logger.info("Populating KPI database with demo data...")
                
                # Generate 30 days of demo data
                random.seed(42)
                base_date = datetime.now() - timedelta(days=30)
                
                for day in range(30):
                    for machine_id in ['M001', 'M002', 'M003', 'M004', 'M005', 'M006', 'M007', 'M008']:
                        timestamp = (base_date + timedelta(days=day)).isoformat()
                        
                        # Generate realistic KPI values with some variation
                        availability = random.uniform(0.85, 0.98)
                        performance = random.uniform(0.88, 0.96)
                        quality = random.uniform(0.92, 0.99)
                        oee = availability * performance * quality
                        
                        fpy = random.uniform(0.93, 0.99)
                        dpmo = random.randint(15000, 50000)
                        cpk = random.uniform(1.2, 1.8)
                        
                        total_units = random.randint(800, 1200)
                        defective_units = int(total_units * (1 - quality))
                        produced_units = total_units - defective_units
                        
                        planned_time = 480  # 8 hours in minutes
                        actual_time = planned_time * availability
                        downtime = planned_time - actual_time
                        
                        cursor.execute('''
                            INSERT INTO kpi_metrics (
                                timestamp, machine_id, oee, availability, performance, quality,
                                fpy, dpmo, cpk, total_units, defective_units, produced_units,
                                planned_production_time, actual_production_time, downtime
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            timestamp, machine_id, oee, availability, performance, quality,
                            fpy, dpmo, cpk, total_units, defective_units, produced_units,
                            planned_time, actual_time, downtime
                        ))
                
                conn.commit()
                logger.info("✓ Demo data populated successfully")
            
            conn.close()
        
        except Exception as e:
            logger.error(f"Failed to populate demo data: {e}")
    
    def get_snapshot(self, machine_id: Optional[str] = None) -> Dict:
        """
        Get current KPI snapshot.
        
        Args:
            machine_id: Optional machine ID to filter by
            
        Returns:
            Dictionary with current KPI values
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Get most recent metrics
            if machine_id:
                query = '''
                    SELECT AVG(oee), AVG(fpy), AVG(dpmo), AVG(cpk),
                           AVG(availability), AVG(performance), AVG(quality),
                           SUM(total_units), SUM(defective_units)
                    FROM kpi_metrics
                    WHERE machine_id = ?
                    AND timestamp >= datetime('now', '-1 day')
                '''
                cursor.execute(query, (machine_id,))
            else:
                query = '''
                    SELECT AVG(oee), AVG(fpy), AVG(dpmo), AVG(cpk),
                           AVG(availability), AVG(performance), AVG(quality),
                           SUM(total_units), SUM(defective_units)
                    FROM kpi_metrics
                    WHERE timestamp >= datetime('now', '-1 day')
                '''
                cursor.execute(query)
            
            row = cursor.fetchone()
            conn.close()
            
            if row and row[0] is not None:
                oee, fpy, dpmo, cpk, availability, performance, quality, total_units, defective_units = row
                
                return {
                    'oee': round(oee * 100, 1),
                    'fpy': round(fpy * 100, 1),
                    'dpmo': int(dpmo),
                    'cpk': round(cpk, 2),
                    'availability': round(availability * 100, 1),
                    'performance': round(performance * 100, 1),
                    'quality': round(quality * 100, 1),
                    'total_units': int(total_units) if total_units else 0,
                    'defective_units': int(defective_units) if defective_units else 0,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # Return demo values if no data
                return self._get_demo_snapshot()
        
        except Exception as e:
            logger.error(f"Failed to get KPI snapshot: {e}")
            return self._get_demo_snapshot()
    
    def _get_demo_snapshot(self) -> Dict:
        """Return demo KPI snapshot."""
        return {
            'oee': 87.3,
            'fpy': 96.8,
            'dpmo': 32000,
            'cpk': 1.45,
            'availability': 94.5,
            'performance': 92.1,
            'quality': 97.8,
            'total_units': 8450,
            'defective_units': 186,
            'timestamp': datetime.now().isoformat(),
            'note': 'Demo data'
        }
    
    def get_trend(self, days: int = 30, machine_id: Optional[str] = None) -> List[Dict]:
        """
        Get KPI trend data.
        
        Args:
            days: Number of days of historical data
            machine_id: Optional machine ID to filter by
            
        Returns:
            List of daily KPI snapshots
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            if machine_id:
                query = '''
                    SELECT DATE(timestamp) as date,
                           AVG(oee), AVG(fpy), AVG(dpmo), AVG(cpk),
                           SUM(total_units), SUM(defective_units)
                    FROM kpi_metrics
                    WHERE machine_id = ?
                    AND timestamp >= datetime('now', '-' || ? || ' days')
                    GROUP BY DATE(timestamp)
                    ORDER BY date
                '''
                cursor.execute(query, (machine_id, days))
            else:
                query = '''
                    SELECT DATE(timestamp) as date,
                           AVG(oee), AVG(fpy), AVG(dpmo), AVG(cpk),
                           SUM(total_units), SUM(defective_units)
                    FROM kpi_metrics
                    WHERE timestamp >= datetime('now', '-' || ? || ' days')
                    GROUP BY DATE(timestamp)
                    ORDER BY date
                '''
                cursor.execute(query, (days,))
            
            rows = cursor.fetchall()
            conn.close()
            
            trend_data = []
            for row in rows:
                date, oee, fpy, dpmo, cpk, total_units, defective_units = row
                trend_data.append({
                    'date': date,
                    'oee': round(oee * 100, 1) if oee else 0,
                    'fpy': round(fpy * 100, 1) if fpy else 0,
                    'dpmo': int(dpmo) if dpmo else 0,
                    'cpk': round(cpk, 2) if cpk else 0,
                    'total_units': int(total_units) if total_units else 0,
                    'defective_units': int(defective_units) if defective_units else 0
                })
            
            return trend_data
        
        except Exception as e:
            logger.error(f"Failed to get KPI trend: {e}")
            return []
    
    def get_by_machine(self, machine_id: str) -> Dict:
        """
        Get KPI metrics for a specific machine.
        
        Args:
            machine_id: Machine identifier
            
        Returns:
            Dictionary with machine-specific KPI metrics
        """
        return self.get_snapshot(machine_id=machine_id)
