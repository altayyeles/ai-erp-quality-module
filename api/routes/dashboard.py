"""
Dashboard Module API Routes
Endpoints for real-time KPI summaries and alerts
"""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/kpis")
async def get_kpis():
    """Get current KPI snapshot (OEE, FPY, DPMO, Cpk)."""
    try:
        from modules.reporting.kpi_engine import KPIEngine
        kpi = KPIEngine()
        result = kpi.get_snapshot()
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts")
async def get_alerts():
    """Get active alerts."""
    try:
        from modules.reporting.alert_system import AlertSystem
        alerts = AlertSystem()
        result = alerts.get_active_alerts()
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/alerts/{alert_id}")
async def dismiss_alert(alert_id: int):
    """Dismiss an active alert by ID."""
    try:
        from modules.reporting.alert_system import AlertSystem
        alerts = AlertSystem()
        alerts.dismiss_alert(alert_id)
        return {"status": "success", "message": f"Alert {alert_id} dismissed"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
