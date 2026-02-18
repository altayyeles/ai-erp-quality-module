"""
KPI Engine - Key Performance Indicator Calculation and Reporting
Manufacturing KPI calculation system for quality metrics

This module calculates and tracks manufacturing KPIs including OEE, FPY, DPMO, and Cpk.
"""

import logging
import sqlite3
from pathlib import Path
from typing import Dict, List
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)


class KPIEngine:
    """
    Manufacturing KPI calculation and reporting engine.
    
    Calculates key performance indicators:
    - OEE (Overall Equipment Effectiveness)
    - FPY (First Pass Yield)
    - DPMO (Defects Per Million Opportunities)
    - Cpk (Process Capability Index)
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize KPI Engine.
        
        Args:
            db_path: Path to SQLite database (optional)
        """
        self.db_path = db_path or "data/kpi_metrics.db"
        self._ensure_data_directory()
        self._initialize_database()
    
    def _ensure_data_directory(self):
        """Ensure the data directory exists."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _initialize_database(self):
        """Initialize SQLite database with KPI tables."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create KPI metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS kpi_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    machine_id TEXT,
                    oee REAL,
                    fpy REAL,
                    dpmo REAL,
                    cpk REAL,
                    availability REAL,
                    performance REAL,
                    quality REAL,
                    good_parts INTEGER,
                    total_parts INTEGER,
                    defects INTEGER,
                    opportunities INTEGER
                )
            ''')
            
            # Create index for faster queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON kpi_metrics(timestamp)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_machine_timestamp 
                ON kpi_metrics(machine_id, timestamp)
            ''')
            
            conn.commit()
            conn.close()
            
            # Populate with demo data if empty
            self._populate_demo_data_if_empty()
            
            logger.info(f"✓ KPI database initialized at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Error initializing KPI database: {e}")
    
    def _populate_demo_data_if_empty(self):
        """Populate database with demo data if it's empty."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM kpi_metrics")
        count = cursor.fetchone()[0]
        
        if count == 0:
            logger.info("Populating KPI database with demo data...")
            
            # Generate 90 days of historical data
            machines = ['M001', 'M002', 'M003', 'M004', 'M005', 'M006', 'M007', 'M008']
            end_date = datetime.now()
            
            for days_ago in range(90, 0, -1):
                timestamp = end_date - timedelta(days=days_ago)
                
                for machine in machines:
                    # Simulate realistic KPI values with trends
                    trend_factor = 1.0 + (90 - days_ago) * 0.001  # Slight improvement over time
                    
                    availability = random.uniform(0.85, 0.98) * trend_factor
                    performance = random.uniform(0.88, 0.97) * trend_factor
                    quality = random.uniform(0.92, 0.99) * trend_factor
                    
                    oee = availability * performance * quality
                    
                    total_parts = random.randint(800, 1200)
                    good_parts = int(total_parts * quality)
                    defects = total_parts - good_parts
                    
                    fpy = good_parts / total_parts if total_parts > 0 else 0
                    
                    opportunities = 6  # Assume 6 defect opportunities per part
                    dpmo = (defects / (total_parts * opportunities)) * 1_000_000 if total_parts > 0 else 0
                    
                    cpk = random.uniform(1.2, 1.8) * trend_factor
                    
                    cursor.execute('''
                        INSERT INTO kpi_metrics 
                        (timestamp, machine_id, oee, fpy, dpmo, cpk, 
                         availability, performance, quality, 
                         good_parts, total_parts, defects, opportunities)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        timestamp.isoformat(),
                        machine,
                        oee,
                        fpy,
                        dpmo,
                        cpk,
                        availability,
                        performance,
                        quality,
                        good_parts,
                        total_parts,
                        defects,
                        opportunities
                    ))
            
            conn.commit()
            logger.info(f"✓ Populated {90 * len(machines)} demo KPI records")
        
        conn.close()
    
    def get_snapshot(self) -> Dict:
        """
        Get current KPI snapshot (latest values).
        
        Returns:
            Dictionary with current KPI values
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get latest KPIs across all machines
            cursor.execute('''
                SELECT 
                    AVG(oee) as oee,
                    AVG(fpy) as fpy,
                    AVG(dpmo) as dpmo,
                    AVG(cpk) as cpk,
                    AVG(availability) as availability,
                    AVG(performance) as performance,
                    AVG(quality) as quality,
                    SUM(good_parts) as total_good,
                    SUM(total_parts) as total_produced,
                    SUM(defects) as total_defects
                FROM kpi_metrics
                WHERE timestamp >= datetime('now', '-1 day')
            ''')
            
            row = cursor.fetchone()
            conn.close()
            
            if row and row[0] is not None:
                return {
                    'oee': round(row[0] * 100, 2),
                    'fpy': round(row[1] * 100, 2),
                    'dpmo': round(row[2], 0),
                    'cpk': round(row[3], 2),
                    'oee_components': {
                        'availability': round(row[4] * 100, 2),
                        'performance': round(row[5] * 100, 2),
                        'quality': round(row[6] * 100, 2)
                    },
                    'production_summary': {
                        'good_parts': int(row[7] or 0),
                        'total_parts': int(row[8] or 0),
                        'defects': int(row[9] or 0),
                        'yield_rate': round((row[7] / row[8] * 100) if row[8] else 0, 2)
                    },
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # Return simulated data if no DB data
                return self._get_simulated_snapshot()
                
        except Exception as e:
            logger.error(f"Error getting KPI snapshot: {e}")
            return self._get_simulated_snapshot()
    
    def _get_simulated_snapshot(self) -> Dict:
        """Get simulated KPI snapshot."""
        availability = 0.93
        performance = 0.92
        quality = 0.97
        oee = availability * performance * quality
        
        return {
            'oee': round(oee * 100, 2),
            'fpy': 96.8,
            'dpmo': 32000,
            'cpk': 1.45,
            'oee_components': {
                'availability': round(availability * 100, 2),
                'performance': round(performance * 100, 2),
                'quality': round(quality * 100, 2)
            },
            'production_summary': {
                'good_parts': 9680,
                'total_parts': 10000,
                'defects': 320,
                'yield_rate': 96.8
            },
            'timestamp': datetime.now().isoformat(),
            'mode': 'simulated'
        }
    
    def get_trend(self, days: int = 30) -> Dict:
        """
        Get KPI trend data for the last N days.
        
        Args:
            days: Number of days to retrieve
            
        Returns:
            Dictionary with time-series KPI data
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    DATE(timestamp) as date,
                    AVG(oee) * 100 as oee,
                    AVG(fpy) * 100 as fpy,
                    AVG(dpmo) as dpmo,
                    AVG(cpk) as cpk
                FROM kpi_metrics
                WHERE timestamp >= datetime('now', '-' || ? || ' days')
                GROUP BY DATE(timestamp)
                ORDER BY date
            ''', (days,))
            
            rows = cursor.fetchall()
            conn.close()
            
            if rows:
                dates = [row[0] for row in rows]
                oee_values = [round(row[1], 2) for row in rows]
                fpy_values = [round(row[2], 2) for row in rows]
                dpmo_values = [round(row[3], 0) for row in rows]
                cpk_values = [round(row[4], 2) for row in rows]
                
                return {
                    'dates': dates,
                    'oee': oee_values,
                    'fpy': fpy_values,
                    'dpmo': dpmo_values,
                    'cpk': cpk_values,
                    'period_days': days
                }
            else:
                return self._get_simulated_trend(days)
                
        except Exception as e:
            logger.error(f"Error getting KPI trend: {e}")
            return self._get_simulated_trend(days)
    
    def _get_simulated_trend(self, days: int) -> Dict:
        """Generate simulated trend data."""
        dates = []
        oee_values = []
        fpy_values = []
        dpmo_values = []
        cpk_values = []
        
        end_date = datetime.now()
        
        for i in range(days):
            date = end_date - timedelta(days=days - i)
            dates.append(date.strftime('%Y-%m-%d'))
            
            # Simulate upward trend with noise
            trend = 1.0 + (i / days) * 0.1
            noise = random.uniform(-0.02, 0.02)
            
            oee_values.append(round((0.82 + 0.05 * trend + noise) * 100, 2))
            fpy_values.append(round((0.94 + 0.03 * trend + noise) * 100, 2))
            dpmo_values.append(round(40000 - 8000 * trend + random.randint(-2000, 2000), 0))
            cpk_values.append(round(1.3 + 0.15 * trend + noise, 2))
        
        return {
            'dates': dates,
            'oee': oee_values,
            'fpy': fpy_values,
            'dpmo': dpmo_values,
            'cpk': cpk_values,
            'period_days': days,
            'mode': 'simulated'
        }
    
    def get_by_machine(self, machine_id: str) -> Dict:
        """
        Get KPI data for a specific machine.
        
        Args:
            machine_id: Machine identifier (e.g., 'M001')
            
        Returns:
            Dictionary with machine-specific KPIs
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    AVG(oee) * 100 as oee,
                    AVG(fpy) * 100 as fpy,
                    AVG(dpmo) as dpmo,
                    AVG(cpk) as cpk,
                    SUM(good_parts) as total_good,
                    SUM(total_parts) as total_produced
                FROM kpi_metrics
                WHERE machine_id = ? AND timestamp >= datetime('now', '-7 days')
            ''', (machine_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row and row[0] is not None:
                return {
                    'machine_id': machine_id,
                    'oee': round(row[0], 2),
                    'fpy': round(row[1], 2),
                    'dpmo': round(row[2], 0),
                    'cpk': round(row[3], 2),
                    'good_parts': int(row[4] or 0),
                    'total_parts': int(row[5] or 0),
                    'period': 'Last 7 days'
                }
            else:
                return {
                    'machine_id': machine_id,
                    'oee': 85.0,
                    'fpy': 95.0,
                    'dpmo': 35000,
                    'cpk': 1.4,
                    'good_parts': 0,
                    'total_parts': 0,
                    'period': 'Last 7 days',
                    'mode': 'simulated'
                }
                
        except Exception as e:
            logger.error(f"Error getting machine KPIs: {e}")
            return {
                'machine_id': machine_id,
                'error': str(e),
                'mode': 'error'
            }
